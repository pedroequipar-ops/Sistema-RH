from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.admissao.filters import ChecklistItemAdmissaoFilter, FuncionarioFilter
from apps.admissao.models import ChecklistItemAdmissao, Funcionario
from apps.admissao.serializers import (
    ChecklistItemAdmissaoSerializer,
    FuncionarioSerializer,
    RevisarChecklistItemSerializer,
)
from apps.core.models import User
from apps.core.permissions import HasFunctionPermission
from utils.utils import capture_company_id


def _aplicar_escopo_gestor(queryset, user, caminho_vaga):
    if user.role == User.Role.GESTOR:
        return queryset.filter(**{f"{caminho_vaga}__area_solicitante": user.area})
    return queryset


class FuncionarioViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Histórico do funcionário + status do onboarding. Criado
    automaticamente quando o processo chega em 'contratado' — sem create
    exposto aqui (não é um cadastro manual, é consequência do funil)."""

    serializer_class = FuncionarioSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "admissao"
    permission_action_map = {
        "list": "view",
        "retrieve": "view",
        "update": "edit",
        "partial_update": "edit",
    }
    filterset_class = FuncionarioFilter

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        queryset = Funcionario.objects.filter(company_id=company_id)
        return _aplicar_escopo_gestor(queryset, self.request.user, "vaga")


class ChecklistItemAdmissaoViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Itens do checklist de documentos — o candidato envia o arquivo pelo
    portal (ver apps.candidatos.views_candidato), o RH revisa aqui."""

    serializer_class = ChecklistItemAdmissaoSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "admissao"
    permission_action_map = {"list": "view", "retrieve": "view", "revisar": "edit"}
    filterset_class = ChecklistItemAdmissaoFilter

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        queryset = ChecklistItemAdmissao.objects.filter(company_id=company_id)
        return _aplicar_escopo_gestor(queryset, self.request.user, "funcionario__vaga")

    @action(detail=True, methods=["post"])
    def revisar(self, request, pk=None):
        item = self.get_object()
        serializer = RevisarChecklistItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item.status = serializer.validated_data["status"]
        item.observacao = serializer.validated_data["observacao"]
        item.revisado_por = request.user
        item.save(update_fields=["status", "observacao", "revisado_por", "updated_at"])

        self._atualizar_status_onboarding(item.funcionario)
        return Response(ChecklistItemAdmissaoSerializer(item).data)

    def _atualizar_status_onboarding(self, funcionario):
        itens = funcionario.checklist.all()
        if all(item.status == ChecklistItemAdmissao.Status.APROVADO for item in itens):
            novo_status = Funcionario.StatusOnboarding.CONCLUIDO
        elif any(
            item.status
            in (ChecklistItemAdmissao.Status.ENVIADO, ChecklistItemAdmissao.Status.APROVADO)
            for item in itens
        ):
            novo_status = Funcionario.StatusOnboarding.EM_ANALISE
        else:
            novo_status = Funcionario.StatusOnboarding.DOCUMENTOS_PENDENTES

        if funcionario.status_onboarding != novo_status:
            funcionario.status_onboarding = novo_status
            funcionario.save(update_fields=["status_onboarding", "updated_at"])
