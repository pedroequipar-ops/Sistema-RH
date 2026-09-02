import uuid

import pytest
from rest_framework.test import APIClient

from apps.candidatos.factories import CandidatoFactory
from apps.candidatos.models import Candidato
from apps.core.factories import UserFactory, UserFunctionPermissionFactory
from apps.core.models import User
from apps.processos_seletivos.factories import ProcessoSeletivoFactory
from apps.processos_seletivos.models import ProcessoSeletivo
from apps.vagas.factories import VagaFactory
from apps.vagas.models import Vaga

pytestmark = pytest.mark.django_db


def client_interno(user, company_id):
    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def client_publico(company_id):
    client = APIClient()
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def client_candidato_token(company_id, access_token):
    client = APIClient()
    client.credentials(
        HTTP_X_COMPANY_ID=str(company_id), HTTP_AUTHORIZATION=f"Bearer {access_token}"
    )
    return client


def test_candidatura_publica_cria_candidato_e_processo():
    company_id = uuid.uuid4()
    vaga = VagaFactory(
        company_id=company_id, status=Vaga.Status.ABERTA, area_solicitante="Tecnologia"
    )

    payload = {
        "vaga_id": str(vaga.id),
        "email": "novo.candidato@example.com",
        "nome": "Novo Candidato",
        "skills": ["Python", "SQL"],
    }
    response = client_publico(company_id).post("/v1/candidaturas/", payload, format="json")

    assert response.status_code == 201
    candidato = Candidato.objects.get(email="novo.candidato@example.com", company_id=company_id)
    assert candidato.skills == ["python", "sql"]
    processo = ProcessoSeletivo.objects.get(candidato=candidato, vaga=vaga)
    assert processo.etapa_atual == ProcessoSeletivo.Etapa.TRIAGEM


def test_candidatura_em_vaga_nao_aberta_falha():
    company_id = uuid.uuid4()
    vaga = VagaFactory(company_id=company_id, status=Vaga.Status.PAUSADA)

    payload = {"vaga_id": str(vaga.id), "email": "x@example.com", "nome": "X"}
    response = client_publico(company_id).post("/v1/candidaturas/", payload, format="json")

    assert response.status_code == 400


def test_candidatura_duplicada_na_mesma_vaga_falha():
    company_id = uuid.uuid4()
    vaga = VagaFactory(company_id=company_id, status=Vaga.Status.ABERTA)
    payload = {"vaga_id": str(vaga.id), "email": "dup@example.com", "nome": "Dup"}

    primeira = client_publico(company_id).post("/v1/candidaturas/", payload, format="json")
    segunda = client_publico(company_id).post("/v1/candidaturas/", payload, format="json")

    assert primeira.status_code == 201
    assert segunda.status_code == 400


def test_cadastro_candidato_e_login_retornam_tokens():
    company_id = uuid.uuid4()
    payload = {"email": "portal@example.com", "password": "SenhaForte123", "nome": "Portal"}

    cadastro = client_publico(company_id).post("/v1/candidatos/cadastro/", payload, format="json")
    assert cadastro.status_code == 201
    assert "access" in cadastro.data and "refresh" in cadastro.data

    login = client_publico(company_id).post(
        "/v1/candidatos/auth/token/",
        {"email": "portal@example.com", "password": "SenhaForte123"},
        format="json",
    )
    assert login.status_code == 200
    assert "access" in login.data


def test_candidato_acessa_e_edita_proprio_perfil():
    company_id = uuid.uuid4()
    candidato = CandidatoFactory(company_id=company_id, password="Teste123!")

    cadastro_login = client_publico(company_id).post(
        "/v1/candidatos/auth/token/",
        {"email": candidato.email, "password": "Teste123!"},
        format="json",
    )
    access = cadastro_login.data["access"]
    client = client_candidato_token(company_id, access)

    resposta = client.get("/v1/candidatos/me/")
    assert resposta.status_code == 200
    assert resposta.data["email"] == candidato.email

    edicao = client.patch("/v1/candidatos/me/", {"cidade": "Rio de Janeiro"}, format="json")
    assert edicao.status_code == 200
    candidato.refresh_from_db()
    assert candidato.cidade == "Rio de Janeiro"


def test_token_de_candidato_nao_acessa_endpoint_interno_do_rh():
    company_id = uuid.uuid4()
    candidato = CandidatoFactory(company_id=company_id, password="Teste123!")
    login = client_publico(company_id).post(
        "/v1/candidatos/auth/token/",
        {"email": candidato.email, "password": "Teste123!"},
        format="json",
    )
    access = login.data["access"]

    resposta = client_candidato_token(company_id, access).get("/v1/candidatos/")

    assert resposta.status_code == 401


def test_minhas_candidaturas_lista_processos_do_proprio_candidato():
    company_id = uuid.uuid4()
    candidato = CandidatoFactory(company_id=company_id, password="Teste123!")
    ProcessoSeletivoFactory(candidato=candidato, company_id=company_id)
    ProcessoSeletivoFactory(company_id=company_id)  # de outro candidato, não deve aparecer

    login = client_publico(company_id).post(
        "/v1/candidatos/auth/token/",
        {"email": candidato.email, "password": "Teste123!"},
        format="json",
    )
    access = login.data["access"]

    resposta = client_candidato_token(company_id, access).get("/v1/candidatos/me/candidaturas/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 1


def test_rh_lista_banco_de_talentos_com_isolamento_multi_tenant():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = UserFactory(role=User.Role.RH, company_id=company_a)
    UserFunctionPermissionFactory(user=rh_a, function="candidatos", can_view=True)
    CandidatoFactory(company_id=company_a)
    CandidatoFactory(company_id=company_b)

    resposta = client_interno(rh_a, company_a).get("/v1/candidatos/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 1


def test_permissao_negada_sem_rbac_banco_de_talentos():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    # sem UserFunctionPermission cadastrado

    resposta = client_interno(rh, company_id).get("/v1/candidatos/")

    assert resposta.status_code == 403


def test_gestor_so_ve_candidatos_com_processo_na_propria_area():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, area="Tecnologia", company_id=company_id)
    UserFunctionPermissionFactory(user=gestor, function="candidatos", can_view=True)

    vaga_tecnologia = VagaFactory(company_id=company_id, area_solicitante="Tecnologia")
    vaga_financeiro = VagaFactory(company_id=company_id, area_solicitante="Financeiro")
    candidato_tecnologia = CandidatoFactory(company_id=company_id)
    candidato_financeiro = CandidatoFactory(company_id=company_id)
    ProcessoSeletivoFactory(
        company_id=company_id, candidato=candidato_tecnologia, vaga=vaga_tecnologia
    )
    ProcessoSeletivoFactory(
        company_id=company_id, candidato=candidato_financeiro, vaga=vaga_financeiro
    )

    resposta = client_interno(gestor, company_id).get("/v1/candidatos/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 1


def test_vagas_publicas_lista_so_vagas_abertas():
    company_id = uuid.uuid4()
    VagaFactory(company_id=company_id, status=Vaga.Status.ABERTA)
    VagaFactory(company_id=company_id, status=Vaga.Status.PAUSADA)

    resposta = client_publico(company_id).get("/v1/vagas-publicas/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 1
