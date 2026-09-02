import uuid

import pytest
from rest_framework.test import APIClient

from apps.candidatos.models import PontuacaoCandidato
from apps.candidatos.services import get_motor_pontuacao
from apps.candidatos.tests.factories import CandidatoFactory, PontuacaoCandidatoFactory
from apps.core.models import User
from apps.core.tests.factories import UserFactory, UserFunctionPermissionFactory
from apps.processos_seletivos.tests.factories import ProcessoSeletivoFactory
from apps.vagas.tests.factories import VagaFactory

pytestmark = pytest.mark.django_db


def client_interno(user, company_id):
    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def rh_com_permissao(company_id):
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    UserFunctionPermissionFactory(
        user=rh, function="candidatos", can_view=True, can_create=True, can_edit=True
    )
    return rh


def test_criar_pontuacao_manual_define_origem_e_avaliador_automaticamente():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    candidato = CandidatoFactory(company_id=company_id)

    resposta = client_interno(rh, company_id).post(
        "/v1/pontuacoes-candidato/",
        {"candidato": str(candidato.id), "funcao": "Analista de RH", "pontuacao": "82.5"},
        format="json",
    )

    assert resposta.status_code == 201
    pontuacao = PontuacaoCandidato.objects.get(candidato=candidato)
    assert pontuacao.funcao == "Analista de RH"
    assert pontuacao.origem == PontuacaoCandidato.Origem.MANUAL
    assert pontuacao.avaliador_id == rh.id


def test_mesmo_candidato_pode_ter_pontuacoes_diferentes_por_funcao():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    candidato = CandidatoFactory(company_id=company_id)
    client = client_interno(rh, company_id)

    client.post(
        "/v1/pontuacoes-candidato/",
        {"candidato": str(candidato.id), "funcao": "Backend", "pontuacao": "90"},
        format="json",
    )
    client.post(
        "/v1/pontuacoes-candidato/",
        {"candidato": str(candidato.id), "funcao": "Frontend", "pontuacao": "60"},
        format="json",
    )

    pontuacoes = PontuacaoCandidato.objects.filter(candidato=candidato)
    assert pontuacoes.count() == 2
    assert set(pontuacoes.values_list("funcao", flat=True)) == {"Backend", "Frontend"}


def test_isolamento_multi_tenant_pontuacoes():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    PontuacaoCandidatoFactory(company_id=company_b)

    resposta = client_interno(rh_a, company_a).get("/v1/pontuacoes-candidato/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 0


def test_permissao_negada_sem_rbac_pontuacoes():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/pontuacoes-candidato/")

    assert resposta.status_code == 403


def test_gestor_so_ve_pontuacoes_de_candidatos_com_processo_na_propria_area():
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
    PontuacaoCandidatoFactory(company_id=company_id, candidato=candidato_tecnologia)
    PontuacaoCandidatoFactory(company_id=company_id, candidato=candidato_financeiro)

    resposta = client_interno(gestor, company_id).get("/v1/pontuacoes-candidato/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 1


def test_motor_de_pontuacao_automatico_ainda_nao_esta_configurado():
    with pytest.raises(NotImplementedError):
        get_motor_pontuacao()
