from rest_framework.permissions import BasePermission

from apps.candidatos.models import Candidato


class IsCandidato(BasePermission):
    """Endpoints do portal do candidato não usam HasFunctionPermission/RBAC —
    são restritos por ownership: só o próprio candidato autenticado acessa.
    """

    def has_permission(self, request, view):
        return isinstance(request.user, Candidato) and bool(request.user.is_authenticated)
