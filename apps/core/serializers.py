from rest_framework import serializers

from apps.core.models import Perfil, PerfilFunctionPermission, User, UserFunctionPermission
from utils.utils import capture_company_id


class UserFunctionPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFunctionPermission
        fields = ["function", "can_view", "can_create", "can_edit", "can_delete"]


class UserMeSerializer(serializers.ModelSerializer):
    function_permissions = UserFunctionPermissionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "role",
            "area",
            "company_id",
            "is_superuser",
            "function_permissions",
        ]


class PerfilFunctionPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilFunctionPermission
        fields = ["function", "can_view", "can_create", "can_edit", "can_delete"]


class PerfilFunctionPermissionWriteSerializer(serializers.Serializer):
    function = serializers.SlugField()
    can_view = serializers.BooleanField(default=False)
    can_create = serializers.BooleanField(default=False)
    can_edit = serializers.BooleanField(default=False)
    can_delete = serializers.BooleanField(default=False)


class PerfilSerializer(serializers.ModelSerializer):
    """Perfil de acesso — listagem/detalhe. 'slug' e 'tipo' nunca são
    editáveis por aqui; 'ativo' pode ser alternado por PATCH desde que o
    perfil não seja do tipo sistema (ver PerfilViewSet.perform_update)."""

    function_permissions = PerfilFunctionPermissionSerializer(many=True, read_only=True)
    usuarios_count = serializers.SerializerMethodField()

    class Meta:
        model = Perfil
        fields = [
            "id",
            "nome",
            "slug",
            "descricao",
            "tipo",
            "ativo",
            "usuarios_count",
            "function_permissions",
        ]
        read_only_fields = ["slug", "tipo"]

    def get_usuarios_count(self, obj):
        return obj.usuarios.filter(active=True).count()


class PerfilCreateSerializer(serializers.ModelSerializer):
    """Todo perfil novo nasce tipo 'personalizado' — 'sistema' é reservado
    para o Administrador criado pela migração, nunca por esta tela."""

    class Meta:
        model = Perfil
        fields = ["id", "nome", "descricao"]


class UserGerenciamentoSerializer(serializers.ModelSerializer):
    """Painel de Usuários (exclusivo do Gestor): o Gestor escolhe um Perfil
    já existente para cada conta RH. As permissões efetivas (RBAC real, lidas
    por HasFunctionPermission) são sincronizadas para UserFunctionPermission
    por UsuarioGerenciamentoViewSet sempre que o perfil muda — ver
    Perfil.aplicar_a."""

    perfil_nome = serializers.CharField(source="perfil.nome", read_only=True, default=None)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "area", "perfil", "perfil_nome", "is_active"]

    def validate_perfil(self, perfil):
        if perfil is None:
            return perfil
        company_id = capture_company_id(self.context["request"])
        if str(perfil.company_id) != str(company_id):
            raise serializers.ValidationError("Perfil inválido.")
        return perfil


class CriarUsuarioSerializer(serializers.ModelSerializer):
    """Sempre cria papel RH, sem perfil — o Gestor atribui um perfil depois
    na lista de usuários; 'role' nem é aceito aqui."""

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "area", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
