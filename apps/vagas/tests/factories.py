import factory

from apps.core.models import User
from apps.core.tests.factories import UserFactory
from apps.vagas.models import Vaga


class VagaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vaga

    cargo = factory.Faker("job")
    descricao = factory.Faker("paragraph")
    requisitos = factory.Faker("paragraph")
    area_solicitante = "Tecnologia"
    tipo = Vaga.Tipo.EXTERNA
    solicitante = factory.SubFactory(UserFactory, role=User.Role.GESTOR)
    company_id = factory.SelfAttribute("solicitante.company_id")
