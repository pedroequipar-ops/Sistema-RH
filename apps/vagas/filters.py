import django_filters

from apps.vagas.models import Vaga


class VagaFilter(django_filters.FilterSet):
    class Meta:
        model = Vaga
        fields = {
            "status": ["exact"],
            "status_aprovacao": ["exact"],
            "tipo": ["exact"],
            "area_solicitante": ["exact", "icontains"],
        }
