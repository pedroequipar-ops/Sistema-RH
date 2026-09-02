from apps.comunicacoes.interfaces import EmailProviderInterface
from apps.comunicacoes.repositories import DjangoEmailProviderRepository


def get_email_provider() -> EmailProviderInterface:
    """Ponto único de resolução do provedor de e-mail — troque aqui sem
    tocar em quem consome (o consumer de mail_queue)."""
    return DjangoEmailProviderRepository()
