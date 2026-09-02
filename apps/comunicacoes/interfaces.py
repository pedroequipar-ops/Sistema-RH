from abc import ABC, abstractmethod


class EmailProviderInterface(ABC):
    """Contrato pra envio de e-mail (padrão obrigatório Interface ->
    Repository -> View, regra arquitetural 7). O consumer depende só desta
    interface; a implementação concreta é resolvida por
    apps.comunicacoes.services.get_email_provider().
    """

    @abstractmethod
    def enviar(self, destinatario: str, assunto: str, corpo_html: str, anexos: list | None = None):
        """anexos: lista de dicts {"filename": str, "conteudo": str|bytes,
        "mimetype": str}. Ex: o convite de entrevista anexa o .ics gerado
        pela Etapa B3 (apps.processos_seletivos.ics)."""
        raise NotImplementedError
