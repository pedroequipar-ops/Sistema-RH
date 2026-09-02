from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.core.serializers import UserMeSerializer


class MeView(generics.RetrieveAPIView):
    """Perfil do usuário interno autenticado (RH/Gestor/Diretoria): dados
    básicos + company_id + permissões por função, usados pelo frontend para
    montar o menu e anexar o header X-Company-ID nas próximas requisições.
    """

    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
