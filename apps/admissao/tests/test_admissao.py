import uuid

import pytest
from rest_framework.test import APIClient

from apps.admissao.models import ChecklistItemAdmissao, Funcionario
from apps.admissao.tests.factories import ChecklistItemAdmissaoFactory, FuncionarioFactory
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
    UserFunctionPermissionFactory(user=rh, function="admissao", can_view=True, can_edit=True)
    return rh


def test_rh_lista_funcionarios():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    FuncionarioFactory(company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/funcionarios/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 1


def test_isolamento_multi_tenant_funcionarios():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    FuncionarioFactory(company_id=company_b)

    resposta = client_interno(rh_a, company_a).get("/v1/funcionarios/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 0


def test_permissao_negada_sem_rbac_funcionarios():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/funcionarios/")

    assert resposta.status_code == 403


def test_gestor_ve_funcionario_de_qualquer_area():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, area="Tecnologia", company_id=company_id)
    UserFunctionPermissionFactory(user=gestor, function="admissao", can_view=True)

    vaga_tecnologia = VagaFactory(company_id=company_id, area_solicitante="Tecnologia")
    vaga_financeiro = VagaFactory(company_id=company_id, area_solicitante="Financeiro")
    processo_tecnologia = ProcessoSeletivoFactory(company_id=company_id, vaga=vaga_tecnologia)
    processo_financeiro = ProcessoSeletivoFactory(company_id=company_id, vaga=vaga_financeiro)
    FuncionarioFactory(company_id=company_id, processo=processo_tecnologia, vaga=vaga_tecnologia)
    FuncionarioFactory(company_id=company_id, processo=processo_financeiro, vaga=vaga_financeiro)

    resposta = client_interno(gestor, company_id).get("/v1/funcionarios/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 2


def test_permissao_negada_sem_rbac_checklist():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/checklist-admissao/")

    assert resposta.status_code == 403


def test_isolamento_multi_tenant_checklist():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    ChecklistItemAdmissaoFactory(company_id=company_b)

    resposta = client_interno(rh_a, company_a).get("/v1/checklist-admissao/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 0


def test_revisar_aprova_item_e_conclui_onboarding_quando_todos_aprovados():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    funcionario = FuncionarioFactory(company_id=company_id)
    # FuncionarioFactory não passa por criar_funcionario_para_processo, então
    # não vem com o checklist padrão de 5 itens — só existe o item criado
    # explicitamente abaixo, o que já isola o cenário sem precisar apagar nada.
    item = ChecklistItemAdmissaoFactory(
        company_id=company_id,
        funcionario=funcionario,
        nome_documento="RG",
        status=ChecklistItemAdmissao.Status.ENVIADO,
    )

    resposta = client_interno(rh, company_id).post(
        f"/v1/checklist-admissao/{item.id}/revisar/", {"status": "aprovado"}, format="json"
    )

    assert resposta.status_code == 200
    item.refresh_from_db()
    funcionario.refresh_from_db()
    assert item.status == ChecklistItemAdmissao.Status.APROVADO
    assert item.revisado_por_id == rh.id
    assert funcionario.status_onboarding == Funcionario.StatusOnboarding.CONCLUIDO


def test_revisar_um_item_mantem_em_analise_quando_outro_ainda_pendente():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    funcionario = FuncionarioFactory(company_id=company_id)
    item_enviado = ChecklistItemAdmissaoFactory(
        company_id=company_id, funcionario=funcionario, status=ChecklistItemAdmissao.Status.ENVIADO
    )
    ChecklistItemAdmissaoFactory(
        company_id=company_id,
        funcionario=funcionario,
        nome_documento="CPF",
        status=ChecklistItemAdmissao.Status.PENDENTE,
    )

    resposta = client_interno(rh, company_id).post(
        f"/v1/checklist-admissao/{item_enviado.id}/revisar/", {"status": "aprovado"}, format="json"
    )

    assert resposta.status_code == 200
    funcionario.refresh_from_db()
    assert funcionario.status_onboarding == Funcionario.StatusOnboarding.EM_ANALISE
