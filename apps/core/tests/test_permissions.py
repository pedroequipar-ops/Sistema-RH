from types import SimpleNamespace

import pytest
from django.core.exceptions import ImproperlyConfigured

from apps.core.models import User
from apps.core.permissions import HasFunctionPermission
from apps.core.tests.factories import UserFactory, UserFunctionPermissionFactory

pytestmark = pytest.mark.django_db


def _fake_view(**kwargs):
    return SimpleNamespace(**kwargs)


def _fake_request(user):
    return SimpleNamespace(user=user)


def test_usuario_nao_autenticado_retorna_false():
    request = _fake_request(user=None)
    view = _fake_view(permission_path="vagas", permission_action_map={}, action="list")

    assert HasFunctionPermission().has_permission(request, view) is False


def test_superuser_bypassa_mesmo_sem_view_configurada():
    superuser = UserFactory(is_superuser=True)
    request = _fake_request(user=superuser)
    view = _fake_view(action="list")  # sem permission_path nem permission_action_map

    assert HasFunctionPermission().has_permission(request, view) is True


def test_view_sem_permission_path_levanta_improperly_configured():
    user = UserFactory(role=User.Role.RH)
    request = _fake_request(user=user)
    view = _fake_view(action="list")  # sem permission_path/permission_action_map

    with pytest.raises(ImproperlyConfigured):
        HasFunctionPermission().has_permission(request, view)


def test_acao_nao_mapeada_retorna_false():
    user = UserFactory(role=User.Role.RH)
    UserFunctionPermissionFactory(user=user, function="vagas", can_view=True)
    request = _fake_request(user=user)
    view = _fake_view(
        permission_path="vagas", permission_action_map={"list": "view"}, action="destroy"
    )

    assert HasFunctionPermission().has_permission(request, view) is False


def test_acao_de_permissao_desconhecida_levanta_improperly_configured():
    user = UserFactory(role=User.Role.RH)
    request = _fake_request(user=user)
    view = _fake_view(
        permission_path="vagas", permission_action_map={"list": "voar"}, action="list"
    )

    with pytest.raises(ImproperlyConfigured):
        HasFunctionPermission().has_permission(request, view)


def test_usuario_com_permissao_concedida_passa():
    user = UserFactory(role=User.Role.RH)
    UserFunctionPermissionFactory(user=user, function="vagas", can_view=True)
    request = _fake_request(user=user)
    view = _fake_view(
        permission_path="vagas", permission_action_map={"list": "view"}, action="list"
    )

    assert HasFunctionPermission().has_permission(request, view) is True
