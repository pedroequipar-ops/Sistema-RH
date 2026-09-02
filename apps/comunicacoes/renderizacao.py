TEMPLATES_POR_TIPO = {
    "confirmacao_inscricao": "emails/confirmacao_inscricao.html",
    "convite_entrevista": "emails/convite_entrevista.html",
}

ASSUNTOS_POR_TIPO = {
    "confirmacao_inscricao": "Recebemos sua candidatura!",
    "convite_entrevista": "Convite para entrevista",
}


def resolver_template_e_assunto(payload):
    """Escolhe o template/assunto de e-mail a partir do evento publicado em
    mail_queue. 'processo_mudanca_etapa' precisa olhar etapa_atual porque
    cobre tanto reprovação quanto avanço normal de etapa (regra 8 nomeia só
    3 templates — confirmação, reprovação, convite — e este mapeamento
    cobre os dois casos que "processo_mudanca_etapa" pode representar).
    """
    tipo = payload["tipo"]
    if tipo == "processo_mudanca_etapa":
        if payload.get("etapa_atual") == "reprovado":
            return "emails/reprovacao.html", "Atualização sobre sua candidatura"
        return "emails/atualizacao_processo.html", "Atualização do seu processo seletivo"

    template = TEMPLATES_POR_TIPO.get(tipo)
    assunto = ASSUNTOS_POR_TIPO.get(tipo)
    if not template:
        raise ValueError(f"Tipo de e-mail desconhecido: {tipo}")
    return template, assunto
