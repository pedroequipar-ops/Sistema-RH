import pytest

from apps.core.factories import UserFactory
from apps.core.models import User

pytestmark = pytest.mark.django_db


def test_delete_de_instancia_e_bloqueado():
    user = UserFactory()
    with pytest.raises(NotImplementedError):
        user.delete()


def test_delete_em_massa_via_queryset_e_bloqueado():
    UserFactory()
    with pytest.raises(NotImplementedError):
        User.objects.all().delete()


def test_soft_delete_marca_active_false_sem_remover_do_banco():
    user = UserFactory()
    user.soft_delete()

    assert not User.objects.filter(id=user.id).exists()
    assert User.all_objects.filter(id=user.id, active=False).exists()


def test_update_em_massa_continua_permitido():
    user = UserFactory()
    User.objects.filter(id=user.id).update(active=False)

    assert User.all_objects.get(id=user.id).active is False
