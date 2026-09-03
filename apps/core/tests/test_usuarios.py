import uuid

import pytest
from rest_framework.test import APIClient

from apps.core.models import User, UserFunctionPermission
from apps.core.tests.factories import PerfilFactory, UserFactory, UserFunctionPermissionFactory

pytestmark = pytest.mark.django_db


def client_interno(user, company_id):
    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def test_gestor_lista_apenas_rh_da_propria_company():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    UserFactory(role=User.Role.RH, company_id=company_id)
    UserFactory(role=User.Role.RH, company_id=uuid.uuid4())  # outra empresa

    resposta = client_interno(gestor, company_id).get("/v1/usuarios/")

    assert resposta.status_code == 200
    # o próprio Gestor nunca aparece na lista que ele mesmo gerencia, e o RH
    # de outra empresa não é visível (isolamento multi-tenant)
    assert resposta.data["count"] == 1


def test_rh_nao_acessa_painel_de_usuarios():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/usuarios/")

    assert resposta.status_code == 403


def test_gestor_cria_novo_usuario():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)

    payload = {"email": "novo.rh@systen.com", "full_name": "Novo RH", "password": "123456"}
    resposta = client_interno(gestor, company_id).post("/v1/usuarios/", payload, format="json")

    assert resposta.status_code == 201
    novo = User.objects.get(email="novo.rh@systen.com")
    assert novo.full_name == "Novo RH"
    assert novo.role == User.Role.RH
    assert novo.perfil_id is None
    assert str(novo.company_id) == str(company_id)
    assert novo.check_password("123456")


def test_criar_usuario_ignora_role_enviado_e_forca_rh():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)

    payload = {
        "email": "tentativa.gestor@systen.com",
        "full_name": "Tentativa",
        "role": "gestor",
        "password": "123456",
    }
    resposta = client_interno(gestor, company_id).post("/v1/usuarios/", payload, format="json")

    assert resposta.status_code == 201
    novo = User.objects.get(email="tentativa.gestor@systen.com")
    assert novo.role == User.Role.RH


def test_criar_usuario_nao_aceita_senha_curta():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)

    payload = {"email": "x@systen.com", "full_name": "X", "password": "123"}
    resposta = client_interno(gestor, company_id).post("/v1/usuarios/", payload, format="json")

    assert resposta.status_code == 400


def test_gestor_atribui_perfil_e_sincroniza_permissoes_do_usuario():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    perfil = PerfilFactory(company_id=company_id)
    perfil.function_permissions.create(function="vagas", can_view=True, can_create=True)
    perfil.function_permissions.create(function="candidatos", can_view=True)

    resposta = client_interno(gestor, company_id).patch(
        f"/v1/usuarios/{rh.id}/", {"perfil": str(perfil.id)}, format="json"
    )

    assert resposta.status_code == 200
    assert resposta.data["perfil_nome"] == perfil.nome
    permissoes = {p.function: p for p in UserFunctionPermission.objects.filter(user=rh)}
    assert permissoes["vagas"].can_view is True
    assert permissoes["vagas"].can_create is True
    assert permissoes["candidatos"].can_view is True


def test_trocar_perfil_sobrescreve_permissoes_do_perfil_anterior():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    perfil_a = PerfilFactory(company_id=company_id)
    perfil_a.function_permissions.create(function="vagas", can_view=True, can_delete=True)
    perfil_b = PerfilFactory(company_id=company_id)
    perfil_b.function_permissions.create(function="vagas", can_view=True, can_delete=False)

    client = client_interno(gestor, company_id)
    client.patch(f"/v1/usuarios/{rh.id}/", {"perfil": str(perfil_a.id)}, format="json")
    client.patch(f"/v1/usuarios/{rh.id}/", {"perfil": str(perfil_b.id)}, format="json")

    permissao = UserFunctionPermission.objects.get(user=rh, function="vagas")
    assert permissao.can_delete is False


def test_remover_perfil_do_usuario_zera_permissoes():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    UserFunctionPermissionFactory(user=rh, function="vagas", can_view=True)

    resposta = client_interno(gestor, company_id).patch(
        f"/v1/usuarios/{rh.id}/", {"perfil": None}, format="json"
    )

    assert resposta.status_code == 200
    permissao = UserFunctionPermission.objects.get(user=rh, function="vagas")
    assert permissao.can_view is False


def test_gestor_nao_atribui_perfil_de_outra_company():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    rh = UserFactory(role=User.Role.RH, company_id=company_id)
    perfil_de_outra_empresa = PerfilFactory(company_id=uuid.uuid4())

    resposta = client_interno(gestor, company_id).patch(
        f"/v1/usuarios/{rh.id}/", {"perfil": str(perfil_de_outra_empresa.id)}, format="json"
    )

    assert resposta.status_code == 400


def test_rh_nao_atribui_perfil():
    company_id = uuid.uuid4()
    rh_a = UserFactory(role=User.Role.RH, company_id=company_id)
    rh_b = UserFactory(role=User.Role.RH, company_id=company_id)
    perfil = PerfilFactory(company_id=company_id)

    resposta = client_interno(rh_a, company_id).patch(
        f"/v1/usuarios/{rh_b.id}/", {"perfil": str(perfil.id)}, format="json"
    )

    assert resposta.status_code == 403


def test_gestor_desativa_usuario():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(gestor, company_id).patch(
        f"/v1/usuarios/{rh.id}/", {"is_active": False}, format="json"
    )

    assert resposta.status_code == 200
    rh.refresh_from_db()
    assert rh.is_active is False


def test_gestor_exclui_usuario_soft_delete():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(gestor, company_id).delete(f"/v1/usuarios/{rh.id}/")

    assert resposta.status_code == 204
    rh.refresh_from_db()
    assert rh.active is False


def test_isolamento_multi_tenant_usuarios():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    gestor_a = UserFactory(role=User.Role.GESTOR, company_id=company_a)
    rh_b = UserFactory(role=User.Role.RH, company_id=company_b)

    resposta = client_interno(gestor_a, company_a).patch(
        f"/v1/usuarios/{rh_b.id}/", {"is_active": False}, format="json"
    )

    assert resposta.status_code == 404
