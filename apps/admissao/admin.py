from django.contrib import admin

from apps.admissao.models import ChecklistItemAdmissao, Funcionario


class ChecklistItemAdmissaoInline(admin.TabularInline):
    model = ChecklistItemAdmissao
    extra = 0
    readonly_fields = ("nome_documento",)


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ("candidato", "cargo", "status_onboarding", "data_admissao", "active")
    list_filter = ("status_onboarding", "active")
    search_fields = ("candidato__nome", "candidato__email", "cargo")
    inlines = [ChecklistItemAdmissaoInline]


@admin.register(ChecklistItemAdmissao)
class ChecklistItemAdmissaoAdmin(admin.ModelAdmin):
    list_display = ("funcionario", "nome_documento", "status", "obrigatorio")
    list_filter = ("status", "obrigatorio")
