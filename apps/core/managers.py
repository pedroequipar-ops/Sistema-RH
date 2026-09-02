from django.db import models


class ActiveObjects(models.Manager):
    """Default manager: only rows with active=True (soft-delete aware)."""

    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class AllObjects(models.Manager):
    """Unfiltered manager: includes soft-deleted (active=False) rows."""

    def get_queryset(self):
        return super().get_queryset()
