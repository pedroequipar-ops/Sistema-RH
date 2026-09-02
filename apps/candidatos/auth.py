from rest_framework import serializers
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from apps.candidatos.models import Candidato

TOKEN_TYPE_ACTOR = "candidato"


def emitir_tokens_candidato(candidato):
    """Emite um par access/refresh para um Candidato — não usa
    TokenObtainPairSerializer padrão porque este é tied a settings.AUTH_USER_MODEL
    (core.User). Os claims custom aqui são o que distingue este token de um
    token de usuário interno; /v1/auth/token/refresh/ e /verify/ (simplejwt
    padrão) funcionam para os dois tipos de token sem alteração, pois só
    copiam/validam claims, sem exigir USER_ID_CLAIM.
    """
    refresh = RefreshToken()
    refresh["candidato_id"] = str(candidato.id)
    refresh["company_id"] = str(candidato.company_id)
    refresh["token_type_actor"] = TOKEN_TYPE_ACTOR
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class CandidatoJWTAuthentication(JWTAuthentication):
    """Reaproveita toda a validação de assinatura/expiração de JWTAuthentication,
    só troca get_user pra resolver um Candidato em vez de core.User.
    """

    def get_user(self, validated_token):
        if validated_token.get("token_type_actor") != TOKEN_TYPE_ACTOR:
            raise AuthenticationFailed("Token não pertence a um candidato.")
        candidato_id = validated_token.get("candidato_id")
        try:
            return Candidato.objects.get(id=candidato_id)
        except Candidato.DoesNotExist:
            raise AuthenticationFailed("Candidato não encontrado.")


class CandidatoTokenObtainSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        company_id = self.context["company_id"]
        try:
            candidato = Candidato.objects.get(company_id=company_id, email=attrs["email"])
        except Candidato.DoesNotExist:
            raise serializers.ValidationError("Credenciais inválidas.")
        if not candidato.check_password(attrs["password"]):
            raise serializers.ValidationError("Credenciais inválidas.")
        return emitir_tokens_candidato(candidato)
