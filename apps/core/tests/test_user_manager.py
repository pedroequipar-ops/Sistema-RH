import uuid

import pytest

from apps.core.models import User, UserFunctionPermission
from apps.core.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_create_user_sem_email_levanta_erro():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="Teste123!", company_id=uuid.uuid4())


def test_create_superuser_com_is_staff_false_levanta_erro():
    with pytest.raises(ValueError):
        User.objects.create_superuser(email="admin@teste.com", password="Teste123!", is_staff=False)


def test_create_superuser_com_is_superuser_false_levanta_erro():
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email="admin@teste.com", password="Teste123!", is_superuser=False
        )


def test_create_superuser_cria_usuario_valido_com_defaults():
    user = User.objects.create_superuser(email="admin@teste.com", password="Teste123!")

    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.role == User.Role.RH
    assert user.company_id is not None


def test_user_has_perm_e_has_module_perms_refletem_is_superuser():
    superuser = UserFactory(is_superuser=True)
    usuario_comum = UserFactory(is_superuser=False)

    assert superuser.has_perm("qualquer.coisa") is True
    assert superuser.has_module_perms("qualquer_app") is True
    assert usuario_comum.has_perm("qualquer.coisa") is False
    assert usuario_comum.has_module_perms("qualquer_app") is False


def test_userfunctionpermission_herda_company_id_do_usuario_quando_omitido():
    company_id = uuid.uuid4()
    user = UserFactory(company_id=company_id)

    item = UserFunctionPermission(user=user, function="vagas", can_view=True)
    item.save()

    assert item.company_id == company_id
