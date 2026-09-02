from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel

DOCUMENTOS_PADRAO_ADMISSAO = [
    "RG",
    "CPF",
    "Comprovante de residência",
    "Dados bancários",
    "Carteira de trabalho (CTPS)",
]


class Funcionario(TimeStampedModel):
    """Histórico do funcionário após contratado — vínculo com o processo
    seletivo de origem. Criado automaticamente quando um ProcessoSeletivo
    chega na etapa 'contratado' (ver apps.admissao.services e o hook em
    apps.processos_seletivos.views.ProcessoSeletivoViewSet.mover_etapa).
    """

    class StatusOnboarding(models.TextChoices):
        DOCUMENTOS_PENDENTES = "documentos_pendentes", "Documentos pendentes"
        EM_ANALISE = "em_analise", "Em análise"
        CONCLUIDO = "concluido", "Concluído"

    processo = models.OneToOneField(
        "processos_seletivos.ProcessoSeletivo", related_name="funcionario", on_delete=models.PROTECT
    )
    candidato = models.ForeignKey(
        "candidatos.Candidato", related_name="admissoes", on_delete=models.PROTECT
    )
    vaga = models.ForeignKey("vagas.Vaga", related_name="admissoes", on_delete=models.PROTECT)
    cargo = models.CharField(max_length=150, blank=True)
    data_admissao = models.DateField(null=True, blank=True)
    status_onboarding = models.CharField(
        max_length=25,
        choices=StatusOnboarding.choices,
        default=StatusOnboarding.DOCUMENTOS_PENDENTES,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.candidato_id} ({self.status_onboarding})"


class ChecklistItemAdmissao(TimeStampedModel):
    """Item do checklist de documentos de admissão — o candidato envia o
    arquivo pelo portal, o RH revisa (aprova/rejeita)."""

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        ENVIADO = "enviado", "Enviado"
        APROVADO = "aprovado", "Aprovado"
        REJEITADO = "rejeitado", "Rejeitado"

    funcionario = models.ForeignKey(Funcionario, related_name="checklist", on_delete=models.CASCADE)
    nome_documento = models.CharField(max_length=150)
    obrigatorio = models.BooleanField(default=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDENTE)
    documento_bucket = models.CharField(max_length=100, blank=True)
    documento_key = models.CharField(max_length=255, blank=True)
    observacao = models.TextField(blank=True)
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["nome_documento"]

    def __str__(self):
        return f"{self.funcionario_id}: {self.nome_documento} ({self.status})"
