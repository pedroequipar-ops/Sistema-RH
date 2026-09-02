import json

import pika
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from apps.comunicacoes.models import EmailEnviado, Notificacao
from apps.comunicacoes.renderizacao import resolver_template_e_assunto
from apps.comunicacoes.services import get_email_provider
from apps.core.logger import logger
from apps.processos_seletivos.models import ProcessoSeletivo


class Command(BaseCommand):
    help = (
        "Consome mail_queue e notifications: renderiza template e envia "
        "e-mail via apps.comunicacoes.services.get_email_provider(), e "
        "persiste notificações internas (Notificacao)."
    )

    def handle(self, *args, **options):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                virtual_host=settings.RABBITMQ_VHOST,
                credentials=pika.PlainCredentials(
                    settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD
                ),
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue=settings.QUEUE_MAIL, durable=True)
        channel.queue_declare(queue=settings.QUEUE_NOTIFICATIONS, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=settings.QUEUE_MAIL, on_message_callback=self._consumir_mail)
        channel.basic_consume(
            queue=settings.QUEUE_NOTIFICATIONS, on_message_callback=self._consumir_notificacao
        )

        self.stdout.write(
            f"Aguardando mensagens em '{settings.QUEUE_MAIL}' e "
            f"'{settings.QUEUE_NOTIFICATIONS}'..."
        )
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        finally:
            connection.close()

    def _consumir_mail(self, channel, method, properties, body):
        payload = json.loads(body)
        processo = None
        try:
            processo = ProcessoSeletivo.objects.get(id=payload["processo_id"])
            template, assunto = resolver_template_e_assunto(payload)
            corpo_html = render_to_string(template, payload)

            anexos = None
            if payload.get("ics_conteudo"):
                anexos = [
                    {
                        "filename": payload.get("ics_filename", "convite.ics"),
                        "conteudo": payload["ics_conteudo"],
                        "mimetype": "text/calendar",
                    }
                ]

            get_email_provider().enviar(payload["candidato_email"], assunto, corpo_html, anexos)

            EmailEnviado.objects.create(
                company_id=processo.company_id,
                tipo=payload["tipo"],
                destinatario=payload["candidato_email"],
                assunto=assunto,
                candidato=processo.candidato,
                processo=processo,
                status=EmailEnviado.Status.ENVIADO,
            )
            logger.info(
                "email.enviado", tipo=payload["tipo"], destinatario=payload["candidato_email"]
            )
        except Exception as exc:  # noqa: BLE001 - consumer não pode derrubar o processo
            logger.exception("email.falha_envio", payload=payload, erro=str(exc))
            if processo:
                EmailEnviado.objects.create(
                    company_id=processo.company_id,
                    tipo=payload.get("tipo", "desconhecido"),
                    destinatario=payload.get("candidato_email", ""),
                    assunto="",
                    candidato=processo.candidato,
                    processo=processo,
                    status=EmailEnviado.Status.FALHA,
                    erro=str(exc),
                )
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def _consumir_notificacao(self, channel, method, properties, body):
        payload = json.loads(body)
        try:
            processo = ProcessoSeletivo.objects.get(id=payload["processo_id"])
            Notificacao.objects.create(
                company_id=processo.company_id,
                destinatario_id=payload["destinatario_user_id"],
                tipo=payload["tipo"],
                mensagem=self._montar_mensagem(payload),
                processo=processo,
                dados=payload,
            )
            logger.info("notificacao.criada", tipo=payload["tipo"])
        except Exception as exc:  # noqa: BLE001
            logger.exception("notificacao.falha_criacao", payload=payload, erro=str(exc))
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def _montar_mensagem(self, payload):
        if payload["tipo"] == "processo_mudanca_etapa":
            return (
                f"{payload['candidato_nome']} avançou para a etapa "
                f"'{payload['etapa_atual']}' na vaga de {payload['vaga_cargo']}."
            )
        if payload["tipo"] == "entrevista_agendada":
            return (
                f"Entrevista agendada com {payload['candidato_nome']} pra vaga de "
                f"{payload['vaga_cargo']} em {payload['data_hora']}."
            )
        return f"Notificação: {payload['tipo']}"
