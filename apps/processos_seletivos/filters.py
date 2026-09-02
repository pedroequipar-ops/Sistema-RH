import django_filters

from apps.processos_seletivos.models import ProcessoSeletivo


class ProcessoSeletivoFilter(django_filters.FilterSet):
    class Meta:
        model = ProcessoSeletivo
        fields = ["etapa_atual", "vaga", "candidato"]
