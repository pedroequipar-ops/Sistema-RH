from rest_framework.routers import DefaultRouter

from apps.processos_seletivos.views import (
    AvaliacaoProcessoViewSet,
    EntrevistaAgendamentoViewSet,
    ProcessoSeletivoViewSet,
    TesteAplicadoViewSet,
)

router = DefaultRouter()
router.register("processos-seletivos", ProcessoSeletivoViewSet, basename="processo-seletivo")
router.register("avaliacoes-processo", AvaliacaoProcessoViewSet, basename="avaliacao-processo")
router.register("testes-processo", TesteAplicadoViewSet, basename="teste-processo")
router.register("entrevistas", EntrevistaAgendamentoViewSet, basename="entrevista")

urlpatterns = router.urls
