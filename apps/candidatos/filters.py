import django_filters

from apps.candidatos.models import Candidato


class CandidatoFilter(django_filters.FilterSet):
    skill = django_filters.CharFilter(method="filter_skill")
    cidade = django_filters.CharFilter(lookup_expr="icontains")
    cargo_pretendido = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Candidato
        fields = ["cidade", "cargo_pretendido", "senioridade"]

    def filter_skill(self, queryset, name, value):
        return queryset.filter(skills__contains=[value.strip().lower()])
