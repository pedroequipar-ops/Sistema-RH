from abc import ABC, abstractmethod


class CurriculoParserInterface(ABC):
    """Contrato pra extração de dados de um currículo (padrão obrigatório
    Interface -> Repository -> View, ver regra arquitetural 7). A view/consumer
    depende só desta interface; a implementação concreta (Repository) é
    resolvida por apps.candidatos.services.get_parser().
    """

    @abstractmethod
    def extrair_dados(self, conteudo: bytes) -> dict:
        """Recebe os bytes do arquivo e retorna um dict best-effort com as
        chaves: nome, email, telefone, resumo_experiencia.
        """
        raise NotImplementedError
