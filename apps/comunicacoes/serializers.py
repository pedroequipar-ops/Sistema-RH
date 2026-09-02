from rest_framework import serializers

from apps.comunicacoes.models import EmailEnviado, Notificacao


class EmailEnviadoSerializer(serializers.ModelSerializer):
    candidato_nome = serializers.CharField(source="candidato.nome", read_only=True, default=None)

    class Meta:
        model = EmailEnviado
        fields = [
            "id",
            "tipo",
            "destinatario",
            "assunto",
            "candidato",
            "candidato_nome",
            "processo",
            "status",
            "erro",
            "created_at",
        ]
        read_only_fields = fields


class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = ["id", "tipo", "mensagem", "lida", "processo", "dados", "created_at"]
        read_only_fields = fields
