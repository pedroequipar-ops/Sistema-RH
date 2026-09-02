from rest_framework import serializers

from apps.candidatos.models import Candidato
from apps.candidatos.services import processar_upload_curriculo
from apps.processos_seletivos.models import ProcessoSeletivo
from apps.vagas.models import Vaga
from utils.storage import MinioStorage


class CandidatoSerializer(serializers.ModelSerializer):
    """Visão do banco de talentos, usada pelo RH/Gestor (RBAC via
    HasFunctionPermission, function='candidatos')."""

    curriculo_url = serializers.SerializerMethodField()

    class Meta:
        model = Candidato
        fields = [
            "id",
            "email",
            "nome",
            "telefone",
            "cidade",
            "cargo_pretendido",
            "senioridade",
            "skills",
            "resumo_experiencia",
            "curriculo_status",
            "curriculo_url",
            "created_at",
            "updated_at",
            "active",
        ]
        read_only_fields = [
            "id",
            "email",
            "resumo_experiencia",
            "curriculo_status",
            "curriculo_url",
            "created_at",
            "updated_at",
            "active",
        ]

    def get_curriculo_url(self, obj):
        if not obj.curriculo_key:
            return None
        return MinioStorage().generate_presigned_url(obj.curriculo_bucket, obj.curriculo_key)


class CandidatoMeSerializer(serializers.ModelSerializer):
    """Visão do próprio candidato no portal — mesma forma, mas o candidato
    pode editar seus próprios dados de perfil."""

    curriculo_url = serializers.SerializerMethodField()

    class Meta:
        model = Candidato
        fields = [
            "id",
            "email",
            "nome",
            "telefone",
            "cidade",
            "cargo_pretendido",
            "senioridade",
            "skills",
            "resumo_experiencia",
            "curriculo_status",
            "curriculo_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email",
            "resumo_experiencia",
            "curriculo_status",
            "curriculo_url",
            "created_at",
            "updated_at",
        ]

    def get_curriculo_url(self, obj):
        if not obj.curriculo_key:
            return None
        return MinioStorage().generate_presigned_url(obj.curriculo_bucket, obj.curriculo_key)


class CandidatoCadastroSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    nome = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def create(self, validated_data):
        company_id = self.context["company_id"]
        email = validated_data["email"]
        senha = validated_data["password"]
        nome = validated_data.get("nome", "")

        candidato, criado = Candidato.objects.get_or_create(
            company_id=company_id, email=email, defaults={"nome": nome}
        )
        if not criado and candidato.password:
            raise serializers.ValidationError({"email": "E-mail já cadastrado. Faça login."})
        if not criado and nome:
            candidato.nome = nome
        candidato.set_password(senha)
        candidato.save()
        return candidato


class ProcessoSeletivoResumoSerializer(serializers.ModelSerializer):
    vaga_cargo = serializers.CharField(source="vaga.cargo", read_only=True)
    vaga_area = serializers.CharField(source="vaga.area_solicitante", read_only=True)

    class Meta:
        model = ProcessoSeletivo
        fields = ["id", "vaga", "vaga_cargo", "vaga_area", "etapa_atual", "created_at"]
        read_only_fields = fields


class VagaPublicaSerializer(serializers.ModelSerializer):
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
            "created_at",
        ]
        read_only_fields = fields


class CandidaturaPublicaSerializer(serializers.Serializer):
    vaga_id = serializers.UUIDField()
    email = serializers.EmailField()
    nome = serializers.CharField(max_length=150)
    telefone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    cidade = serializers.CharField(max_length=100, required=False, allow_blank=True)
    cargo_pretendido = serializers.CharField(max_length=150, required=False, allow_blank=True)
    senioridade = serializers.ChoiceField(
        choices=Candidato.Senioridade.choices, required=False, allow_blank=True
    )
    skills = serializers.ListField(
        child=serializers.CharField(max_length=50), required=False, default=list
    )
    curriculo = serializers.FileField(required=False)

    def validate_vaga_id(self, value):
        company_id = self.context["company_id"]
        try:
            return Vaga.objects.get(id=value, company_id=company_id, status=Vaga.Status.ABERTA)
        except Vaga.DoesNotExist:
            raise serializers.ValidationError("Vaga não encontrada ou não está mais aberta.")

    def create(self, validated_data):
        company_id = self.context["company_id"]
        vaga = validated_data.pop("vaga_id")
        arquivo = validated_data.pop("curriculo", None)
        email = validated_data.pop("email")
        skills = [s.lower() for s in validated_data.pop("skills", [])]
        dados_candidato = {**validated_data, "skills": skills}

        candidato, criado = Candidato.objects.get_or_create(
            company_id=company_id, email=email, defaults=dados_candidato
        )
        if not criado:
            for campo, valor in dados_candidato.items():
                if valor:
                    setattr(candidato, campo, valor)
            candidato.save()

        processo, processo_criado = ProcessoSeletivo.objects.get_or_create(
            company_id=company_id,
            candidato=candidato,
            vaga=vaga,
            defaults={"etapa_atual": ProcessoSeletivo.Etapa.TRIAGEM},
        )
        if not processo_criado:
            raise serializers.ValidationError({"vaga_id": "Você já se candidatou a esta vaga."})

        if arquivo:
            processar_upload_curriculo(candidato, arquivo)

        return processo
