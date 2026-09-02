import uuid

import pytest
from rest_framework.test import APIClient

from apps.core.models import User
from apps.core.tests.factories import UserFactory, UserFunctionPermissionFactory
from apps.vagas.models import Vaga
from apps.vagas.tests.factories import VagaFactory

pytestmark = pytest.mark.django_db


def auth_client(user, company_id):
    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def test_gestor_cria_vaga_forca_area_e_entra_em_aguardando_rh():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, area="Tecnologia", company_id=company_id)
    UserFunctionPermissionFactory(user=gestor, function="vagas", can_create=True)
    client = auth_client(gestor, company_id)

    payload = {
        "cargo": "Dev Backend",
        "descricao": "desc",
        "requisitos": "req",
        "area_solicitante": "Financeiro",  # deve ser ignorado e forçado pra área do gestor
        "tipo": "externa",
    }
    response = client.post("/v1/vagas/", payload, format="json")

    assert response.status_code == 201
    vaga = Vaga.objects.get(id=response.data["id"])
    assert vaga.area_solicitante == "Tecnologia"
    assert vaga.solicitante_id == gestor.id
    assert vaga.status_aprovacao == Vaga.StatusAprovacao.AGUARDANDO_RH
    assert vaga.status == Vaga.Status.PAUSADA
    assert vaga.historico_status.count() == 1


def test_fluxo_aprovacao_completo_rh_depois_diretoria():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, area="Tecnologia", company_id=company_id)
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    diretoria = UserFactory(role=User.Role.DIRETORIA, company_id=company_id)
    for user in (rh, diretoria):
        UserFunctionPermissionFactory(user=user, function="vagas", can_view=True, can_edit=True)

    vaga = VagaFactory(company_id=company_id, solicitante=gestor, area_solicitante="Tecnologia")

    resposta_rh = auth_client(rh, company_id).post(
        f"/v1/vagas/{vaga.id}/aprovar/", {}, format="json"
    )
    assert resposta_rh.status_code == 200
    vaga.refresh_from_db()
    assert vaga.status_aprovacao == Vaga.StatusAprovacao.AGUARDANDO_DIRETORIA
    assert vaga.status == Vaga.Status.PAUSADA

    resposta_diretoria = auth_client(diretoria, company_id).post(
        f"/v1/vagas/{vaga.id}/aprovar/", {}, format="json"
    )
    assert resposta_diretoria.status_code == 200
    vaga.refresh_from_db()
    assert vaga.status_aprovacao == Vaga.StatusAprovacao.APROVADA
    assert vaga.status == Vaga.Status.ABERTA
    assert vaga.historico_status.count() == 3  # RH + (aprovação diretoria + operacional)


def test_reprovar_na_etapa_rh_cancela_vaga():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    UserFunctionPermissionFactory(user=rh, function="vagas", can_view=True, can_edit=True)
    vaga = VagaFactory(company_id=company_id, area_solicitante="Tecnologia")

    response = auth_client(rh, company_id).post(
        f"/v1/vagas/{vaga.id}/reprovar/", {"observacao": "Fora do orçamento"}, format="json"
    )

    assert response.status_code == 200
    vaga.refresh_from_db()
    assert vaga.status_aprovacao == Vaga.StatusAprovacao.REPROVADA
    assert vaga.status == Vaga.Status.CANCELADA


def test_gestor_nao_pode_aprovar_propria_vaga():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, area="Tecnologia", company_id=company_id)
    UserFunctionPermissionFactory(user=gestor, function="vagas", can_view=True, can_edit=True)
    vaga = VagaFactory(company_id=company_id, solicitante=gestor, area_solicitante="Tecnologia")

    response = auth_client(gestor, company_id).post(
        f"/v1/vagas/{vaga.id}/aprovar/", {}, format="json"
    )

    assert response.status_code == 403


def test_gestor_so_ve_vagas_da_propria_area():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, area="Tecnologia", company_id=company_id)
    UserFunctionPermissionFactory(user=gestor, function="vagas", can_view=True)
    VagaFactory(company_id=company_id, area_solicitante="Tecnologia")
    VagaFactory(company_id=company_id, area_solicitante="Financeiro")

    response = auth_client(gestor, company_id).get("/v1/vagas/")

    assert response.status_code == 200
    assert response.data["count"] == 1


def test_isolamento_multi_tenant():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    rh_a = UserFactory(role=User.Role.RH, company_id=company_a)
    UserFunctionPermissionFactory(user=rh_a, function="vagas", can_view=True)
    VagaFactory(company_id=company_b, area_solicitante="Outra empresa")

    response = auth_client(rh_a, company_a).get("/v1/vagas/")

    assert response.status_code == 200
    assert response.data["count"] == 0


def test_permissao_negada_sem_rbac():
    company_id = uuid.uuid4()
    user = UserFactory(role=User.Role.RH, company_id=company_id)
    # nenhum UserFunctionPermission criado para este usuário

    response = auth_client(user, company_id).get("/v1/vagas/")

    assert response.status_code == 403


def test_destroy_faz_soft_delete():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    UserFunctionPermissionFactory(user=rh, function="vagas", can_view=True, can_delete=True)
    vaga = VagaFactory(company_id=company_id, area_solicitante="Tecnologia")

    response = auth_client(rh, company_id).delete(f"/v1/vagas/{vaga.id}/")

    assert response.status_code == 204
    assert not Vaga.objects.filter(id=vaga.id).exists()
    assert Vaga.all_objects.filter(id=vaga.id, active=False).exists()
