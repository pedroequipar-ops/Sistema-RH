from rest_framework import serializers

from apps.admissao.models import ChecklistItemAdmissao, Funcionario
from utils.storage import MinioStorage


class ChecklistItemAdmissaoSerializer(serializers.ModelSerializer):
    documento_url = serializers.SerializerMethodField()

    class Meta:
        model = ChecklistItemAdmissao
        fields = [
            "id",
            "funcionario",
            "nome_documento",
            "obrigatorio",
            "status",
            "documento_url",
            "observacao",
            "revisado_por",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "funcionario",
            "nome_documento",
            "obrigatorio",
            "status",
            "documento_url",
            "revisado_por",
            "created_at",
            "updated_at",
        ]

    def get_documento_url(self, obj):
        if not obj.documento_key:
            return None
        return MinioStorage().generate_presigned_url(obj.documento_bucket, obj.documento_key)


class FuncionarioSerializer(serializers.ModelSerializer):
    candidato_nome = serializers.CharField(source="candidato.nome", read_only=True)
    checklist = ChecklistItemAdmissaoSerializer(many=True, read_only=True)

    class Meta:
        model = Funcionario
        fields = [
            "id",
            "processo",
            "candidato",
            "candidato_nome",
            "vaga",
            "cargo",
            "data_admissao",
            "status_onboarding",
            "checklist",
            "created_at",
            "updated_at",
            "active",
        ]
        read_only_fields = [
            "id",
            "processo",
            "candidato",
            "candidato_nome",
            "vaga",
            "cargo",
            "checklist",
            "created_at",
            "updated_at",
            "active",
        ]


class RevisarChecklistItemSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[ChecklistItemAdmissao.Status.APROVADO, ChecklistItemAdmissao.Status.REJEITADO]
    )
    observacao = serializers.CharField(required=False, allow_blank=True, default="")
