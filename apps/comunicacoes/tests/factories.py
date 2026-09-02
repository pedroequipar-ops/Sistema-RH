import factory

from apps.comunicacoes.models import EmailEnviado, Notificacao
from apps.core.tests.factories import UserFactory
from apps.processos_seletivos.tests.factories import ProcessoSeletivoFactory


class EmailEnviadoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailEnviado

    tipo = "confirmacao_inscricao"
    destinatario = factory.Sequence(lambda n: f"destinatario{n}@example.com")
    assunto = "Recebemos sua candidatura!"
    processo = factory.SubFactory(ProcessoSeletivoFactory)
    candidato = factory.SelfAttribute("processo.candidato")
    status = EmailEnviado.Status.ENVIADO
    company_id = factory.SelfAttribute("processo.company_id")


class NotificacaoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notificacao

    destinatario = factory.SubFactory(UserFactory)
    tipo = "processo_mudanca_etapa"
    mensagem = "Candidato avançou de etapa."
    processo = factory.SubFactory(ProcessoSeletivoFactory)
    company_id = factory.SelfAttribute("destinatario.company_id")
