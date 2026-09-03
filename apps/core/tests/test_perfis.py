import uuid

import pytest
from rest_framework.test import APIClient

from apps.core.models import Perfil, User, UserFunctionPermission
from apps.core.tests.factories import PerfilFactory, UserFactory

pytestmark = pytest.mark.django_db


def client_interno(user, company_id):
    client = APIClient()
    client.force_authenticate(user=user)
    client.credentials(HTTP_X_COMPANY_ID=str(company_id))
    return client


def test_gestor_lista_perfis_da_propria_company():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    PerfilFactory(company_id=company_id)
    PerfilFactory(company_id=uuid.uuid4())  # outra empresa

    resposta = client_interno(gestor, company_id).get("/v1/perfis/")

    assert resposta.status_code == 200
    assert resposta.data["count"] == 1


def test_rh_nao_acessa_perfis():
    company_id = uuid.uuid4()
    rh = UserFactory(role=User.Role.RH, company_id=company_id)

    resposta = client_interno(rh, company_id).get("/v1/perfis/")

    assert resposta.status_code == 403


def test_gestor_cria_perfil_com_modulos_zerados():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)

    payload = {"nome": "Recrutador", "descricao": "Só enxerga vagas e candidatos."}
    resposta = client_interno(gestor, company_id).post("/v1/perfis/", payload, format="json")

    assert resposta.status_code == 201
    perfil = Perfil.objects.get(company_id=company_id, nome="Recrutador")
    assert perfil.slug == "recrutador"
    assert perfil.tipo == Perfil.Tipo.PERSONALIZADO
    assert perfil.function_permissions.count() == 6
    assert not perfil.function_permissions.filter(can_view=True).exists()


def test_nao_cria_dois_perfis_com_mesmo_nome_na_company():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    PerfilFactory(company_id=company_id, nome="Recrutador", slug="recrutador")

    resposta = client_interno(gestor, company_id).post(
        "/v1/perfis/", {"nome": "Recrutador", "descricao": ""}, format="json"
    )

    assert resposta.status_code == 400


def test_gestor_edita_permissoes_do_perfil_e_sincroniza_usuarios():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    perfil = PerfilFactory(company_id=company_id)
    membro = UserFactory(role=User.Role.RH, company_id=company_id, perfil=perfil)

    payload = [
        {"function": "vagas", "can_view": True, "can_create": True},
        {"function": "candidatos", "can_view": True},
    ]
    resposta = client_interno(gestor, company_id).put(
        f"/v1/perfis/{perfil.id}/permissoes/", payload, format="json"
    )

    assert resposta.status_code == 200
    permissoes = {p.function: p for p in UserFunctionPermission.objects.filter(user=membro)}
    assert permissoes["vagas"].can_view is True
    assert permissoes["vagas"].can_create is True
    assert permissoes["candidatos"].can_view is True


def test_perfil_sistema_nao_pode_ser_editado():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    administrador = PerfilFactory(
        company_id=company_id, nome="Administrador", tipo=Perfil.Tipo.SISTEMA
    )

    resposta = client_interno(gestor, company_id).patch(
        f"/v1/perfis/{administrador.id}/", {"descricao": "tentativa"}, format="json"
    )

    assert resposta.status_code == 400


def test_perfil_sistema_nao_pode_ter_permissoes_editadas():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    administrador = PerfilFactory(
        company_id=company_id, nome="Administrador", tipo=Perfil.Tipo.SISTEMA
    )

    resposta = client_interno(gestor, company_id).put(
        f"/v1/perfis/{administrador.id}/permissoes/",
        [{"function": "vagas", "can_view": False}],
        format="json",
    )

    assert resposta.status_code == 400


def test_perfil_sistema_nao_pode_ser_excluido():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    administrador = PerfilFactory(
        company_id=company_id, nome="Administrador", tipo=Perfil.Tipo.SISTEMA
    )

    resposta = client_interno(gestor, company_id).delete(f"/v1/perfis/{administrador.id}/")

    assert resposta.status_code == 400
    assert Perfil.objects.filter(id=administrador.id, active=True).exists()


def test_nao_exclui_perfil_com_usuario_vinculado():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    perfil = PerfilFactory(company_id=company_id)
    UserFactory(role=User.Role.RH, company_id=company_id, perfil=perfil)

    resposta = client_interno(gestor, company_id).delete(f"/v1/perfis/{perfil.id}/")

    assert resposta.status_code == 400
    assert Perfil.objects.filter(id=perfil.id, active=True).exists()


def test_exclui_perfil_personalizado_sem_usuarios():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    perfil = PerfilFactory(company_id=company_id)

    resposta = client_interno(gestor, company_id).delete(f"/v1/perfis/{perfil.id}/")

    assert resposta.status_code == 204
    assert not Perfil.objects.filter(id=perfil.id, active=True).exists()


def test_duplicar_perfil_copia_permissoes_como_personalizado():
    company_id = uuid.uuid4()
    gestor = UserFactory(role=User.Role.GESTOR, company_id=company_id)
    original = PerfilFactory(company_id=company_id, nome="Recrutador")
    original.function_permissions.create(function="vagas", can_view=True, can_create=True)

    resposta = client_interno(gestor, company_id).post(f"/v1/perfis/{original.id}/duplicar/")

    assert resposta.status_code == 201
    copia = Perfil.objects.get(id=resposta.data["id"])
    assert copia.nome == "Recrutador (cópia)"
    assert copia.tipo == Perfil.Tipo.PERSONALIZADO
    assert copia.function_permissions.get(function="vagas").can_view is True


def test_isolamento_multi_tenant_perfis():
    company_a = uuid.uuid4()
    company_b = uuid.uuid4()
    gestor_a = UserFactory(role=User.Role.GESTOR, company_id=company_a)
    perfil_b = PerfilFactory(company_id=company_b)

    resposta = client_interno(gestor_a, company_a).delete(f"/v1/perfis/{perfil_b.id}/")

    assert resposta.status_code == 404
