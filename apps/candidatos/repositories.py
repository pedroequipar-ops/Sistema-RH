import io
import re

from pypdf import PdfReader

from apps.candidatos.interfaces import CurriculoParserInterface


class PdfCurriculoParserRepository(CurriculoParserInterface):
    """Extrai texto de um PDF e aplica heurísticas simples (regex) pra achar
    nome, e-mail e telefone. Sem OCR de imagem — currículos escaneados como
    imagem não são suportados nesta versão (fica como falha de processamento).
    """

    EMAIL_REGEX = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
    TELEFONE_REGEX = re.compile(r"(\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}")

    def extrair_dados(self, conteudo: bytes) -> dict:
        texto = self._extrair_texto(conteudo)
        return self._extrair_dados_do_texto(texto)

    def _extrair_texto(self, conteudo: bytes) -> str:
        reader = PdfReader(io.BytesIO(conteudo))
        return "\n".join((page.extract_text() or "") for page in reader.pages)

    def _extrair_dados_do_texto(self, texto: str) -> dict:
        linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
        return {
            "nome": linhas[0] if linhas else "",
            "email": self._buscar(self.EMAIL_REGEX, texto),
            "telefone": self._buscar(self.TELEFONE_REGEX, texto),
            "resumo_experiencia": texto[:2000],
        }

    def _buscar(self, regex, texto):
        match = regex.search(texto)
        return match.group(0) if match else ""
