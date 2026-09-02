from django.db.models import Count, DurationField, ExpressionWrapper, F
from rest_framework import generics
from rest_framework.response import Response

from apps.core.models import User
from apps.core.permissions import HasFunctionPermission
from apps.processos_seletivos.models import HistoricoEtapaProcesso, ProcessoSeletivo
from apps.relatorios.serializers import (
    CandidatosPorVagaSerializer,
    CustoContratacaoSerializer,
    FunilEtapaSerializer,
    TempoMedioContratacaoSerializer,
)
from apps.vagas.models import Vaga
from utils.utils import capture_company_id

ETAPAS_FUNIL = [
    ProcessoSeletivo.Etapa.TRIAGEM,
    ProcessoSeletivo.Etapa.TESTE,
    ProcessoSeletivo.Etapa.ENTREVISTA,
    ProcessoSeletivo.Etapa.PROPOSTA,
    ProcessoSeletivo.Etapa.CONTRATADO,
]


def _queryset_processos(request):
    company_id = capture_company_id(request)
    queryset = ProcessoSeletivo.objects.filter(company_id=company_id)
    user = request.user
    if user.role == User.Role.GESTOR:
        queryset = queryset.filter(vaga__area_solicitante=user.area)
    return queryset


def _queryset_vagas(request):
    company_id = capture_company_id(request)
    queryset = Vaga.objects.filter(company_id=company_id)
    user = request.user
    if user.role == User.Role.GESTOR:
        queryset = queryset.filter(area_solicitante=user.area)
    return queryset


class RelatorioBaseView(generics.GenericAPIView):
    """Todo relatório é só leitura (agregação sobre dados de outros apps,
    sem model próprio) — mesmo assim declara RBAC completo (regra 5).
    `action` é fixado na classe porque GenericAPIView não populariza esse
    atributo sozinho como um ViewSet faria."""

    permission_classes = [HasFunctionPermission]
    permission_path = "relatorios"
    permission_action_map = {"list": "view"}
    action = "list"


class TempoMedioContratacaoView(RelatorioBaseView):
    serializer_class = TempoMedioContratacaoSerializer

    def get(self, request):
        processos = _queryset_processos(request).filter(
            etapa_atual=ProcessoSeletivo.Etapa.CONTRATADO
        )
        vaga_id = request.query_params.get("vaga")
        if vaga_id:
            processos = processos.filter(vaga_id=vaga_id)

        duracoes = list(
            HistoricoEtapaProcesso.objects.filter(
                processo__in=processos, para_etapa=ProcessoSeletivo.Etapa.CONTRATADO
            )
            .annotate(
                duracao=ExpressionWrapper(
                    F("created_at") - F("processo__created_at"), output_field=DurationField()
                )
            )
            .values_list("duracao", flat=True)
        )

        media_dias = None
        if duracoes:
            media_segundos = sum(d.total_seconds() for d in duracoes) / len(duracoes)
            media_dias = round(media_segundos / 86400, 1)

        dados = {"tempo_medio_dias": media_dias, "total_contratacoes": len(duracoes)}
        return Response(self.get_serializer(dados).data)


class CandidatosPorVagaView(RelatorioBaseView):
    serializer_class = CandidatosPorVagaSerializer

    def get(self, request):
        processos = _queryset_processos(request)
        dados = (
            processos.values("vaga_id", "vaga__cargo")
            .annotate(total_candidatos=Count("id"))
            .order_by("-total_candidatos")
        )
        resultado = [
            {
                "vaga_id": item["vaga_id"],
                "vaga_cargo": item["vaga__cargo"],
                "total_candidatos": item["total_candidatos"],
            }
            for item in dados
        ]
        return Response(self.get_serializer(resultado, many=True).data)


class FunilConversaoView(RelatorioBaseView):
    """Taxa de conversão por etapa: de quem ENTROU numa etapa, quantos %
    AVANÇARAM pra próxima (em vez de ficar parado ou ser reprovado)."""

    serializer_class = FunilEtapaSerializer

    def get(self, request):
        processos = _queryset_processos(request)

        entraram = {}
        for etapa in ETAPAS_FUNIL:
            entraram[etapa] = (
                HistoricoEtapaProcesso.objects.filter(processo__in=processos, para_etapa=etapa)
                .values("processo")
                .distinct()
                .count()
            )

        avancaram = {}
        for etapa_atual, proxima_etapa in zip(ETAPAS_FUNIL, ETAPAS_FUNIL[1:]):
            avancaram[etapa_atual] = (
                HistoricoEtapaProcesso.objects.filter(
                    processo__in=processos, de_etapa=etapa_atual, para_etapa=proxima_etapa
                )
                .values("processo")
                .distinct()
                .count()
            )

        resultado = []
        for etapa in ETAPAS_FUNIL:
            qtd_entrou = entraram[etapa]
            qtd_avancou = avancaram.get(etapa)
            taxa = None
            if qtd_avancou is not None and qtd_entrou:
                taxa = round(qtd_avancou / qtd_entrou * 100, 2)
            resultado.append(
                {
                    "etapa": etapa,
                    "entraram": qtd_entrou,
                    "avancaram": qtd_avancou,
                    "taxa_conversao": taxa,
                }
            )
        return Response(self.get_serializer(resultado, many=True).data)


class CustoContratacaoView(RelatorioBaseView):
    serializer_class = CustoContratacaoSerializer

    def get(self, request):
        vagas = _queryset_vagas(request).filter(
            status=Vaga.Status.FECHADA, custo_contratacao__isnull=False
        )
        vagas_lista = [
            {"vaga_id": vaga.id, "cargo": vaga.cargo, "custo_contratacao": vaga.custo_contratacao}
            for vaga in vagas
        ]
        custos = [vaga.custo_contratacao for vaga in vagas]
        custo_medio = (sum(custos) / len(custos)) if custos else None
        custo_total = sum(custos) if custos else 0

        dados = {"vagas": vagas_lista, "custo_medio": custo_medio, "custo_total": custo_total}
        return Response(self.get_serializer(dados).data)
