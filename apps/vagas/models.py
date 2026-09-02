from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Vaga(TimeStampedModel):
    class Tipo(models.TextChoices):
        INTERNA = "interna", "Interna"
        EXTERNA = "externa", "Externa"

    class StatusAprovacao(models.TextChoices):
        AGUARDANDO_RH = "aguardando_rh", "Aguardando aprovação do RH"
        AGUARDANDO_DIRETORIA = "aguardando_diretoria", "Aguardando aprovação da diretoria"
        APROVADA = "aprovada", "Aprovada"
        REPROVADA = "reprovada", "Reprovada"

    class Status(models.TextChoices):
        ABERTA = "aberta", "Aberta"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        PAUSADA = "pausada", "Pausada"
        FECHADA = "fechada", "Fechada"
        CANCELADA = "cancelada", "Cancelada"

    cargo = models.CharField(max_length=150)
    descricao = models.TextField()
    requisitos = models.TextField()
    salario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    area_solicitante = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.EXTERNA)
    status_aprovacao = models.CharField(
        max_length=25,
        choices=StatusAprovacao.choices,
        default=StatusAprovacao.AGUARDANDO_RH,
    )
    # Enquanto status_aprovacao não chega em APROVADA, a vaga fica PAUSADA
    # (não recebe candidatos). Vira ABERTA quando a diretoria aprova.
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PAUSADA)
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="vagas_solicitadas",
        on_delete=models.PROTECT,
    )
    custo_contratacao = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.cargo} ({self.area_solicitante})"


class HistoricoStatusVaga(TimeStampedModel):
    class TipoStatus(models.TextChoices):
        APROVACAO = "aprovacao", "Aprovação"
        OPERACIONAL = "operacional", "Operacional"

    vaga = models.ForeignKey(Vaga, related_name="historico_status", on_delete=models.CASCADE)
    tipo_status = models.CharField(max_length=15, choices=TipoStatus.choices)
    de_status = models.CharField(max_length=30, blank=True)
    para_status = models.CharField(max_length=30)
    alterado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.vaga_id}: {self.de_status} -> {self.para_status}"
