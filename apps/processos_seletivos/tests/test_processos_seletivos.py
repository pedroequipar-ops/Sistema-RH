import uuid
from datetime import timedelta

import pytest
from django.utils import timezone as django_timezone
from rest_framework.test import APIClient

from apps.candidatos.tests.factories import CandidatoFactory
from apps.core.models import User
from apps.core.tests.factories import UserFactory, UserFunctionPermissionFactory
from apps.processos_seletivos.models import (
    AvaliacaoProcesso,
    EntrevistaAgendamento,
    ProcessoSeletivo,
    TesteAplicado,
)
from apps.processos_seletivos.tests.factories import (
    AvaliacaoProcessoFactory,
    EntrevistaAgendamentoFactory,
    ProcessoSeletivoFactory,
    TesteAplicadoFactory,
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
    UserFunctionPermissionFactory(
        user=rh,
        function="processos-seletivos",
        can_view=True,
        can_create=True,
        can_edit=True,
        can_delete=True,
    )
    return rh


def test_mover_etapa_valida_gera_historico_e_avanca_status_da_vaga():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    vaga = VagaFactory(company_id=company_id, status=Vaga.Status.ABERTA)
    candidato = CandidatoFactory(company_id=company_id)
    processo = ProcessoSeletivoFactory(company_id=company_id, candidato=candidato, vaga=vaga)

    response = client_interno(rh, company_id).post(
        f"/v1/processos-seletivos/{processo.id}/mover_etapa/",
        {"etapa": "teste", "observacao": "Bom currículo"},
        format="json",
    )

    assert response.status_code == 200
    processo.refresh_from_db()
    vaga.refresh_from_db()
    assert processo.etapa_atual == ProcessoSeletivo.Etapa.TESTE
    assert processo.historico_etapas.count() == 1
    assert vaga.status == Vaga.Status.EM_ANDAMENTO


def test_transicao_invalida_e_rejeitada():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    processo = ProcessoSeletivoFactory(company_id=company_id)

    response = client_interno(rh, company_id).post(
        f"/v1/processos-seletivos/{processo.id}/mover_etapa/",
        {"etapa": "contratado"},
        format="json",
    )

    assert response.status_code == 400
    processo.refresh_from_db()
    assert processo.etapa_atual == ProcessoSeletivo.Etapa.TRIAGEM


def test_fluxo_completo_ate_contratado_fecha_a_vaga():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    vaga = VagaFactory(company_id=company_id, status=Vaga.Status.ABERTA)
    processo = ProcessoSeletivoFactory(company_id=company_id, vaga=vaga)
    client = client_interno(rh, company_id)

    for etapa in ("teste", "entrevista", "proposta", "contratado"):
        resposta = client.post(
            f"/v1/processos-seletivos/{processo.id}/mover_etapa/", {"etapa": etapa}, format="json"
        )
        assert resposta.status_code == 200, resposta.data

    processo.refresh_from_db()
    vaga.refresh_from_db()
    assert processo.etapa_atual == ProcessoSeletivo.Etapa.CONTRATADO
    assert vaga.status == Vaga.Status.FECHADA
    assert processo.historico_etapas.count() == 4


def test_isolamento_multi_tenant():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    ProcessoSeletivoFactory(company_id=company_b)

    resposta = client_interno(rh_a, company_a).get("/v1/processos-seletivos/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 0


def test_permissao_negada_sem_rbac():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/processos-seletivos/")

    assert resposta.status_code == 403


def test_gestor_ve_processos_de_qualquer_area():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, area="Tecnologia", company_id=company_id)
    UserFunctionPermissionFactory(user=gestor, function="processos-seletivos", can_view=True)

    vaga_tecnologia = VagaFactory(company_id=company_id, area_solicitante="Tecnologia")
    vaga_financeiro = VagaFactory(company_id=company_id, area_solicitante="Financeiro")
    ProcessoSeletivoFactory(company_id=company_id, vaga=vaga_tecnologia)
    ProcessoSeletivoFactory(company_id=company_id, vaga=vaga_financeiro)

    resposta = client_interno(gestor, company_id).get("/v1/processos-seletivos/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 2


def test_criar_avaliacao_processo_define_autor_automaticamente():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    processo = ProcessoSeletivoFactory(company_id=company_id)

    resposta = client_interno(rh, company_id).post(
        "/v1/avaliacoes-processo/",
        {"processo": str(processo.id), "nota": "8.5", "comentario": "Boa comunicação"},
        format="json",
    )

    assert resposta.status_code == 201
    avaliacao = AvaliacaoProcesso.objects.get(processo=processo)
    assert avaliacao.autor_id == rh.id


def test_criar_e_avaliar_teste():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    processo = ProcessoSeletivoFactory(company_id=company_id)
    client = client_interno(rh, company_id)

    criacao = client.post(
        "/v1/testes-processo/",
        {
            "processo": str(processo.id),
            "tipo": "tecnico",
            "titulo": "Teste de lógica",
            "perguntas": ["Pergunta 1", "Pergunta 2"],
        },
        format="json",
    )
    assert criacao.status_code == 201
    teste_id = criacao.data["id"]
    assert criacao.data["status"] == TesteAplicado.Status.PENDENTE

    avaliacao = client.post(
        f"/v1/testes-processo/{teste_id}/avaliar/",
        {"respostas": {"1": "resposta A"}, "nota": "7.0"},
        format="json",
    )
    assert avaliacao.status_code == 200
    assert avaliacao.data["status"] == TesteAplicado.Status.AVALIADO
    assert avaliacao.data["nota"] == "7.00"


def test_agendar_entrevista_gera_registro():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    processo = ProcessoSeletivoFactory(company_id=company_id)
    data_hora = (django_timezone.now() + timedelta(days=2)).isoformat()

    resposta = client_interno(rh, company_id).post(
        "/v1/entrevistas/",
        {
            "processo": str(processo.id),
            "data_hora": data_hora,
            "duracao_minutos": 45,
            "local_ou_link": "https://meet.example.com/abc",
        },
        format="json",
    )

    assert resposta.status_code == 201
    entrevista = EntrevistaAgendamento.objects.get(processo=processo)
    assert entrevista.duracao_minutos == 45
    assert entrevista.criado_por_id == rh.id


def test_soft_delete_processo():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    processo = ProcessoSeletivoFactory(company_id=company_id)

    resposta = client_interno(rh, company_id).delete(f"/v1/processos-seletivos/{processo.id}/")

    assert resposta.status_code == 204
    assert not ProcessoSeletivo.objects.filter(id=processo.id).exists()
    assert ProcessoSeletivo.all_objects.filter(id=processo.id, active=False).exists()


def test_soft_delete_teste():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    teste = TesteAplicadoFactory(company_id=company_id)

    resposta = client_interno(rh, company_id).delete(f"/v1/testes-processo/{teste.id}/")

    assert resposta.status_code == 204
    assert not TesteAplicado.objects.filter(id=teste.id).exists()
    assert TesteAplicado.all_objects.filter(id=teste.id, active=False).exists()


def test_soft_delete_entrevista():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    entrevista = EntrevistaAgendamentoFactory(company_id=company_id)

    resposta = client_interno(rh, company_id).delete(f"/v1/entrevistas/{entrevista.id}/")

    assert resposta.status_code == 204
    assert not EntrevistaAgendamento.objects.filter(id=entrevista.id).exists()
    assert EntrevistaAgendamento.all_objects.filter(id=entrevista.id, active=False).exists()


def test_isolamento_multi_tenant_avaliacoes():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    AvaliacaoProcessoFactory(company_id=company_b)

    resposta = client_interno(rh_a, company_a).get("/v1/avaliacoes-processo/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 0


def test_permissao_negada_sem_rbac_avaliacoes():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/avaliacoes-processo/")

    assert resposta.status_code == 403


def test_isolamento_multi_tenant_testes():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    TesteAplicadoFactory(company_id=company_b)

    resposta = client_interno(rh_a, company_a).get("/v1/testes-processo/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 0


def test_permissao_negada_sem_rbac_testes():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/testes-processo/")

    assert resposta.status_code == 403


def test_isolamento_multi_tenant_entrevistas():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    EntrevistaAgendamentoFactory(company_id=company_b)

    resposta = client_interno(rh_a, company_a).get("/v1/entrevistas/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 0


def test_permissao_negada_sem_rbac_entrevistas():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/entrevistas/")

    assert resposta.status_code == 403
