import factory

from apps.candidatos.factories import CandidatoFactory
from apps.processos_seletivos.models import ProcessoSeletivo
from apps.vagas.factories import VagaFactory


class ProcessoSeletivoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProcessoSeletivo

    candidato = factory.SubFactory(CandidatoFactory)
    vaga = factory.SubFactory(VagaFactory)
    etapa_atual = ProcessoSeletivo.Etapa.TRIAGEM
    company_id = factory.SelfAttribute("candidato.company_id")
