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
