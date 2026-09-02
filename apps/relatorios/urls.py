from django.urls import path

from apps.relatorios.views import (
    CandidatosPorVagaView,
    CustoContratacaoView,
    FunilConversaoView,
    TempoMedioContratacaoView,
)

urlpatterns = [
    path(
        "relatorios/tempo-medio-contratacao/",
        TempoMedioContratacaoView.as_view(),
        name="relatorio-tempo-medio-contratacao",
    ),
    path(
        "relatorios/candidatos-por-vaga/",
        CandidatosPorVagaView.as_view(),
        name="relatorio-candidatos-por-vaga",
    ),
    path(
        "relatorios/funil-conversao/",
        FunilConversaoView.as_view(),
        name="relatorio-funil-conversao",
    ),
    path(
        "relatorios/custo-contratacao/",
        CustoContratacaoView.as_view(),
        name="relatorio-custo-contratacao",
    ),
]
