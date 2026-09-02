import factory

from apps.admissao.models import ChecklistItemAdmissao, Funcionario
from apps.processos_seletivos.tests.factories import ProcessoSeletivoFactory


class FuncionarioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Funcionario

    processo = factory.SubFactory(ProcessoSeletivoFactory)
    candidato = factory.SelfAttribute("processo.candidato")
    vaga = factory.SelfAttribute("processo.vaga")
    cargo = factory.SelfAttribute("processo.vaga.cargo")
    company_id = factory.SelfAttribute("processo.company_id")


class ChecklistItemAdmissaoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChecklistItemAdmissao

    funcionario = factory.SubFactory(FuncionarioFactory)
    nome_documento = "RG"
    company_id = factory.SelfAttribute("funcionario.company_id")
