from django.contrib import admin

from apps.candidatos.models import Candidato, PontuacaoCandidato


@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "email",
        "cidade",
        "cargo_pretendido",
        "senioridade",
        "curriculo_status",
        "active",
    )
    list_filter = ("senioridade", "curriculo_status", "active")
    search_fields = ("nome", "email", "cidade", "cargo_pretendido")
    exclude = ("password",)
    readonly_fields = ("curriculo_bucket", "curriculo_key", "curriculo_status", "curriculo_erro")


@admin.register(PontuacaoCandidato)
class PontuacaoCandidatoAdmin(admin.ModelAdmin):
    list_display = ("candidato", "funcao", "pontuacao", "origem", "avaliador", "created_at")
    list_filter = ("origem", "funcao")
    search_fields = ("candidato__nome", "candidato__email", "funcao")
