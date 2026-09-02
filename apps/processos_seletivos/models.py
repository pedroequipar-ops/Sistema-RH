from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class ProcessoSeletivo(TimeStampedModel):
    """Vínculo candidato -> vaga -> etapa atual do funil de seleção.

    Modelo mínimo criado já na Etapa B2 porque a candidatura pública
    (apps.candidatos) depende dele para registrar a entrada do candidato no
    funil. A Etapa B3 constrói em cima deste model: histórico de etapa,
    avaliações/notas, testes/formulários e agendamento de entrevista (.ics).
    """

    class Etapa(models.TextChoices):
        TRIAGEM = "triagem", "Triagem"
        TESTE = "teste", "Teste"
        ENTREVISTA = "entrevista", "Entrevista"
        PROPOSTA = "proposta", "Proposta"
        CONTRATADO = "contratado", "Contratado"
        REPROVADO = "reprovado", "Reprovado"

    candidato = models.ForeignKey(
        "candidatos.Candidato", related_name="processos", on_delete=models.CASCADE
    )
    vaga = models.ForeignKey("vagas.Vaga", related_name="processos", on_delete=models.CASCADE)
    etapa_atual = models.CharField(max_length=15, choices=Etapa.choices, default=Etapa.TRIAGEM)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["candidato", "vaga"], name="unique_candidato_vaga")
        ]

    def __str__(self):
        return f"{self.candidato_id} -> {self.vaga_id} ({self.etapa_atual})"


class HistoricoEtapaProcesso(TimeStampedModel):
    """Auditoria de toda movimentação de etapa do kanban."""

    processo = models.ForeignKey(
        ProcessoSeletivo, related_name="historico_etapas", on_delete=models.CASCADE
    )
    de_etapa = models.CharField(max_length=15, blank=True)
    para_etapa = models.CharField(max_length=15)
    alterado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.processo_id}: {self.de_etapa} -> {self.para_etapa}"


class AvaliacaoProcesso(TimeStampedModel):
    """Anotação/avaliação de um candidato num processo — notas do RH ou do
    gestor. Imutável por design (sem update/destroy expostos): é um registro
    de auditoria de opinião, não um dado editável.
    """

    processo = models.ForeignKey(
        ProcessoSeletivo, related_name="avaliacoes", on_delete=models.CASCADE
    )
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    nota = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    comentario = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.processo_id}: nota {self.nota} por {self.autor_id}"


class TesteAplicado(TimeStampedModel):
    """Teste/formulário (comportamental ou técnico) associado ao processo.
    Quem registra respostas e nota é o RH/Gestor (ex: aplicado por telefone,
    presencialmente ou por um serviço externo de assessment) — não há
    autoatendimento do candidato nesta versão.
    """

    class Tipo(models.TextChoices):
        COMPORTAMENTAL = "comportamental", "Comportamental"
        TECNICO = "tecnico", "Técnico"

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        RESPONDIDO = "respondido", "Respondido"
        AVALIADO = "avaliado", "Avaliado"

    processo = models.ForeignKey(ProcessoSeletivo, related_name="testes", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=15, choices=Tipo.choices)
    titulo = models.CharField(max_length=150)
    perguntas = models.JSONField(default=list, blank=True)
    respostas = models.JSONField(default=dict, blank=True)
    nota = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDENTE)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.titulo} ({self.processo_id})"


class EntrevistaAgendamento(TimeStampedModel):
    """Agendamento de entrevista. Ao criar, gera um .ics (regra arquitetural
    13) anexado ao e-mail de convite disparado via mail_queue.
    """

    processo = models.ForeignKey(
        ProcessoSeletivo, related_name="entrevistas", on_delete=models.CASCADE
    )
    data_hora = models.DateTimeField()
    duracao_minutos = models.PositiveIntegerField(default=60)
    local_ou_link = models.CharField(max_length=255, blank=True)
    observacoes = models.TextField(blank=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        ordering = ["-data_hora"]

    def __str__(self):
        return f"Entrevista {self.processo_id} em {self.data_hora:%Y-%m-%d %H:%M}"
