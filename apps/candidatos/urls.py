from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.candidatos.views import CandidatoViewSet, PontuacaoCandidatoViewSet
from apps.candidatos.views_candidato import (
    CandidatoCadastroView,
    CandidatoMeCurriculoView,
    CandidatoMeView,
    CandidatoTokenObtainView,
    MinhasCandidaturasView,
)
from apps.candidatos.views_publico import CandidaturaPublicaView, VagasPublicasViewSet

router = DefaultRouter()
router.register("candidatos", CandidatoViewSet, basename="candidato")
router.register("pontuacoes-candidato", PontuacaoCandidatoViewSet, basename="pontuacao-candidato")
router.register("vagas-publicas", VagasPublicasViewSet, basename="vaga-publica")

urlpatterns = [
    path("candidatos/cadastro/", CandidatoCadastroView.as_view(), name="candidato-cadastro"),
    path(
        "candidatos/auth/token/", CandidatoTokenObtainView.as_view(), name="candidato-token-obtain"
    ),
    path("candidatos/me/", CandidatoMeView.as_view(), name="candidato-me"),
    path(
        "candidatos/me/curriculo/",
        CandidatoMeCurriculoView.as_view(),
        name="candidato-me-curriculo",
    ),
    path(
        "candidatos/me/candidaturas/",
        MinhasCandidaturasView.as_view(),
        name="candidato-minhas-candidaturas",
    ),
    path("candidaturas/", CandidaturaPublicaView.as_view(), name="candidatura-publica"),
] + router.urls
