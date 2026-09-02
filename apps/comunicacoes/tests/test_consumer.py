import json

import pytest

from apps.comunicacoes.management.commands.consumir_comunicacoes import Command
from apps.comunicacoes.models import EmailEnviado, Notificacao
from apps.processos_seletivos.tests.factories import ProcessoSeletivoFactory

pytestmark = pytest.mark.django_db


class FakeMethod:
    def __init__(self, delivery_tag=1):
        self.delivery_tag = delivery_tag


class FakeChannel:
    def __init__(self):
        self.acked = []

    def basic_ack(self, delivery_tag):
        self.acked.append(delivery_tag)


def _publicar(command_method, payload):
    command = Command()
    channel = FakeChannel()
    getattr(command, command_method)(channel, FakeMethod(), None, json.dumps(payload).encode())
    return channel


def test_consumir_mail_envia_email_e_persiste_historico(mailoutbox):
    processo = ProcessoSeletivoFactory()
    payload = {
        "tipo": "confirmacao_inscricao",
        "candidato_email": processo.candidato.email,
        "candidato_nome": processo.candidato.nome,
        "vaga_cargo": processo.vaga.cargo,
        "processo_id": str(processo.id),
    }

    channel = _publicar("_consumir_mail", payload)

    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [processo.candidato.email]
    email_enviado = EmailEnviado.objects.get(processo=processo)
    assert email_enviado.status == EmailEnviado.Status.ENVIADO
    assert str(email_enviado.company_id) == str(processo.company_id)
    assert channel.acked == [1]


def test_consumir_mail_de_entrevista_anexa_ics(mailoutbox):
    processo = ProcessoSeletivoFactory()
    payload = {
        "tipo": "convite_entrevista",
        "candidato_email": processo.candidato.email,
        "candidato_nome": processo.candidato.nome,
        "vaga_cargo": processo.vaga.cargo,
        "data_hora": "2026-01-01T10:00:00-03:00",
        "local_ou_link": "https://meet.example.com/x",
        "ics_conteudo": "BEGIN:VCALENDAR\r\nEND:VCALENDAR",
        "ics_filename": "entrevista.ics",
        "processo_id": str(processo.id),
    }

    _publicar("_consumir_mail", payload)

    assert len(mailoutbox) == 1
    anexo = mailoutbox[0].attachments[0]
    assert anexo[0] == "entrevista.ics"


def test_consumir_mail_registra_falha_quando_tipo_desconhecido(mailoutbox):
    processo = ProcessoSeletivoFactory()
    payload = {
        "tipo": "tipo_invalido",
        "candidato_email": processo.candidato.email,
        "processo_id": str(processo.id),
    }

    _publicar("_consumir_mail", payload)

    assert len(mailoutbox) == 0
    email_enviado = EmailEnviado.objects.get(processo=processo)
    assert email_enviado.status == EmailEnviado.Status.FALHA
    assert "desconhecido" in email_enviado.erro.lower()


def test_consumir_notificacao_persiste_registro():
    processo = ProcessoSeletivoFactory()
    payload = {
        "tipo": "processo_mudanca_etapa",
        "destinatario_user_id": str(processo.vaga.solicitante_id),
        "candidato_nome": processo.candidato.nome,
        "vaga_cargo": processo.vaga.cargo,
        "etapa_atual": "teste",
        "processo_id": str(processo.id),
    }

    channel = _publicar("_consumir_notificacao", payload)

    notificacao = Notificacao.objects.get(processo=processo)
    assert notificacao.destinatario_id == processo.vaga.solicitante_id
    assert "teste" in notificacao.mensagem
    assert notificacao.lida is False
    assert channel.acked == [1]
