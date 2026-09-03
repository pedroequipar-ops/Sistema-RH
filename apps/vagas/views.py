from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.core.logger import logger
from apps.core.models import User
from apps.core.permissions import HasFunctionPermission
from apps.vagas.filters import VagaFilter
from apps.vagas.models import HistoricoStatusVaga, Vaga
from apps.vagas.serializers import VagaSerializer
from utils.utils import capture_company_id


class VagaViewSet(viewsets.ModelViewSet):
    """CRUD de vagas + fluxo de aprovação gestor -> RH -> diretoria.

    `status_aprovacao` e `status` nunca são editáveis via PUT/PATCH — só
    mudam através das ações /aprovar/, /reprovar/, /pausar/ e /cancelar/,
    cada mudança fica registrada em HistoricoStatusVaga.
    """

    serializer_class = VagaSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "vagas"
    permission_action_map = {
        "list": "view",
        "retrieve": "view",
        "create": "create",
        "update": "edit",
        "partial_update": "edit",
        "destroy": "delete",
        "aprovar": "edit",
        "reprovar": "edit",
        "pausar": "edit",
        "cancelar": "edit",
    }
    filterset_class = VagaFilter
    search_fields = ["cargo", "descricao", "requisitos"]
    ordering_fields = ["created_at", "cargo", "salario"]

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        return Vaga.objects.filter(company_id=company_id)

    def perform_create(self, serializer):
        company_id = capture_company_id(self.request)
        user = self.request.user
        vaga = serializer.save(
            company_id=company_id,
            solicitante=user,
            area_solicitante=serializer.validated_data.get("area_solicitante", ""),
            status_aprovacao=Vaga.StatusAprovacao.AGUARDANDO_RH,
            status=Vaga.Status.PAUSADA,
        )
        self._registrar_historico(
            vaga,
            HistoricoStatusVaga.TipoStatus.APROVACAO,
            "",
            vaga.status_aprovacao,
            user,
            "Vaga criada, aguardando aprovação do RH.",
        )
        logger.info("vaga.criada", vaga_id=str(vaga.id), company_id=str(company_id))

    def perform_destroy(self, instance):
        instance.soft_delete()

    def _registrar_historico(self, vaga, tipo_status, de_status, para_status, user, observacao=""):
        HistoricoStatusVaga.objects.create(
            company_id=vaga.company_id,
            vaga=vaga,
            tipo_status=tipo_status,
            de_status=de_status,
            para_status=para_status,
            alterado_por=user,
            observacao=observacao,
        )

    def _checar_dono(self, vaga, user):
        if user.is_superuser or user.role in (User.Role.RH, User.Role.DIRETORIA):
            return
        if user.role == User.Role.GESTOR and vaga.solicitante_id == user.id:
            return
        raise PermissionDenied("Você só pode alterar vagas que você mesmo solicitou.")

    @action(detail=True, methods=["post"])
    def aprovar(self, request, pk=None):
        vaga = self.get_object()
        user = request.user
        observacao = request.data.get("observacao", "")

        if vaga.status_aprovacao == Vaga.StatusAprovacao.AGUARDANDO_RH:
            if not (user.is_superuser or user.role == User.Role.RH):
                raise PermissionDenied("Somente RH pode aprovar esta etapa.")
            de_status = vaga.status_aprovacao
            vaga.status_aprovacao = Vaga.StatusAprovacao.AGUARDANDO_DIRETORIA
            vaga.save(update_fields=["status_aprovacao", "updated_at"])
            self._registrar_historico(
                vaga,
                HistoricoStatusVaga.TipoStatus.APROVACAO,
                de_status,
                vaga.status_aprovacao,
                user,
                observacao,
            )
        elif vaga.status_aprovacao == Vaga.StatusAprovacao.AGUARDANDO_DIRETORIA:
            if not (user.is_superuser or user.role == User.Role.DIRETORIA):
                raise PermissionDenied("Somente a diretoria pode aprovar esta etapa.")
            de_status_aprovacao = vaga.status_aprovacao
            de_status_operacional = vaga.status
            vaga.status_aprovacao = Vaga.StatusAprovacao.APROVADA
            vaga.status = Vaga.Status.ABERTA
            vaga.save(update_fields=["status_aprovacao", "status", "updated_at"])
            self._registrar_historico(
                vaga,
                HistoricoStatusVaga.TipoStatus.APROVACAO,
                de_status_aprovacao,
                vaga.status_aprovacao,
                user,
                observacao,
            )
            self._registrar_historico(
                vaga,
                HistoricoStatusVaga.TipoStatus.OPERACIONAL,
                de_status_operacional,
                vaga.status,
                user,
                "Vaga aberta após aprovação da diretoria.",
            )
        else:
            raise ValidationError("Esta vaga não está aguardando aprovação.")

        logger.info(
            "vaga.aprovada_etapa", vaga_id=str(vaga.id), status_aprovacao=vaga.status_aprovacao
        )
        return Response(VagaSerializer(vaga).data)

    @action(detail=True, methods=["post"])
    def reprovar(self, request, pk=None):
        vaga = self.get_object()
        user = request.user
        observacao = request.data.get("observacao", "")

        if vaga.status_aprovacao not in (
            Vaga.StatusAprovacao.AGUARDANDO_RH,
            Vaga.StatusAprovacao.AGUARDANDO_DIRETORIA,
        ):
            raise ValidationError("Esta vaga não está aguardando aprovação.")
        if vaga.status_aprovacao == Vaga.StatusAprovacao.AGUARDANDO_RH and not (
            user.is_superuser or user.role == User.Role.RH
        ):
            raise PermissionDenied("Somente RH pode reprovar esta etapa.")
        if vaga.status_aprovacao == Vaga.StatusAprovacao.AGUARDANDO_DIRETORIA and not (
            user.is_superuser or user.role == User.Role.DIRETORIA
        ):
            raise PermissionDenied("Somente a diretoria pode reprovar esta etapa.")

        de_status = vaga.status_aprovacao
        vaga.status_aprovacao = Vaga.StatusAprovacao.REPROVADA
        vaga.status = Vaga.Status.CANCELADA
        vaga.save(update_fields=["status_aprovacao", "status", "updated_at"])
        self._registrar_historico(
            vaga,
            HistoricoStatusVaga.TipoStatus.APROVACAO,
            de_status,
            vaga.status_aprovacao,
            user,
            observacao,
        )
        logger.info("vaga.reprovada", vaga_id=str(vaga.id))
        return Response(VagaSerializer(vaga).data)

    @action(detail=True, methods=["post"])
    def pausar(self, request, pk=None):
        vaga = self.get_object()
        user = request.user
        self._checar_dono(vaga, user)
        if vaga.status not in (Vaga.Status.ABERTA, Vaga.Status.EM_ANDAMENTO):
            raise ValidationError("Só é possível pausar uma vaga aberta ou em andamento.")
        de_status = vaga.status
        vaga.status = Vaga.Status.PAUSADA
        vaga.save(update_fields=["status", "updated_at"])
        self._registrar_historico(
            vaga,
            HistoricoStatusVaga.TipoStatus.OPERACIONAL,
            de_status,
            vaga.status,
            user,
            request.data.get("observacao", ""),
        )
        return Response(VagaSerializer(vaga).data)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        vaga = self.get_object()
        user = request.user
        self._checar_dono(vaga, user)
        if vaga.status == Vaga.Status.CANCELADA:
            raise ValidationError("Vaga já está cancelada.")
        de_status = vaga.status
        vaga.status = Vaga.Status.CANCELADA
        vaga.save(update_fields=["status", "updated_at"])
        self._registrar_historico(
            vaga,
            HistoricoStatusVaga.TipoStatus.OPERACIONAL,
            de_status,
            vaga.status,
            user,
            request.data.get("observacao", ""),
        )
        return Response(VagaSerializer(vaga).data)
