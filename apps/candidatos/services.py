import uuid

from django.conf import settings

from apps.candidatos.interfaces import CurriculoParserInterface
from apps.candidatos.repositories import PdfCurriculoParserRepository
from utils.queue import QueueEngine
from utils.storage import MinioStorage


def get_parser() -> CurriculoParserInterface:
    """Ponto único de resolução da implementação concreta do parser —
    troque aqui (ex: por um serviço de OCR real) sem tocar em quem consome.
    """
    return PdfCurriculoParserRepository()


def processar_upload_curriculo(candidato, arquivo):
    """Sobe o PDF pro MinIO e publica na fila rh.curriculos — nenhuma
    extração pesada roda aqui (síncrono na view); quem processa de fato é o
    consumer (management command consumir_curriculos).
    """
    storage = MinioStorage()
    key = f"{candidato.company_id}/{candidato.id}/{uuid.uuid4()}.pdf"
    storage.upload_fileobj(
        settings.MINIO_BUCKET_CURRICULOS, key, arquivo, content_type="application/pdf"
    )

    candidato.curriculo_bucket = settings.MINIO_BUCKET_CURRICULOS
    candidato.curriculo_key = key
    candidato.curriculo_status = candidato.StatusProcessamento.PROCESSANDO
    candidato.curriculo_erro = ""
    candidato.save(
        update_fields=[
            "curriculo_bucket",
            "curriculo_key",
            "curriculo_status",
            "curriculo_erro",
            "updated_at",
        ]
    )

    QueueEngine().publish(settings.QUEUE_CURRICULOS, {"candidato_id": str(candidato.id)})
