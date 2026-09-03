from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.comunicacoes.models import EmailEnviado, Notificacao
from apps.comunicacoes.serializers import EmailEnviadoSerializer, NotificacaoSerializer
from apps.core.permissions import HasFunctionPermission
from utils.utils import capture_company_id


class EmailEnviadoViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Histórico de e-mails enviados (F4). RH/Gestor, RBAC via
    HasFunctionPermission."""

    serializer_class = EmailEnviadoSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "comunicacoes"
    permission_action_map = {"list": "view", "retrieve": "view"}
    filterset_fields = ["candidato", "tipo", "status"]

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        return EmailEnviado.objects.filter(company_id=company_id)


class NotificacaoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Notificações internas (F4) — sempre restritas ao próprio destinatário,
    independente de role: RBAC (permission_path='comunicacoes') controla se
    o usuário acessa o recurso; o get_queryset garante que ninguém lê a
    caixa de notificação de outra pessoa, nem RH."""

    serializer_class = NotificacaoSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "comunicacoes"
    permission_action_map = {
        "list": "view",
        "retrieve": "view",
        "marcar_lida": "view",
        "limpar_todas": "view",
    }
    filterset_fields = ["tipo", "lida"]

    def get_queryset(self):
        capture_company_id(self.request)
        return Notificacao.objects.filter(destinatario=self.request.user)

    @action(detail=True, methods=["post"])
    def marcar_lida(self, request, pk=None):
        notificacao = self.get_object()
        notificacao.lida = True
        notificacao.save(update_fields=["lida", "updated_at"])
        return Response(NotificacaoSerializer(notificacao).data)

    @action(detail=False, methods=["post"])
    def limpar_todas(self, request):
        """Soft-delete de todas as notificações do usuário — some da lista,
        mas continua no banco via all_objects (auditoria), como todo model
        que herda de TimeStampedModel."""
        limpas = self.get_queryset().update(active=False, updated_at=timezone.now())
        return Response({"limpas": limpas})
