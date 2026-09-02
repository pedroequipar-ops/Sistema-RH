from django.contrib import admin

from apps.comunicacoes.models import EmailEnviado, Notificacao


@admin.register(EmailEnviado)
class EmailEnviadoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "destinatario", "assunto", "status", "created_at")
    list_filter = ("tipo", "status")
    search_fields = ("destinatario", "assunto", "candidato__nome")


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ("destinatario", "tipo", "mensagem", "lida", "created_at")
    list_filter = ("tipo", "lida")
    search_fields = ("destinatario__email", "mensagem")
