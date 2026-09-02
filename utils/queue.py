import json

import pika
from django.conf import settings


class QueueEngine:
    """Publisher para RabbitMQ. Nenhuma operação de I/O pesado roda síncrona
    na view — a view só publica o payload aqui; o processamento pesado é
    feito por um consumer separado (worker/management command).
    """

    def _get_connection(self):
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            virtual_host=settings.RABBITMQ_VHOST,
            credentials=credentials,
        )
        return pika.BlockingConnection(parameters)

    def publish(self, queue, payload):
        connection = self._get_connection()
        try:
            channel = connection.channel()
            channel.queue_declare(queue=queue, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=queue,
                body=json.dumps(payload, default=str),
                properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
            )
        finally:
            connection.close()
