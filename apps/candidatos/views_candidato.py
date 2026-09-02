from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.candidatos.auth import (
    CandidatoJWTAuthentication,
    CandidatoTokenObtainSerializer,
    emitir_tokens_candidato,
)
from apps.candidatos.permissions import IsCandidato
from apps.candidatos.serializers import (
    CandidatoCadastroSerializer,
    CandidatoMeSerializer,
    ProcessoSeletivoResumoSerializer,
)
from apps.candidatos.services import processar_upload_curriculo
from apps.processos_seletivos.models import ProcessoSeletivo
from utils.utils import capture_company_id


class CandidatoCadastroView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        company_id = capture_company_id(request)
        serializer = CandidatoCadastroSerializer(
            data=request.data, context={"company_id": company_id}
        )
        serializer.is_valid(raise_exception=True)
        candidato = serializer.save()
        return Response(emitir_tokens_candidato(candidato), status=status.HTTP_201_CREATED)


class CandidatoTokenObtainView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        company_id = capture_company_id(request)
        serializer = CandidatoTokenObtainSerializer(
            data=request.data, context={"company_id": company_id}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CandidatoMeView(generics.RetrieveUpdateAPIView):
    serializer_class = CandidatoMeSerializer
    authentication_classes = [CandidatoJWTAuthentication]
    permission_classes = [IsCandidato]

    def get_object(self):
        return self.request.user


class CandidatoMeCurriculoView(APIView):
    authentication_classes = [CandidatoJWTAuthentication]
    permission_classes = [IsCandidato]
    parser_classes = [MultiPartParser]

    def post(self, request):
        arquivo = request.FILES.get("curriculo")
        if not arquivo:
            raise ValidationError({"curriculo": "Arquivo obrigatório."})
        processar_upload_curriculo(request.user, arquivo)
        return Response(CandidatoMeSerializer(request.user).data, status=status.HTTP_202_ACCEPTED)


class MinhasCandidaturasView(generics.ListAPIView):
    serializer_class = ProcessoSeletivoResumoSerializer
    authentication_classes = [CandidatoJWTAuthentication]
    permission_classes = [IsCandidato]

    def get_queryset(self):
        return ProcessoSeletivo.objects.filter(candidato=self.request.user).select_related("vaga")
