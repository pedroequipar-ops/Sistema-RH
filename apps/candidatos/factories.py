import factory

from apps.candidatos.models import Candidato


class CandidatoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Candidato
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"candidato{n}@example.com")
    nome = factory.Faker("name")
    cidade = "São Paulo"
    cargo_pretendido = "Desenvolvedor"
    senioridade = Candidato.Senioridade.PLENO
    skills = factory.LazyFunction(lambda: ["python", "django"])
    company_id = factory.Faker("uuid4")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "Teste123!")
        if create:
            self.save()
