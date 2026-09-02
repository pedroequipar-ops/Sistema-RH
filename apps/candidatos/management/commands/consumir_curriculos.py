import json

import pika
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.candidatos.models import Candidato
from apps.candidatos.services import get_parser
from apps.core.logger import logger
from utils.storage import MinioStorage


class Command(BaseCommand):
    help = (
        "Consome a fila rh.curriculos: baixa o PDF do MinIO, extrai dados via "
        "apps.candidatos.services.get_parser() e atualiza o Candidato."
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
        channel.queue_declare(queue=settings.QUEUE_CURRICULOS, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=settings.QUEUE_CURRICULOS, on_message_callback=self._callback)

        self.stdout.write(f"Aguardando mensagens em '{settings.QUEUE_CURRICULOS}'...")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        finally:
            connection.close()

    def _callback(self, channel, method, properties, body):
        payload = json.loads(body)
        candidato_id = payload["candidato_id"]
        try:
            candidato = Candidato.all_objects.get(id=candidato_id)
            conteudo = MinioStorage().download_bytes(
                candidato.curriculo_bucket, candidato.curriculo_key
            )
            dados = get_parser().extrair_dados(conteudo)

            candidato.nome = candidato.nome or dados.get("nome", "")
            candidato.telefone = candidato.telefone or dados.get("telefone", "")
            candidato.resumo_experiencia = dados.get("resumo_experiencia", "")
            candidato.curriculo_status = Candidato.StatusProcessamento.PROCESSADO
            candidato.save(
                update_fields=[
                    "nome",
                    "telefone",
                    "resumo_experiencia",
                    "curriculo_status",
                    "updated_at",
                ]
            )
            logger.info("curriculo.processado", candidato_id=candidato_id)
        except Exception as exc:  # noqa: BLE001 - consumer não pode derrubar o processo
            logger.exception(
                "curriculo.falha_processamento", candidato_id=candidato_id, erro=str(exc)
            )
            Candidato.all_objects.filter(id=candidato_id).update(
                curriculo_status=Candidato.StatusProcessamento.FALHA, curriculo_erro=str(exc)
            )
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)
