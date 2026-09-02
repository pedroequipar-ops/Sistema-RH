from rest_framework import serializers

from apps.vagas.models import HistoricoStatusVaga, Vaga


class HistoricoStatusVagaSerializer(serializers.ModelSerializer):
    alterado_por_nome = serializers.CharField(
        source="alterado_por.full_name", read_only=True, default=None
    )

    class Meta:
        model = HistoricoStatusVaga
        fields = [
            "id",
            "tipo_status",
            "de_status",
            "para_status",
            "alterado_por",
            "alterado_por_nome",
            "observacao",
            "created_at",
        ]
        read_only_fields = fields


class VagaSerializer(serializers.ModelSerializer):
    historico = HistoricoStatusVagaSerializer(source="historico_status", many=True, read_only=True)
    solicitante_nome = serializers.CharField(source="solicitante.full_name", read_only=True)

    class Meta:
        model = Vaga
        fields = [
            "id",
            "cargo",
            "descricao",
            "requisitos",
            "salario",
            "area_solicitante",
            "tipo",
            "status",
            "status_aprovacao",
            "solicitante",
            "solicitante_nome",
            "custo_contratacao",
            "historico",
            "created_at",
            "updated_at",
            "active",
        ]
        read_only_fields = [
            "id",
            "status",
            "status_aprovacao",
            "solicitante",
            "historico",
            "created_at",
            "updated_at",
            "active",
        ]
