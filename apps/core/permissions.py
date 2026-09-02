from django.core.exceptions import ImproperlyConfigured
from rest_framework.permissions import BasePermission

from apps.core.models import UserFunctionPermission

ACTION_FIELD = {
    "view": "can_view",
    "create": "can_create",
    "edit": "can_edit",
    "delete": "can_delete",
}


class HasFunctionPermission(BasePermission):
    """RBAC por função de módulo.

    Todo ViewSet de domínio (RH/Gestor) deve declarar:
      permission_path = "vagas"                      # slug kebab-case do módulo
      permission_action_map = {                       # ação DRF -> ação de permissão
          "list": "view", "retrieve": "view",
          "create": "create",
          "update": "edit", "partial_update": "edit",
          "destroy": "delete",
      }

    is_superuser=True bypassa tudo. Candidato (apps.candidatos) não usa esta
    permission — autentica com outro model e é restrito por ownership, não RBAC.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "is_superuser", False):
            return True

        permission_path = getattr(view, "permission_path", None)
        action_map = getattr(view, "permission_action_map", None)
        if not permission_path or action_map is None:
            raise ImproperlyConfigured(
                f"{view.__class__.__name__} precisa declarar permission_path e "
                "permission_action_map para usar HasFunctionPermission."
            )

        required_action = action_map.get(view.action)
        if required_action is None:
            return False

        field = ACTION_FIELD.get(required_action)
        if field is None:
            raise ImproperlyConfigured(
                f"Ação de permissão desconhecida: '{required_action}'. "
                f"Use um de: {list(ACTION_FIELD)}."
            )

        return UserFunctionPermission.objects.filter(
            user=user, function=permission_path, **{field: True}
        ).exists()
