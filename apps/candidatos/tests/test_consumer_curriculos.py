import json
from io import BytesIO
from unittest.mock import patch

import pytest
from django.conf import settings

from apps.candidatos.management.commands.consumir_curriculos import Command
from apps.candidatos.models import Candidato
from apps.candidatos.tests.factories import CandidatoFactory
from utils.storage import MinioStorage

pytestmark = pytest.mark.django_db


class FakeMethod:
    def __init__(self, delivery_tag=1):
        self.delivery_tag = delivery_tag


class FakeChannel:
    def __init__(self):
        self.acked = []

    def basic_ack(self, delivery_tag):
        self.acked.append(delivery_tag)


def _publicar(candidato):
    command = Command()
    channel = FakeChannel()
    payload = json.dumps({"candidato_id": str(candidato.id)}).encode()
    command._callback(channel, FakeMethod(), None, payload)
    return channel


@patch("apps.candidatos.management.commands.consumir_curriculos.get_parser")
def test_consumir_curriculo_processa_com_sucesso(mock_get_parser):
    mock_get_parser.return_value.extrair_dados.return_value = {
        "nome": "",
        "telefone": "(11) 99999-8888",
        "resumo_experiencia": "Experiência extraída do currículo.",
    }

    candidato = CandidatoFactory(nome="", telefone="")
    key = f"{candidato.company_id}/{candidato.id}/curriculo.pdf"
    MinioStorage().upload_fileobj(
        settings.MINIO_BUCKET_CURRICULOS, key, BytesIO(b"conteudo"), content_type="application/pdf"
    )
    Candidato.objects.filter(id=candidato.id).update(
        curriculo_bucket=settings.MINIO_BUCKET_CURRICULOS,
        curriculo_key=key,
        curriculo_status=Candidato.StatusProcessamento.PROCESSANDO,
    )
    candidato.refresh_from_db()

    channel = _publicar(candidato)

    candidato.refresh_from_db()
    assert candidato.curriculo_status == Candidato.StatusProcessamento.PROCESSADO
    assert candidato.telefone == "(11) 99999-8888"
    assert candidato.resumo_experiencia == "Experiência extraída do currículo."
    assert channel.acked == [1]


def test_consumir_curriculo_registra_falha_quando_objeto_nao_existe_no_minio():
    candidato = CandidatoFactory()
    Candidato.objects.filter(id=candidato.id).update(
        curriculo_bucket=settings.MINIO_BUCKET_CURRICULOS,
        curriculo_key="chave/que/nao/existe.pdf",
        curriculo_status=Candidato.StatusProcessamento.PROCESSANDO,
    )
    candidato.refresh_from_db()

    channel = _publicar(candidato)

    candidato.refresh_from_db()
    assert candidato.curriculo_status == Candidato.StatusProcessamento.FALHA
    assert candidato.curriculo_erro
    assert channel.acked == [1]
