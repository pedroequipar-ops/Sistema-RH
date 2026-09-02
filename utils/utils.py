from uuid import UUID

from rest_framework.exceptions import ValidationError


def capture_company_id(request):
    """Lê e valida o header X-Company-ID, obrigatório em toda requisição de
    domínio (multi-tenancy). Usar em get_queryset()/perform_create() de todo
    ViewSet de domínio.
    """
    raw_value = request.headers.get("X-Company-ID")
    if not raw_value:
        raise ValidationError({"X-Company-ID": "Header obrigatório."})
    try:
        return UUID(raw_value)
    except (ValueError, AttributeError):
        raise ValidationError({"X-Company-ID": "UUID inválido."})
