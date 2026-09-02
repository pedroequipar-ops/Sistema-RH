from datetime import timedelta, timezone

from django.utils import timezone as django_timezone

_DTFORMAT = "%Y%m%dT%H%M%SZ"


def gerar_ics(entrevista) -> str:
    """Gera o conteúdo de um convite .ics (padrão iCalendar) pra uma
    EntrevistaAgendamento — regra arquitetural 13: sem integração com API
    externa de calendário, o .ics anexado ao e-mail cobre qualquer
    calendário (Google, Outlook etc.).
    """
    inicio = entrevista.data_hora.astimezone(timezone.utc)
    fim = inicio + timedelta(minutes=entrevista.duracao_minutos)
    agora = django_timezone.now().astimezone(timezone.utc)
    cargo = entrevista.processo.vaga.cargo

    linhas = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Sistema RH//Entrevistas//PT-BR",
        "CALSCALE:GREGORIAN",
        "METHOD:REQUEST",
        "BEGIN:VEVENT",
        f"UID:{entrevista.id}@sistema-rh",
        f"DTSTAMP:{agora.strftime(_DTFORMAT)}",
        f"DTSTART:{inicio.strftime(_DTFORMAT)}",
        f"DTEND:{fim.strftime(_DTFORMAT)}",
        f"SUMMARY:Entrevista - {cargo}",
        f"DESCRIPTION:Entrevista de seleção para a vaga de {cargo}.",
        f"LOCATION:{entrevista.local_ou_link}",
        "STATUS:CONFIRMED",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(linhas)
