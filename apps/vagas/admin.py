from django.contrib import admin

from apps.vagas.models import HistoricoStatusVaga, Vaga


class HistoricoStatusVagaInline(admin.TabularInline):
    model = HistoricoStatusVaga
    extra = 0
    can_delete = False
    readonly_fields = (
        "tipo_status",
        "de_status",
        "para_status",
        "alterado_por",
        "observacao",
        "created_at",
    )


@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin):
    list_display = (
        "cargo",
        "area_solicitante",
        "tipo",
        "status",
        "status_aprovacao",
        "solicitante",
        "active",
    )
    list_filter = ("status", "status_aprovacao", "tipo", "active")
    search_fields = ("cargo", "area_solicitante")
    inlines = [HistoricoStatusVagaInline]
