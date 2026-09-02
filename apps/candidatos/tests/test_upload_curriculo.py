import uuid
from io import BytesIO

import pytest
from rest_framework.test import APIClient

from apps.candidatos.models import Candidato
from apps.candidatos.tests.factories import CandidatoFactory
from apps.core.models import User
from apps.core.tests.factories import UserFactory, UserFunctionPermissionFactory

pytestmark = pytest.mark.django_db


def _arquivo_fake():
    arquivo = BytesIO(b"%PDF-1.4 conteudo qualquer")
    arquivo.name = "curriculo.pdf"
    return arquivo


def client_publico(company_id):
    client = APIClient()
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def client_candidato(candidato, company_id, senha="Teste123!"):
    login = client_publico(company_id).post(
        "/v1/candidatos/auth/token/", {"email": candidato.email, "password": senha}, format="json"
    )
    client = APIClient()
    client.credentials(
        HTTP_X_COMPANY_ID=str(company_id), HTTP_AUTHORIZATION=f"Bearer {login.data['access']}"
    )
    return client


def client_interno(user, company_id):
    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def test_candidato_faz_upload_do_proprio_curriculo():
    company_id = uuid.uuid4()
    candidato = CandidatoFactory(company_id=company_id, password="Teste123!")

    resposta = client_candidato(candidato, company_id).post(
        "/v1/candidatos/me/curriculo/", {"curriculo": _arquivo_fake()}, format="multipart"
    )

    assert resposta.status_code == 202
    candidato.refresh_from_db()
    assert candidato.curriculo_status == Candidato.StatusProcessamento.PROCESSANDO
    assert candidato.curriculo_bucket
    assert candidato.curriculo_key


def test_upload_de_curriculo_sem_arquivo_retorna_400():
    company_id = uuid.uuid4()
    candidato = CandidatoFactory(company_id=company_id, password="Teste123!")

    resposta = client_candidato(candidato, company_id).post(
        "/v1/candidatos/me/curriculo/", {}, format="multipart"
    )

    assert resposta.status_code == 400


def test_rh_faz_upload_de_curriculo_de_candidato_do_banco_de_talentos():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    UserFunctionPermissionFactory(user=rh, function="candidatos", can_view=True, can_edit=True)
    candidato = CandidatoFactory(company_id=company_id)

    resposta = client_interno(rh, company_id).post(
        f"/v1/candidatos/{candidato.id}/upload_curriculo/",
        {"curriculo": _arquivo_fake()},
        format="multipart",
    )

    assert resposta.status_code == 202
    candidato.refresh_from_db()
    assert candidato.curriculo_status == Candidato.StatusProcessamento.PROCESSANDO
