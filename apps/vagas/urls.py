from rest_framework.routers import DefaultRouter

from apps.vagas.views import VagaViewSet

router = DefaultRouter()
router.register("vagas", VagaViewSet, basename="vaga")

urlpatterns = router.urls
