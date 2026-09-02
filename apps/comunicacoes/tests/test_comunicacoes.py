import uuid

import pytest
from rest_framework.test import APIClient

from apps.comunicacoes.models import Notificacao
from apps.comunicacoes.tests.factories import EmailEnviadoFactory, NotificacaoFactory
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
    UserFunctionPermissionFactory(user=rh, function="comunicacoes", can_view=True)
    return rh


def test_rh_lista_emails_enviados():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    EmailEnviadoFactory(company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/emails-enviados/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 1


def test_isolamento_multi_tenant_emails():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = rh_com_permissao(company_a)
    EmailEnviadoFactory(company_id=company_b)

    resposta = client_interno(rh_a, company_a).get("/v1/emails-enviados/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 0


def test_permissao_negada_sem_rbac_emails():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/emails-enviados/")

    assert resposta.status_code == 403


def test_gestor_so_ve_emails_de_candidatos_da_propria_area():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, area="Tecnologia", company_id=company_id)
    UserFunctionPermissionFactory(user=gestor, function="comunicacoes", can_view=True)

    vaga_tecnologia = VagaFactory(company_id=company_id, area_solicitante="Tecnologia")
    vaga_financeiro = VagaFactory(company_id=company_id, area_solicitante="Financeiro")
    processo_tecnologia = ProcessoSeletivoFactory(company_id=company_id, vaga=vaga_tecnologia)
    processo_financeiro = ProcessoSeletivoFactory(company_id=company_id, vaga=vaga_financeiro)
    EmailEnviadoFactory(company_id=company_id, processo=processo_tecnologia)
    EmailEnviadoFactory(company_id=company_id, processo=processo_financeiro)

    resposta = client_interno(gestor, company_id).get("/v1/emails-enviados/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 1


def test_usuario_so_ve_as_proprias_notificacoes():
    company_id = uuid.uuid4()
    rh_a = rh_com_permissao(company_id)
    rh_b = UserFactory(role=User.Role.RH, company_id=company_id)
    UserFunctionPermissionFactory(user=rh_b, function="comunicacoes", can_view=True)
    NotificacaoFactory(company_id=company_id, destinatario=rh_a)
    NotificacaoFactory(company_id=company_id, destinatario=rh_b)

    resposta = client_interno(rh_a, company_id).get("/v1/notificacoes/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 1


def test_permissao_negada_sem_rbac_notificacoes():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/notificacoes/")

    assert resposta.status_code == 403


def test_marcar_notificacao_como_lida():
    company_id = uuid.uuid4()
    rh = rh_com_permissao(company_id)
    notificacao = NotificacaoFactory(company_id=company_id, destinatario=rh)

    resposta = client_interno(rh, company_id).post(
        f"/v1/notificacoes/{notificacao.id}/marcar_lida/", {}, format="json"
    )

    assert resposta.status_code == 200
    notificacao.refresh_from_db()
    assert notificacao.lida is True


def test_nao_marca_notificacao_de_outro_usuario_como_lida():
    company_id = uuid.uuid4()
    rh_a = rh_com_permissao(company_id)
    rh_b = UserFactory(role=User.Role.RH, company_id=company_id)
    UserFunctionPermissionFactory(user=rh_b, function="comunicacoes", can_view=True)
    notificacao_de_b = NotificacaoFactory(company_id=company_id, destinatario=rh_b)

    resposta = client_interno(rh_a, company_id).post(
        f"/v1/notificacoes/{notificacao_de_b.id}/marcar_lida/", {}, format="json"
    )

    assert resposta.status_code == 404
    assert Notificacao.objects.get(id=notificacao_de_b.id).lida is False
