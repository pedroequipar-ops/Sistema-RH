from django.urls import path

from apps.core.views import MeView

urlpatterns = [
    path("auth/me/", MeView.as_view(), name="core-me"),
]
