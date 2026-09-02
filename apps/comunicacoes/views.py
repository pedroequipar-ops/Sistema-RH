from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.comunicacoes.models import EmailEnviado, Notificacao
from apps.comunicacoes.serializers import EmailEnviadoSerializer, NotificacaoSerializer
from apps.core.models import User
from apps.core.permissions import HasFunctionPermission
from utils.utils import capture_company_id


class EmailEnviadoViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Histórico de e-mails enviados (F4). RH/Gestor, RBAC via
    HasFunctionPermission — Gestor só vê e-mail de candidato com processo
    em vaga da própria área, mesma regra do banco de talentos."""

    serializer_class = EmailEnviadoSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "comunicacoes"
    permission_action_map = {"list": "view", "retrieve": "view"}
    filterset_fields = ["candidato", "tipo", "status"]

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        queryset = EmailEnviado.objects.filter(company_id=company_id)
        user = self.request.user
        if user.role == User.Role.GESTOR:
            queryset = queryset.filter(
                candidato__processos__vaga__area_solicitante=user.area
            ).distinct()
        return queryset


class NotificacaoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Notificações internas (F4) — sempre restritas ao próprio destinatário,
    independente de role: RBAC (permission_path='comunicacoes') controla se
    o usuário acessa o recurso; o get_queryset garante que ninguém lê a
    caixa de notificação de outra pessoa, nem RH."""

    serializer_class = NotificacaoSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "comunicacoes"
    permission_action_map = {"list": "view", "retrieve": "view", "marcar_lida": "view"}
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
