from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from apps.candidatos.filters import CandidatoFilter
from apps.candidatos.models import Candidato
from apps.candidatos.serializers import CandidatoSerializer
from apps.candidatos.services import processar_upload_curriculo
from apps.core.models import User
from apps.core.permissions import HasFunctionPermission
from utils.utils import capture_company_id


class CandidatoViewSet(viewsets.ModelViewSet):
    """Banco de talentos — uso interno (RH/Gestor), RBAC via
    HasFunctionPermission. Não expõe cadastro/login de candidato (isso é
    público, ver apps.candidatos.views_publico/views_candidato).
    """

    serializer_class = CandidatoSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "candidatos"
    permission_action_map = {
        "list": "view",
        "retrieve": "view",
        "create": "create",
        "update": "edit",
        "partial_update": "edit",
        "destroy": "delete",
        "upload_curriculo": "edit",
    }
    filterset_class = CandidatoFilter
    search_fields = ["nome", "email", "cargo_pretendido", "cidade"]
    ordering_fields = ["created_at", "nome"]

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        queryset = Candidato.objects.filter(company_id=company_id)
        user = self.request.user
        if user.role == User.Role.GESTOR:
            queryset = queryset.filter(processos__vaga__area_solicitante=user.area).distinct()
        return queryset

    def perform_create(self, serializer):
        company_id = capture_company_id(self.request)
        serializer.save(company_id=company_id)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser])
    def upload_curriculo(self, request, pk=None):
        candidato = self.get_object()
        arquivo = request.FILES.get("curriculo")
        if not arquivo:
            raise ValidationError({"curriculo": "Arquivo obrigatório."})
        processar_upload_curriculo(candidato, arquivo)
        return Response(CandidatoSerializer(candidato).data, status=202)
