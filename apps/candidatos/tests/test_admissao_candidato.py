import uuid

import pytest
from rest_framework.test import APIClient

from apps.admissao.models import ChecklistItemAdmissao
from apps.admissao.tests.factories import ChecklistItemAdmissaoFactory, FuncionarioFactory
from apps.candidatos.tests.factories import CandidatoFactory

pytestmark = pytest.mark.django_db


def client_publico(company_id):
    client = APIClient()
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def _login(candidato, company_id, senha="Teste123!"):
    resposta = client_publico(company_id).post(
        "/v1/candidatos/auth/token/",
        {"email": candidato.email, "password": senha},
        format="json",
    )
    return resposta.data["access"]


def client_candidato(candidato, company_id):
    access = _login(candidato, company_id)
    client = APIClient()
    client.credentials(HTTP_X_COMPANY_ID=str(company_id), HTTP_AUTHORIZATION=f"Bearer {access}")
    return client


def test_candidato_ve_a_propria_admissao():
    company_id = uuid.uuid4()
    candidato = CandidatoFactory(company_id=company_id, password="Teste123!")
    funcionario = FuncionarioFactory(company_id=company_id, candidato=candidato)
    ChecklistItemAdmissaoFactory(company_id=company_id, funcionario=funcionario)

    resposta = client_candidato(candidato, company_id).get("/v1/candidatos/me/admissao/")

    assert resposta.status_code == 200
    assert resposta.data["candidato"] == candidato.id
    assert len(resposta.data["checklist"]) == 1


def test_candidato_sem_admissao_recebe_404():
    company_id = uuid.uuid4()
    candidato = CandidatoFactory(company_id=company_id, password="Teste123!")

    resposta = client_candidato(candidato, company_id).get("/v1/candidatos/me/admissao/")

    assert resposta.status_code == 404


def test_candidato_faz_upload_de_documento_do_proprio_checklist():
    company_id = uuid.uuid4()
    candidato = CandidatoFactory(company_id=company_id, password="Teste123!")
    funcionario = FuncionarioFactory(company_id=company_id, candidato=candidato)
    item = ChecklistItemAdmissaoFactory(company_id=company_id, funcionario=funcionario)

    from io import BytesIO

    arquivo = BytesIO(b"conteudo-fake")
    arquivo.name = "rg.pdf"

    resposta = client_candidato(candidato, company_id).post(
        f"/v1/candidatos/me/admissao/checklist/{item.id}/upload/",
        {"documento": arquivo},
        format="multipart",
    )

    assert resposta.status_code == 202
    item.refresh_from_db()
    assert item.status == ChecklistItemAdmissao.Status.ENVIADO
    assert item.documento_key


def test_candidato_nao_acessa_item_de_checklist_de_outro_candidato():
    company_id = uuid.uuid4()
    candidato_a = CandidatoFactory(company_id=company_id, password="Teste123!")
    candidato_b = CandidatoFactory(company_id=company_id, password="Teste123!")
    funcionario_b = FuncionarioFactory(company_id=company_id, candidato=candidato_b)
    item_de_b = ChecklistItemAdmissaoFactory(company_id=company_id, funcionario=funcionario_b)

    from io import BytesIO

    arquivo = BytesIO(b"conteudo-fake")
    arquivo.name = "rg.pdf"

    resposta = client_candidato(candidato_a, company_id).post(
        f"/v1/candidatos/me/admissao/checklist/{item_de_b.id}/upload/",
        {"documento": arquivo},
        format="multipart",
    )

    assert resposta.status_code == 404
