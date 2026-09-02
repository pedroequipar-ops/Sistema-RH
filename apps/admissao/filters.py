import django_filters

from apps.admissao.models import ChecklistItemAdmissao, Funcionario


class FuncionarioFilter(django_filters.FilterSet):
    class Meta:
        model = Funcionario
        fields = ["status_onboarding", "vaga", "candidato"]


class ChecklistItemAdmissaoFilter(django_filters.FilterSet):
    class Meta:
        model = ChecklistItemAdmissao
        fields = ["status", "funcionario"]
