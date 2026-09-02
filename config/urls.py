from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth
    path("v1/auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("v1/auth/token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    # Docs — schema OpenAPI (drf-spectacular) renderizado via RapiDoc
    path("v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        TemplateView.as_view(
            template_name="docs/rapidoc.html",
            extra_context={"schema_url": "/v1/schema/"},
        ),
        name="docs",
    ),
    # Domain apps (populated etapa a etapa)
    path("v1/", include("apps.core.urls")),
    path("v1/", include("apps.vagas.urls")),
    path("v1/", include("apps.candidatos.urls")),
    path("v1/", include("apps.processos_seletivos.urls")),
    path("v1/", include("apps.comunicacoes.urls")),
    path("v1/", include("apps.relatorios.urls")),
    path("v1/", include("apps.admissao.urls")),
]
