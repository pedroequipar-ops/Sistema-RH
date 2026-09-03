import factory

from apps.core.models import Perfil, User, UserFunctionPermission


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.Faker("name")
    role = User.Role.RH
    area = ""
    company_id = factory.Faker("uuid4")
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "Teste123!")
        if create:
            self.save()


class UserFunctionPermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserFunctionPermission

    user = factory.SubFactory(UserFactory)
    function = "vagas"
    can_view = False
    can_create = False
    can_edit = False
    can_delete = False

    @factory.lazy_attribute
    def company_id(self):
        return self.user.company_id


class PerfilFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Perfil

    nome = factory.Sequence(lambda n: f"Perfil {n}")
    slug = factory.Sequence(lambda n: f"perfil-{n}")
    descricao = ""
    tipo = Perfil.Tipo.PERSONALIZADO
    ativo = True
    company_id = factory.Faker("uuid4")
