from django.utils.text import slugify
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.models import MODULOS, Perfil, PerfilFunctionPermission, User, UserFunctionPermission
from apps.core.permissions import IsGestor
from apps.core.serializers import (
    CriarUsuarioSerializer,
    PerfilCreateSerializer,
    PerfilFunctionPermissionWriteSerializer,
    PerfilSerializer,
    UserGerenciamentoSerializer,
    UserMeSerializer,
)
from utils.utils import capture_company_id


class MeView(generics.RetrieveAPIView):
    """Perfil do usuário interno autenticado (RH/Gestor/Diretoria): dados
    básicos + company_id + permissões por função, usados pelo frontend para
    montar o menu e anexar o header X-Company-ID nas próximas requisições.
    """

    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UsuarioGerenciamentoViewSet(viewsets.ModelViewSet):
    """Painel de Usuários: listar/criar contas de RH e atribuir um Perfil de
    acesso já existente — exclusivo do papel Gestor (IsGestor, não
    HasFunctionPermission: ver o comentário na classe de permissão). O
    Gestor já tem acesso total ao sistema por papel, então nunca aparece na
    própria lista que ele gerencia — só a equipe de RH fica visível/editável
    aqui."""

    permission_classes = [IsGestor]
    http_method_names = ["get", "post", "patch", "put", "delete", "head", "options"]

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        return User.objects.filter(company_id=company_id, role=User.Role.RH).select_related(
            "perfil"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CriarUsuarioSerializer
        return UserGerenciamentoSerializer

    def perform_create(self, serializer):
        company_id = capture_company_id(self.request)
        serializer.save(company_id=company_id, role=User.Role.RH)

    def perform_update(self, serializer):
        usuario = serializer.save()
        if usuario.perfil_id:
            usuario.perfil.aplicar_a(usuario)
        else:
            UserFunctionPermission.objects.filter(user=usuario).update(
                can_view=False, can_create=False, can_edit=False, can_delete=False
            )

    def destroy(self, request, *args, **kwargs):
        usuario = self.get_object()
        usuario.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PerfilViewSet(viewsets.ModelViewSet):
    """Perfis de acesso: templates de permissão por módulo reutilizáveis
    entre usuários RH — exclusivo do Gestor. O perfil 'Administrador' (do
    próprio Gestor, criado pela migração) é do tipo sistema: nunca editável,
    desativável ou excluível por ninguém."""

    permission_classes = [IsGestor]
    http_method_names = ["get", "post", "patch", "put", "delete", "head", "options"]

    def get_queryset(self):
        company_id = capture_company_id(self.request)
        return Perfil.objects.filter(company_id=company_id).prefetch_related("function_permissions")

    def get_serializer_class(self):
        if self.action == "create":
            return PerfilCreateSerializer
        return PerfilSerializer

    def perform_create(self, serializer):
        company_id = capture_company_id(self.request)
        slug = slugify(serializer.validated_data["nome"])
        if Perfil.objects.filter(company_id=company_id, slug=slug).exists():
            raise ValidationError({"nome": "Já existe um perfil com esse nome."})
        perfil = serializer.save(company_id=company_id, slug=slug, tipo=Perfil.Tipo.PERSONALIZADO)
        for modulo in MODULOS:
            PerfilFunctionPermission.objects.create(
                perfil=perfil, company_id=company_id, function=modulo
            )

    def perform_update(self, serializer):
        if serializer.instance.tipo == Perfil.Tipo.SISTEMA:
            raise ValidationError("Perfis de sistema não podem ser editados.")
        perfil = serializer.save()
        for usuario in perfil.usuarios.filter(active=True):
            perfil.aplicar_a(usuario)

    def destroy(self, request, *args, **kwargs):
        perfil = self.get_object()
        if perfil.tipo == Perfil.Tipo.SISTEMA:
            return Response(
                {"detail": "Perfis de sistema não podem ser excluídos."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if perfil.usuarios.filter(active=True).exists():
            return Response(
                {"detail": "Não é possível excluir um perfil com usuários vinculados."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        perfil.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["put"])
    def permissoes(self, request, pk=None):
        perfil = self.get_object()
        if perfil.tipo == Perfil.Tipo.SISTEMA:
            raise ValidationError("Perfis de sistema não podem ser editados.")
        serializer = PerfilFunctionPermissionWriteSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        for item in serializer.validated_data:
            PerfilFunctionPermission.objects.update_or_create(
                perfil=perfil,
                function=item["function"],
                defaults={
                    "can_view": item["can_view"],
                    "can_create": item["can_create"],
                    "can_edit": item["can_edit"],
                    "can_delete": item["can_delete"],
                },
            )
        perfil.refresh_from_db()
        for usuario in perfil.usuarios.filter(active=True):
            perfil.aplicar_a(usuario)
        return Response(PerfilSerializer(perfil).data)

    @action(detail=True, methods=["post"])
    def duplicar(self, request, pk=None):
        original = self.get_object()
        company_id = capture_company_id(request)
        base_slug = slugify(f"{original.nome} copia")
        slug = base_slug
        contador = 2
        while Perfil.objects.filter(company_id=company_id, slug=slug).exists():
            slug = f"{base_slug}-{contador}"
            contador += 1
        copia = Perfil.objects.create(
            company_id=company_id,
            nome=f"{original.nome} (cópia)",
            slug=slug,
            descricao=original.descricao,
            tipo=Perfil.Tipo.PERSONALIZADO,
            ativo=True,
        )
        for perm in original.function_permissions.all():
            PerfilFunctionPermission.objects.create(
                perfil=copia,
                company_id=company_id,
                function=perm.function,
                can_view=perm.can_view,
                can_create=perm.can_create,
                can_edit=perm.can_edit,
                can_delete=perm.can_delete,
            )
        return Response(PerfilSerializer(copia).data, status=status.HTTP_201_CREATED)
