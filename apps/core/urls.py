from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.core.views import MeView, PerfilViewSet, UsuarioGerenciamentoViewSet

router = DefaultRouter()
router.register("usuarios", UsuarioGerenciamentoViewSet, basename="usuario")
router.register("perfis", PerfilViewSet, basename="perfil")

urlpatterns = [
    path("auth/me/", MeView.as_view(), name="core-me"),
] + router.urls
