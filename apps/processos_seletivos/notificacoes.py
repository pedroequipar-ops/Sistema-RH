from django.conf import settings

from apps.processos_seletivos.ics import gerar_ics
from utils.queue import QueueEngine


def publicar_mudanca_etapa(processo, etapa_anterior):
    """Regra 8: movimentação de etapa dispara notificação (gestor) e e-mail
    (candidato) — publica só o evento, quem realmente envia/renderiza o
    e-mail é o consumer que a Etapa B4 (comunicacoes) constrói.
    """
    candidato = processo.candidato
    vaga = processo.vaga

    QueueEngine().publish(
        settings.QUEUE_MAIL,
        {
            "tipo": "processo_mudanca_etapa",
            "candidato_email": candidato.email,
            "candidato_nome": candidato.nome,
            "vaga_cargo": vaga.cargo,
            "etapa_anterior": etapa_anterior,
            "etapa_atual": processo.etapa_atual,
            "processo_id": str(processo.id),
        },
    )
    QueueEngine().publish(
        settings.QUEUE_NOTIFICATIONS,
        {
            "tipo": "processo_mudanca_etapa",
            "destinatario_user_id": str(vaga.solicitante_id),
            "candidato_nome": candidato.nome,
            "vaga_cargo": vaga.cargo,
            "etapa_atual": processo.etapa_atual,
            "processo_id": str(processo.id),
        },
    )


def publicar_entrevista_agendada(entrevista):
    candidato = entrevista.processo.candidato
    vaga = entrevista.processo.vaga
    ics_conteudo = gerar_ics(entrevista)

    QueueEngine().publish(
        settings.QUEUE_MAIL,
        {
            "tipo": "convite_entrevista",
            "candidato_email": candidato.email,
            "candidato_nome": candidato.nome,
            "vaga_cargo": vaga.cargo,
            "data_hora": entrevista.data_hora.isoformat(),
            "local_ou_link": entrevista.local_ou_link,
            "ics_conteudo": ics_conteudo,
            "ics_filename": "entrevista.ics",
            "processo_id": str(entrevista.processo_id),
        },
    )
    QueueEngine().publish(
        settings.QUEUE_NOTIFICATIONS,
        {
            "tipo": "entrevista_agendada",
            "destinatario_user_id": str(vaga.solicitante_id),
            "candidato_nome": candidato.nome,
            "vaga_cargo": vaga.cargo,
            "data_hora": entrevista.data_hora.isoformat(),
            "processo_id": str(entrevista.processo_id),
        },
    )
