from django.contrib import admin

from apps.processos_seletivos.models import (
    AvaliacaoProcesso,
    EntrevistaAgendamento,
    HistoricoEtapaProcesso,
    ProcessoSeletivo,
    TesteAplicado,
)


class HistoricoEtapaProcessoInline(admin.TabularInline):
    model = HistoricoEtapaProcesso
    extra = 0
    can_delete = False
    readonly_fields = ("de_etapa", "para_etapa", "alterado_por", "observacao", "created_at")


@admin.register(ProcessoSeletivo)
class ProcessoSeletivoAdmin(admin.ModelAdmin):
    list_display = ("candidato", "vaga", "etapa_atual", "active")
    list_filter = ("etapa_atual", "active")
    search_fields = ("candidato__nome", "candidato__email", "vaga__cargo")
    inlines = [HistoricoEtapaProcessoInline]


@admin.register(AvaliacaoProcesso)
class AvaliacaoProcessoAdmin(admin.ModelAdmin):
    list_display = ("processo", "autor", "nota", "created_at")
    search_fields = ("processo__candidato__nome",)


@admin.register(TesteAplicado)
class TesteAplicadoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "processo", "tipo", "status", "nota")
    list_filter = ("tipo", "status")


@admin.register(EntrevistaAgendamento)
class EntrevistaAgendamentoAdmin(admin.ModelAdmin):
    list_display = ("processo", "data_hora", "duracao_minutos", "local_ou_link", "active")
    list_filter = ("active",)
