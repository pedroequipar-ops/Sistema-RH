from rest_framework import serializers

from apps.processos_seletivos.models import (
    AvaliacaoProcesso,
    EntrevistaAgendamento,
    HistoricoEtapaProcesso,
    ProcessoSeletivo,
    TesteAplicado,
)


class HistoricoEtapaProcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoEtapaProcesso
        fields = ["id", "de_etapa", "para_etapa", "alterado_por", "observacao", "created_at"]
        read_only_fields = fields


class ProcessoSeletivoSerializer(serializers.ModelSerializer):
    candidato_nome = serializers.CharField(source="candidato.nome", read_only=True)
    candidato_email = serializers.CharField(source="candidato.email", read_only=True)
    vaga_cargo = serializers.CharField(source="vaga.cargo", read_only=True)
    historico_etapas = HistoricoEtapaProcessoSerializer(many=True, read_only=True)

    class Meta:
        model = ProcessoSeletivo
        fields = [
            "id",
            "candidato",
            "candidato_nome",
            "candidato_email",
            "vaga",
            "vaga_cargo",
            "etapa_atual",
            "historico_etapas",
            "created_at",
            "updated_at",
            "active",
        ]
        read_only_fields = [
            "id",
            "etapa_atual",
            "historico_etapas",
            "created_at",
            "updated_at",
            "active",
        ]


class MoverEtapaSerializer(serializers.Serializer):
    etapa = serializers.ChoiceField(choices=ProcessoSeletivo.Etapa.choices)
    observacao = serializers.CharField(required=False, allow_blank=True, default="")


class AvaliacaoProcessoSerializer(serializers.ModelSerializer):
    autor_nome = serializers.CharField(source="autor.full_name", read_only=True)

    class Meta:
        model = AvaliacaoProcesso
        fields = ["id", "processo", "autor", "autor_nome", "nota", "comentario", "created_at"]
        read_only_fields = ["id", "autor", "autor_nome", "created_at"]


class TesteAplicadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TesteAplicado
        fields = [
            "id",
            "processo",
            "tipo",
            "titulo",
            "perguntas",
            "respostas",
            "nota",
            "status",
            "criado_por",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "criado_por", "created_at", "updated_at"]


class AvaliarTesteSerializer(serializers.Serializer):
    respostas = serializers.JSONField(required=False)
    nota = serializers.DecimalField(max_digits=4, decimal_places=2, required=False, allow_null=True)


class EntrevistaAgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntrevistaAgendamento
        fields = [
            "id",
            "processo",
            "data_hora",
            "duracao_minutos",
            "local_ou_link",
            "observacoes",
            "criado_por",
            "created_at",
            "active",
        ]
        read_only_fields = ["id", "criado_por", "created_at", "active"]
