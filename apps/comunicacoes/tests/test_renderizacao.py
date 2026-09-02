import pytest

from apps.comunicacoes.renderizacao import resolver_template_e_assunto


def test_resolver_template_confirmacao_inscricao():
    template, assunto = resolver_template_e_assunto({"tipo": "confirmacao_inscricao"})

    assert template == "emails/confirmacao_inscricao.html"
    assert assunto


def test_resolver_template_reprovacao_quando_etapa_reprovado():
    template, _ = resolver_template_e_assunto(
        {"tipo": "processo_mudanca_etapa", "etapa_atual": "reprovado"}
    )

    assert template == "emails/reprovacao.html"


def test_resolver_template_atualizacao_quando_outra_etapa():
    template, _ = resolver_template_e_assunto(
        {"tipo": "processo_mudanca_etapa", "etapa_atual": "teste"}
    )

    assert template == "emails/atualizacao_processo.html"


def test_resolver_template_convite_entrevista():
    template, _ = resolver_template_e_assunto({"tipo": "convite_entrevista"})

    assert template == "emails/convite_entrevista.html"


def test_resolver_template_tipo_desconhecido_lanca_erro():
    with pytest.raises(ValueError):
        resolver_template_e_assunto({"tipo": "bagunca"})
