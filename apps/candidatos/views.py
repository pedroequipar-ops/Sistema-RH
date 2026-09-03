from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from apps.candidatos.filters import CandidatoFilter
from apps.candidatos.models import Candidato, PontuacaoCandidato
from apps.candidatos.serializers import CandidatoSerializer, PontuacaoCandidatoSerializer
from apps.candidatos.services import processar_upload_curriculo
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
        return Candidato.objects.filter(company_id=company_id)

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


class PontuacaoCandidatoViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """Pontuação de candidato por função — lançada manualmente pelo RH/Gestor
    (origem=manual). Sem update/destroy: é registro de avaliação, imutável
    (mesmo padrão de AvaliacaoProcesso na B3). Quando um motor automático de
    pontuação for decidido (ver apps.candidatos.services.get_motor_pontuacao),
    ele passa a criar registros com origem=motor_automatico por um endpoint
    à parte — sem mudar este.
    """

    serializer_class = PontuacaoCandidatoSerializer
    permission_classes = [HasFunctionPermission]
    permission_path = "candidatos"
    permission_action_map = {"list": "view", "create": "edit"}
    filterset_fields = ["candidato", "funcao", "origem"]

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        return PontuacaoCandidato.objects.filter(company_id=company_id)

    def perform_create(self, serializer):
        company_id = capture_company_id(self.request)
        serializer.save(
            company_id=company_id,
            origem=PontuacaoCandidato.Origem.MANUAL,
            avaliador=self.request.user,
        )
