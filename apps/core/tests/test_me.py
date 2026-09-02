import uuid

import pytest
from rest_framework.test import APIClient

from apps.core.models import User
from apps.core.tests.factories import UserFactory, UserFunctionPermissionFactory

pytestmark = pytest.mark.django_db


def test_me_retorna_perfil_e_permissoes_do_usuario_autenticado():
    company_id = uuid.uuid4()
    user = UserFactory(role=User.Role.RH, company_id=company_id, full_name="Ana RH")
    UserFunctionPermissionFactory(user=user, function="vagas", can_view=True, can_create=True)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/v1/auth/me/")

    assert response.status_code == 200
    assert response.data["email"] == user.email
    assert response.data["full_name"] == "Ana RH"
    assert str(response.data["company_id"]) == str(company_id)
    assert response.data["function_permissions"][0]["function"] == "vagas"
    assert response.data["function_permissions"][0]["can_create"] is True


def test_me_sem_autenticacao_retorna_401():
    client = APIClient()

    response = client.get("/v1/auth/me/")

    assert response.status_code == 401
