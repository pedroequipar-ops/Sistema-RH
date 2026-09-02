import uuid

import pytest
from rest_framework.test import APIClient

from apps.candidatos.tests.factories import CandidatoFactory
from apps.core.models import User
from apps.core.tests.factories import UserFactory, UserFunctionPermissionFactory

pytestmark = pytest.mark.django_db


def client_publico(company_id):
    client = APIClient()
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def test_login_com_email_inexistente_retorna_400():
    company_id = uuid.uuid4()

    resposta = client_publico(company_id).post(
        "/v1/candidatos/auth/token/",
        {"email": "nao.existe@example.com", "password": "qualquer"},
        format="json",
    )

    assert resposta.status_code == 400


def test_login_com_senha_errada_retorna_400():
    company_id = uuid.uuid4()
    candidato = CandidatoFactory(company_id=company_id, password="SenhaCerta123")

    resposta = client_publico(company_id).post(
        "/v1/candidatos/auth/token/",
        {"email": candidato.email, "password": "SenhaErrada"},
        format="json",
    )

    assert resposta.status_code == 400


def test_token_interno_do_rh_nao_acessa_endpoint_do_candidato():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    UserFunctionPermissionFactory(user=rh, function="candidatos", can_view=True)

    resposta_login = client_publico(company_id).post(
        "/v1/auth/token/", {"email": rh.email, "password": "Teste123!"}, format="json"
    )
    # UserFactory usa senha padrão "Teste123!" (ver apps.core.tests.factories)
    assert resposta_login.status_code == 200
    access = resposta_login.data["access"]

    client = APIClient()
    client.credentials(HTTP_X_COMPANY_ID=str(company_id), HTTP_AUTHORIZATION=f"Bearer {access}")
    resposta = client.get("/v1/candidatos/me/")

    assert resposta.status_code == 401


def test_candidato_com_registro_apagado_apos_emissao_do_token_e_rejeitado():
    company_id = uuid.uuid4()
    candidato = CandidatoFactory(company_id=company_id, password="Teste123!")
    login = client_publico(company_id).post(
        "/v1/candidatos/auth/token/",
        {"email": candidato.email, "password": "Teste123!"},
        format="json",
    )
    access = login.data["access"]

    candidato.soft_delete()

    client = APIClient()
    client.credentials(HTTP_X_COMPANY_ID=str(company_id), HTTP_AUTHORIZATION=f"Bearer {access}")
    resposta = client.get("/v1/candidatos/me/")

    assert resposta.status_code == 401
