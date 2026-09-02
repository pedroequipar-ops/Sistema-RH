import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.core.models import User
from apps.core.tests.factories import UserFactory, UserFunctionPermissionFactory
from apps.processos_seletivos.models import HistoricoEtapaProcesso, ProcessoSeletivo
from apps.processos_seletivos.tests.factories import (
    HistoricoEtapaProcessoFactory,
    ProcessoSeletivoFactory,
)
from apps.vagas.models import Vaga
from apps.vagas.tests.factories import VagaFactory

pytestmark = pytest.mark.django_db


def client_interno(user, company_id):
    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def rh_com_permissao(company_id):
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    UserFunctionPermissionFactory(user=rh, function="relatorios", can_view=True)
    return rh


ENDPOINTS = [
    "/v1/relatorios/tempo-medio-contratacao/",
    "/v1/relatorios/candidatos-por-vaga/",
    "/v1/relatorios/funil-conversao/",
    "/v1/relatorios/custo-contratacao/",
]


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_permissao_negada_sem_rbac(endpoint):
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get(endpoint)

    assert resposta.status_code == 403


def test_isolamento_multi_tenant_tempo_medio_contratacao():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    ProcessoSeletivoFactory(company_id=company_b, etapa_atual=ProcessoSeletivo.Etapa.CONTRATADO)

    resposta = client_interno(rh_a, company_a).get("/v1/relatorios/tempo-medio-contratacao/")

    assert resposta.status_code == 200
    assert resposta.data["total_contratacoes"] == 0


def test_isolamento_multi_tenant_candidatos_por_vaga():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    ProcessoSeletivoFactory(company_id=company_b)

    resposta = client_interno(rh_a, company_a).get("/v1/relatorios/candidatos-por-vaga/")

    assert resposta.status_code == 200
    assert resposta.data == []


def test_isolamento_multi_tenant_funil_conversao():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    processo_b = ProcessoSeletivoFactory(company_id=company_b)
    HistoricoEtapaProcessoFactory(
        processo=processo_b, de_etapa="", para_etapa=ProcessoSeletivo.Etapa.TRIAGEM
    )

    resposta = client_interno(rh_a, company_a).get("/v1/relatorios/funil-conversao/")

    assert resposta.status_code == 200
    por_etapa = {item["etapa"]: item for item in resposta.data}
    assert por_etapa["triagem"]["entraram"] == 0


def test_isolamento_multi_tenant_custo_contratacao():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    VagaFactory(company_id=company_b, status=Vaga.Status.FECHADA, custo_contratacao=Decimal("5000"))

    resposta = client_interno(rh_a, company_a).get("/v1/relatorios/custo-contratacao/")

    assert resposta.status_code == 200
    assert resposta.data["vagas"] == []
    assert Decimal(resposta.data["custo_total"]) == Decimal("0")


def test_tempo_medio_contratacao_calcula_media_em_dias():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)

    processo = ProcessoSeletivoFactory(
        company_id=company_id, etapa_atual=ProcessoSeletivo.Etapa.CONTRATADO
    )
    inicio = timezone.now() - timedelta(days=10)
    ProcessoSeletivo.objects.filter(id=processo.id).update(created_at=inicio)

    historico = HistoricoEtapaProcessoFactory(
        processo=processo, de_etapa="proposta", para_etapa=ProcessoSeletivo.Etapa.CONTRATADO
    )
    HistoricoEtapaProcesso.objects.filter(id=historico.id).update(
        created_at=inicio + timedelta(days=4)
    )

    resposta = client_interno(rh, company_id).get("/v1/relatorios/tempo-medio-contratacao/")

    assert resposta.status_code == 200
    assert resposta.data["total_contratacoes"] == 1
    assert resposta.data["tempo_medio_dias"] == 4.0


def test_tempo_medio_contratacao_sem_contratados_retorna_nulo():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    ProcessoSeletivoFactory(company_id=company_id, etapa_atual=ProcessoSeletivo.Etapa.TRIAGEM)

    resposta = client_interno(rh, company_id).get("/v1/relatorios/tempo-medio-contratacao/")

    assert resposta.status_code == 200
    assert resposta.data["total_contratacoes"] == 0
    assert resposta.data["tempo_medio_dias"] is None


def test_candidatos_por_vaga_agrupa_corretamente():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    vaga = VagaFactory(company_id=company_id, cargo="Dev Backend")
    ProcessoSeletivoFactory(company_id=company_id, vaga=vaga)
    ProcessoSeletivoFactory(company_id=company_id, vaga=vaga)
    outra_vaga = VagaFactory(company_id=company_id, cargo="Dev Frontend")
    ProcessoSeletivoFactory(company_id=company_id, vaga=outra_vaga)

    resposta = client_interno(rh, company_id).get("/v1/relatorios/candidatos-por-vaga/")

    assert resposta.status_code == 200
    por_vaga = {item["vaga_id"]: item["total_candidatos"] for item in resposta.data}
    assert por_vaga[str(vaga.id)] == 2
    assert por_vaga[str(outra_vaga.id)] == 1


def test_funil_conversao_calcula_taxa_por_etapa():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)

    processos = [ProcessoSeletivoFactory(company_id=company_id) for _ in range(4)]
    for processo in processos:
        HistoricoEtapaProcessoFactory(
            processo=processo, de_etapa="", para_etapa=ProcessoSeletivo.Etapa.TRIAGEM
        )

    avancam_para_teste = processos[:2]
    for processo in avancam_para_teste:
        HistoricoEtapaProcessoFactory(
            processo=processo,
            de_etapa=ProcessoSeletivo.Etapa.TRIAGEM,
            para_etapa=ProcessoSeletivo.Etapa.TESTE,
        )

    HistoricoEtapaProcessoFactory(
        processo=avancam_para_teste[0],
        de_etapa=ProcessoSeletivo.Etapa.TESTE,
        para_etapa=ProcessoSeletivo.Etapa.ENTREVISTA,
    )

    resposta = client_interno(rh, company_id).get("/v1/relatorios/funil-conversao/")

    assert resposta.status_code == 200
    por_etapa = {item["etapa"]: item for item in resposta.data}

    assert por_etapa["triagem"]["entraram"] == 4
    assert por_etapa["triagem"]["avancaram"] == 2
    assert por_etapa["triagem"]["taxa_conversao"] == 50.0

    assert por_etapa["teste"]["entraram"] == 2
    assert por_etapa["teste"]["avancaram"] == 1
    assert por_etapa["teste"]["taxa_conversao"] == 50.0

    assert por_etapa["entrevista"]["entraram"] == 1
    assert por_etapa["entrevista"]["avancaram"] == 0
    assert por_etapa["entrevista"]["taxa_conversao"] == 0.0

    assert por_etapa["proposta"]["entraram"] == 0
    assert por_etapa["proposta"]["taxa_conversao"] is None

    assert por_etapa["contratado"]["avancaram"] is None


def test_custo_contratacao_agrega_media_e_total():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    VagaFactory(
        company_id=company_id,
        cargo="Dev Backend",
        status=Vaga.Status.FECHADA,
        custo_contratacao=Decimal("3000.00"),
    )
    VagaFactory(
        company_id=company_id,
        cargo="Dev Frontend",
        status=Vaga.Status.FECHADA,
        custo_contratacao=Decimal("5000.00"),
    )
    VagaFactory(
        company_id=company_id, status=Vaga.Status.ABERTA, custo_contratacao=Decimal("9999.00")
    )  # não fechada, não deve entrar

    resposta = client_interno(rh, company_id).get("/v1/relatorios/custo-contratacao/")

    assert resposta.status_code == 200
    assert len(resposta.data["vagas"]) == 2
    assert Decimal(resposta.data["custo_medio"]) == Decimal("4000.00")
    assert Decimal(resposta.data["custo_total"]) == Decimal("8000.00")


def test_gestor_so_ve_relatorio_da_propria_area():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, area="Tecnologia", company_id=company_id)
    UserFunctionPermissionFactory(user=gestor, function="relatorios", can_view=True)

    vaga_tecnologia = VagaFactory(company_id=company_id, area_solicitante="Tecnologia")
    vaga_financeiro = VagaFactory(company_id=company_id, area_solicitante="Financeiro")
    ProcessoSeletivoFactory(company_id=company_id, vaga=vaga_tecnologia)
    ProcessoSeletivoFactory(company_id=company_id, vaga=vaga_financeiro)

    resposta = client_interno(gestor, company_id).get("/v1/relatorios/candidatos-por-vaga/")

    assert resposta.status_code == 200
    assert len(resposta.data) == 1
    assert resposta.data[0]["vaga_id"] == str(vaga_tecnologia.id)
