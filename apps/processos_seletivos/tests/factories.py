from datetime import timedelta

import factory
from django.utils import timezone

from apps.candidatos.tests.factories import CandidatoFactory
from apps.core.tests.factories import UserFactory
from apps.processos_seletivos.models import (
    AvaliacaoProcesso,
    EntrevistaAgendamento,
    HistoricoEtapaProcesso,
    ProcessoSeletivo,
    TesteAplicado,
)
from apps.vagas.tests.factories import VagaFactory


class ProcessoSeletivoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProcessoSeletivo

    candidato = factory.SubFactory(CandidatoFactory)
    vaga = factory.SubFactory(VagaFactory)
    etapa_atual = ProcessoSeletivo.Etapa.TRIAGEM
    company_id = factory.SelfAttribute("candidato.company_id")


class HistoricoEtapaProcessoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HistoricoEtapaProcesso

    processo = factory.SubFactory(ProcessoSeletivoFactory)
    de_etapa = ""
    para_etapa = ProcessoSeletivo.Etapa.TRIAGEM
    alterado_por = factory.SubFactory(UserFactory)
    company_id = factory.SelfAttribute("processo.company_id")


class AvaliacaoProcessoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AvaliacaoProcesso

    processo = factory.SubFactory(ProcessoSeletivoFactory)
    autor = factory.SubFactory(UserFactory)
    nota = 8.0
    comentario = "Boa comunicação, segue pra próxima etapa."
    company_id = factory.SelfAttribute("processo.company_id")


class TesteAplicadoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TesteAplicado

    processo = factory.SubFactory(ProcessoSeletivoFactory)
    tipo = TesteAplicado.Tipo.TECNICO
    titulo = "Teste técnico"
    perguntas = factory.LazyFunction(lambda: ["Pergunta 1", "Pergunta 2"])
    criado_por = factory.SubFactory(UserFactory)
    company_id = factory.SelfAttribute("processo.company_id")


class EntrevistaAgendamentoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EntrevistaAgendamento

    processo = factory.SubFactory(ProcessoSeletivoFactory)
    data_hora = factory.LazyFunction(lambda: timezone.now() + timedelta(days=2))
    duracao_minutos = 60
    local_ou_link = "https://meet.example.com/entrevista"
    criado_por = factory.SubFactory(UserFactory)
    company_id = factory.SelfAttribute("processo.company_id")
