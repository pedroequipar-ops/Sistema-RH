import uuid

import pytest
from rest_framework.test import APIClient

from apps.admissao.models import DOCUMENTOS_PADRAO_ADMISSAO, Funcionario
from apps.admissao.services import criar_funcionario_para_processo
from apps.core.models import User
from apps.core.tests.factories import UserFactory, UserFunctionPermissionFactory
from apps.processos_seletivos.tests.factories import ProcessoSeletivoFactory
from apps.vagas.models import Vaga
from apps.vagas.tests.factories import VagaFactory

pytestmark = pytest.mark.django_db


def client_interno(user, company_id):
    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def test_mover_processo_para_contratado_cria_funcionario_e_checklist_padrao():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    UserFunctionPermissionFactory(
        user=rh, function="processos-seletivos", can_view=True, can_edit=True
    )
    vaga = VagaFactory(company_id=company_id, status=Vaga.Status.ABERTA)
    processo = ProcessoSeletivoFactory(company_id=company_id, vaga=vaga)
    client = client_interno(rh, company_id)

    for etapa in ("teste", "entrevista", "proposta", "contratado"):
        resposta = client.post(
            f"/v1/processos-seletivos/{processo.id}/mover_etapa/", {"etapa": etapa}, format="json"
        )
        assert resposta.status_code == 200, resposta.data

    funcionario = Funcionario.objects.get(processo=processo)
    assert funcionario.candidato_id == processo.candidato_id
    assert funcionario.cargo == vaga.cargo
    assert funcionario.status_onboarding == Funcionario.StatusOnboarding.DOCUMENTOS_PENDENTES
    nomes_checklist = set(funcionario.checklist.values_list("nome_documento", flat=True))
    assert nomes_checklist == set(DOCUMENTOS_PADRAO_ADMISSAO)


def test_criar_funcionario_para_processo_e_idempotente():
    processo = ProcessoSeletivoFactory()

    primeiro = criar_funcionario_para_processo(processo)
    segundo = criar_funcionario_para_processo(processo)

    assert primeiro.id == segundo.id
    assert Funcionario.objects.filter(processo=processo).count() == 1
    assert primeiro.checklist.count() == len(DOCUMENTOS_PADRAO_ADMISSAO)
