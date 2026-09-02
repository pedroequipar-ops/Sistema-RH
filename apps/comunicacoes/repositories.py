from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from apps.comunicacoes.interfaces import EmailProviderInterface


class DjangoEmailProviderRepository(EmailProviderInterface):
    """Envia via django.core.mail — funciona com qualquer provedor real
    (Gmail, SES, Mailgun etc.) que fale SMTP, configurado por env
    (EMAIL_HOST/PORT/USER/PASSWORD), sem SDK de terceiro. Em dev,
    EMAIL_BACKEND aponta pro console (imprime nos logs do worker).
    """

    def enviar(self, destinatario, assunto, corpo_html, anexos=None):
        email = EmailMultiAlternatives(
            subject=assunto,
            body=strip_tags(corpo_html),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario],
        )
        email.attach_alternative(corpo_html, "text/html")
        for anexo in anexos or []:
            email.attach(
                anexo["filename"],
                anexo["conteudo"],
                anexo.get("mimetype", "application/octet-stream"),
            )
        email.send(fail_silently=False)
