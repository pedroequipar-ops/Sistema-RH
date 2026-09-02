from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class EmailEnviado(TimeStampedModel):
    """Histórico de e-mail disparado via mail_queue — quem lê é o RH/Gestor
    (F4: 'histórico de e-mails enviados por candidato').
    """

    class Status(models.TextChoices):
        ENVIADO = "enviado", "Enviado"
        FALHA = "falha", "Falha"

    tipo = models.CharField(max_length=50)
    destinatario = models.EmailField()
    assunto = models.CharField(max_length=255)
    candidato = models.ForeignKey(
        "candidatos.Candidato",
        null=True,
        blank=True,
        related_name="emails_enviados",
        on_delete=models.SET_NULL,
    )
    processo = models.ForeignKey(
        "processos_seletivos.ProcessoSeletivo",
        null=True,
        blank=True,
        related_name="emails_enviados",
        on_delete=models.SET_NULL,
    )
    status = models.CharField(max_length=10, choices=Status.choices)
    erro = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tipo} -> {self.destinatario} ({self.status})"


class Notificacao(TimeStampedModel):
    """Notificação interna via fila notifications — visível só pro próprio
    destinatário (F4: 'visualização de notificações internas')."""

    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="notificacoes", on_delete=models.CASCADE
    )
    tipo = models.CharField(max_length=50)
    mensagem = models.CharField(max_length=255)
    lida = models.BooleanField(default=False)
    processo = models.ForeignKey(
        "processos_seletivos.ProcessoSeletivo",
        null=True,
        blank=True,
        related_name="notificacoes",
        on_delete=models.SET_NULL,
    )
    dados = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.destinatario_id}: {self.mensagem}"
