from apps.candidatos.repositories import PdfCurriculoParserRepository


def test_extrai_nome_email_telefone_do_texto():
    parser = PdfCurriculoParserRepository()
    texto = "João Silva\nDesenvolvedor Backend\ncontato: joao.silva@email.com\n(11) 98765-4321"

    dados = parser._extrair_dados_do_texto(texto)

    assert dados["nome"] == "João Silva"
    assert dados["email"] == "joao.silva@email.com"
    assert "98765-4321" in dados["telefone"]
    assert texto in dados["resumo_experiencia"] or dados["resumo_experiencia"].startswith("João")


def test_texto_sem_email_nem_telefone_retorna_vazio():
    parser = PdfCurriculoParserRepository()
    dados = parser._extrair_dados_do_texto("Apenas um texto qualquer sem contato")

    assert dados["email"] == ""
    assert dados["telefone"] == ""
