from rest_framework import serializers


class TempoMedioContratacaoSerializer(serializers.Serializer):
    tempo_medio_dias = serializers.FloatField(allow_null=True)
    total_contratacoes = serializers.IntegerField()


class CandidatosPorVagaSerializer(serializers.Serializer):
    vaga_id = serializers.UUIDField()
    vaga_cargo = serializers.CharField()
    total_candidatos = serializers.IntegerField()


class FunilEtapaSerializer(serializers.Serializer):
    etapa = serializers.CharField()
    entraram = serializers.IntegerField()
    avancaram = serializers.IntegerField(allow_null=True)
    taxa_conversao = serializers.FloatField(allow_null=True)


class CustoContratacaoVagaSerializer(serializers.Serializer):
    vaga_id = serializers.UUIDField()
    cargo = serializers.CharField()
    custo_contratacao = serializers.DecimalField(max_digits=12, decimal_places=2)


class CustoContratacaoSerializer(serializers.Serializer):
    vagas = CustoContratacaoVagaSerializer(many=True)
    custo_medio = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    custo_total = serializers.DecimalField(max_digits=12, decimal_places=2)
