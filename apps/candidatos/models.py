from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.core.models import TimeStampedModel


class Candidato(TimeStampedModel):
    """Candidato do banco de talentos. Tem autenticação própria (JWT com role
    'candidato', ver apps.candidatos.auth) — não usa core.User nem
    HasFunctionPermission, é restrito por ownership.
    """

    class Senioridade(models.TextChoices):
        JUNIOR = "junior", "Júnior"
        PLENO = "pleno", "Pleno"
        SENIOR = "senior", "Sênior"

    class StatusProcessamento(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        PROCESSANDO = "processando", "Processando"
        PROCESSADO = "processado", "Processado"
        FALHA = "falha", "Falha"

    email = models.EmailField()
    password = models.CharField(max_length=128, blank=True)

    nome = models.CharField(max_length=150, blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    cargo_pretendido = models.CharField(max_length=150, blank=True)
    senioridade = models.CharField(max_length=10, choices=Senioridade.choices, blank=True)
    skills = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    resumo_experiencia = models.TextField(blank=True)

    curriculo_bucket = models.CharField(max_length=100, blank=True)
    curriculo_key = models.CharField(max_length=255, blank=True)
    curriculo_status = models.CharField(
        max_length=15, choices=StatusProcessamento.choices, default=StatusProcessamento.PENDENTE
    )
    curriculo_erro = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["company_id", "email"], name="unique_candidato_email")
        ]

    def __str__(self):
        return f"{self.nome or self.email}"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return bool(self.password) and check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        return True


class PontuacaoCandidato(TimeStampedModel):
    """Pontuação do candidato por função/cargo — não uma nota única genérica
    no Candidato: um mesmo candidato pode ter pontuações diferentes conforme
    a função sendo considerada. Desacoplada do motor de avaliação atrás de
    MotorPontuacaoInterface (ver apps.candidatos.interfaces) porque o
    provedor (ex: um motor de IA) ainda não foi decidido — hoje toda
    pontuação é lançada manualmente (origem=MANUAL, avaliador preenchido).
    """

    class Origem(models.TextChoices):
        MANUAL = "manual", "Avaliação manual"
        MOTOR_AUTOMATICO = "motor_automatico", "Motor automático"

    candidato = models.ForeignKey(
        "candidatos.Candidato", related_name="pontuacoes", on_delete=models.CASCADE
    )
    funcao = models.CharField(max_length=150)
    pontuacao = models.DecimalField(max_digits=5, decimal_places=2)
    origem = models.CharField(max_length=20, choices=Origem.choices, default=Origem.MANUAL)
    avaliador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Preenchido quando origem=manual; nulo quando origem=motor_automatico.",
    )
    detalhes = models.JSONField(
        default=dict, blank=True, help_text="Metadados do motor (ex: critérios, versão, prompt)."
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.candidato_id} · {self.funcao}: {self.pontuacao}"
