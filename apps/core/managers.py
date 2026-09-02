from django.db import models


class SoftDeleteQuerySet(models.QuerySet):
    """Bloqueia hard delete também em massa (Model.objects.filter(...).delete()),
    que não passa por TimeStampedModel.delete() (só bloqueia por instância).
    """

    def delete(self):
        raise NotImplementedError(
            "Hard delete em massa proibido. Atualize active=False registro a "
            "registro (ex: queryset.update(active=False)) ou use instance.soft_delete()."
        )


class ActiveObjects(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Default manager: only rows with active=True (soft-delete aware)."""

    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class AllObjects(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Unfiltered manager: includes soft-deleted (active=False) rows."""

    def get_queryset(self):
        return super().get_queryset()
