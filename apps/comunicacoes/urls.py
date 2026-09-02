from rest_framework.routers import DefaultRouter

from apps.comunicacoes.views import EmailEnviadoViewSet, NotificacaoViewSet

router = DefaultRouter()
router.register("emails-enviados", EmailEnviadoViewSet, basename="email-enviado")
router.register("notificacoes", NotificacaoViewSet, basename="notificacao")

urlpatterns = router.urls
