from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.admissao.services import criar_funcionario_para_processo
from apps.core.logger import logger
from apps.core.permissions import HasFunctionPermission
from apps.processos_seletivos.filters import ProcessoSeletivoFilter
from apps.processos_seletivos.models import (
    AvaliacaoProcesso,
    EntrevistaAgendamento,
    HistoricoEtapaProcesso,
    ProcessoSeletivo,
    TesteAplicado,
)
from apps.processos_seletivos.notificacoes import (
    publicar_entrevista_agendada,
    publicar_mudanca_etapa,
)
from apps.processos_seletivos.serializers import (
    AvaliacaoProcessoSerializer,
    AvaliarTesteSerializer,
    EntrevistaAgendamentoSerializer,
    MoverEtapaSerializer,
    ProcessoSeletivoSerializer,
    TesteAplicadoSerializer,
)
from apps.vagas.models import HistoricoStatusVaga, Vaga
from utils.utils import capture_company_id

# triagem -> teste -> entrevista -> proposta -> contratado, com "reprovado"
# alcançável de qualquer etapa em aberto. contratado/reprovado são finais.
TRANSICOES_PERMITIDAS = {
    ProcessoSeletivo.Etapa.TRIAGEM: {
        ProcessoSeletivo.Etapa.TESTE,
        ProcessoSeletivo.Etapa.REPROVADO,
    },
    ProcessoSeletivo.Etapa.TESTE: {
        ProcessoSeletivo.Etapa.ENTREVISTA,
        ProcessoSeletivo.Etapa.REPROVADO,
    },
    ProcessoSeletivo.Etapa.ENTREVISTA: {
        ProcessoSeletivo.Etapa.PROPOSTA,
        ProcessoSeletivo.Etapa.REPROVADO,
    },
    ProcessoSeletivo.Etapa.PROPOSTA: {
        ProcessoSeletivo.Etapa.CONTRATADO,
        ProcessoSeletivo.Etapa.REPROVADO,
    },
    ProcessoSeletivo.Etapa.CONTRATADO: set(),
    ProcessoSeletivo.Etapa.REPROVADO: set(),
}


class ProcessoSeletivoViewSet(viewsets.ModelViewSet):
    """Kanban do funil de seleção: candidato -> vaga -> etapa atual."""

    serializer_class = ProcessoSeletivoSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "processos-seletivos"
    permission_action_map = {
        "list": "view",
        "retrieve": "view",
        "create": "create",
        "update": "edit",
        "partial_update": "edit",
        "destroy": "delete",
        "mover_etapa": "edit",
    }
    filterset_class = ProcessoSeletivoFilter

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        return ProcessoSeletivo.objects.filter(company_id=company_id)

    def perform_create(self, serializer):
        company_id = capture_company_id(self.request)
        processo = serializer.save(company_id=company_id)
        HistoricoEtapaProcesso.objects.create(
            company_id=company_id,
            processo=processo,
            de_etapa="",
            para_etapa=processo.etapa_atual,
            alterado_por=self.request.user,
            observacao="Candidato incluído manualmente no funil.",
        )

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def mover_etapa(self, request, pk=None):
        processo = self.get_object()
        serializer = MoverEtapaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nova_etapa = serializer.validated_data["etapa"]
        observacao = serializer.validated_data["observacao"]

        permitidas = TRANSICOES_PERMITIDAS.get(processo.etapa_atual, set())
        if nova_etapa not in permitidas:
            raise ValidationError(
                f"Não é possível mover de '{processo.etapa_atual}' para '{nova_etapa}'."
            )

        etapa_anterior = processo.etapa_atual
        processo.etapa_atual = nova_etapa
        processo.save(update_fields=["etapa_atual", "updated_at"])
        HistoricoEtapaProcesso.objects.create(
            company_id=processo.company_id,
            processo=processo,
            de_etapa=etapa_anterior,
            para_etapa=nova_etapa,
            alterado_por=request.user,
            observacao=observacao,
        )

        self._ajustar_status_vaga(processo.vaga, nova_etapa, request.user)
        if nova_etapa == ProcessoSeletivo.Etapa.CONTRATADO:
            criar_funcionario_para_processo(processo)
        publicar_mudanca_etapa(processo, etapa_anterior)
        logger.info(
            "processo.mudou_etapa",
            processo_id=str(processo.id),
            de=etapa_anterior,
            para=nova_etapa,
        )

        return Response(ProcessoSeletivoSerializer(processo).data)

    def _ajustar_status_vaga(self, vaga, nova_etapa, user):
        """Regra combinada com a Etapa B1: EM_ANDAMENTO e FECHADA ficavam
        reservados pro funil de seleção mexer no ciclo de vida da vaga."""
        if nova_etapa == ProcessoSeletivo.Etapa.CONTRATADO and vaga.status != Vaga.Status.FECHADA:
            de_status = vaga.status
            vaga.status = Vaga.Status.FECHADA
            vaga.save(update_fields=["status", "updated_at"])
            HistoricoStatusVaga.objects.create(
                company_id=vaga.company_id,
                vaga=vaga,
                tipo_status=HistoricoStatusVaga.TipoStatus.OPERACIONAL,
                de_status=de_status,
                para_status=vaga.status,
                alterado_por=user,
                observacao="Vaga fechada: candidato contratado.",
            )
        elif (
            nova_etapa in (ProcessoSeletivo.Etapa.TESTE, ProcessoSeletivo.Etapa.ENTREVISTA)
            and vaga.status == Vaga.Status.ABERTA
        ):
            de_status = vaga.status
            vaga.status = Vaga.Status.EM_ANDAMENTO
            vaga.save(update_fields=["status", "updated_at"])
            HistoricoStatusVaga.objects.create(
                company_id=vaga.company_id,
                vaga=vaga,
                tipo_status=HistoricoStatusVaga.TipoStatus.OPERACIONAL,
                de_status=de_status,
                para_status=vaga.status,
                alterado_por=user,
                observacao="Vaga em andamento: candidato avançou no funil.",
            )


class AvaliacaoProcessoViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """Anotações/notas do RH e do gestor sobre um candidato num processo —
    sem update/destroy: é registro de auditoria, não dado editável."""

    serializer_class = AvaliacaoProcessoSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "processos-seletivos"
    permission_action_map = {"list": "view", "create": "edit"}
    filterset_fields = ["processo"]

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        return AvaliacaoProcesso.objects.filter(company_id=company_id)

    def perform_create(self, serializer):
        company_id = capture_company_id(self.request)
        serializer.save(company_id=company_id, autor=self.request.user)


class TesteAplicadoViewSet(viewsets.ModelViewSet):
    """Teste/formulário (comportamental ou técnico) associado ao processo —
    RH/Gestor registra perguntas, respostas e nota (ex: aplicado numa
    entrevista ou por um serviço externo de assessment)."""

    serializer_class = TesteAplicadoSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "processos-seletivos"
    permission_action_map = {
        "list": "view",
        "retrieve": "view",
        "create": "create",
        "update": "edit",
        "partial_update": "edit",
        "destroy": "delete",
        "avaliar": "edit",
    }
    filterset_fields = ["processo", "tipo", "status"]

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        return TesteAplicado.objects.filter(company_id=company_id)

    def perform_create(self, serializer):
        company_id = capture_company_id(self.request)
        serializer.save(company_id=company_id, criado_por=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def avaliar(self, request, pk=None):
        teste = self.get_object()
        serializer = AvaliarTesteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if "respostas" in serializer.validated_data:
            teste.respostas = serializer.validated_data["respostas"]
        if "nota" in serializer.validated_data:
            teste.nota = serializer.validated_data["nota"]
        teste.status = TesteAplicado.Status.AVALIADO
        teste.save(update_fields=["respostas", "nota", "status", "updated_at"])

        return Response(TesteAplicadoSerializer(teste).data)


class EntrevistaAgendamentoViewSet(viewsets.ModelViewSet):
    """Agendamento de entrevista — ao criar, gera o .ics e publica o convite
    via mail_queue (regra arquitetural 13)."""

    serializer_class = EntrevistaAgendamentoSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "processos-seletivos"
    permission_action_map = {
        "list": "view",
        "retrieve": "view",
        "create": "create",
        "update": "edit",
        "partial_update": "edit",
        "destroy": "delete",
    }
    filterset_fields = ["processo"]

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        return EntrevistaAgendamento.objects.filter(company_id=company_id)

    def perform_create(self, serializer):
        company_id = capture_company_id(self.request)
        entrevista = serializer.save(company_id=company_id, criado_por=self.request.user)
        publicar_entrevista_agendada(entrevista)
        logger.info("entrevista.agendada", entrevista_id=str(entrevista.id))

    def perform_destroy(self, instance):
        instance.soft_delete()
