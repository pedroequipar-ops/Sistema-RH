from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.candidatos.serializers import (
    CandidaturaPublicaSerializer,
    ProcessoSeletivoResumoSerializer,
    VagaPublicaSerializer,
)
from apps.vagas.models import Vaga
from utils.utils import capture_company_id


class VagasPublicasViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Página pública de vagas abertas — sem autenticação, só precisa do
    header X-Company-ID pra saber de qual empresa é a página de carreiras.
    """

    serializer_class = VagaPublicaSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    search_fields = ["cargo", "descricao"]

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        return Vaga.objects.filter(company_id=company_id, status=Vaga.Status.ABERTA)


class CandidaturaPublicaView(APIView):
    """Candidatura direta: cria/atualiza o Candidato e o vincula à vaga
    (ProcessoSeletivo, etapa 'triagem'). Endpoint público."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        company_id = capture_company_id(request)
        serializer = CandidaturaPublicaSerializer(
            data=request.data, context={"company_id": company_id}
        )
        serializer.is_valid(raise_exception=True)
        processo = serializer.save()
        return Response(
            ProcessoSeletivoResumoSerializer(processo).data, status=status.HTTP_201_CREATED
        )
