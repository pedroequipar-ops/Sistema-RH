import boto3
from botocore.client import Config
from django.conf import settings


class MinioStorage:
    """Cliente S3-compatible para o MinIO. Nunca gera URL pública permanente —
    sempre presigned URL (TTL padrão: settings.MINIO_PRESIGNED_URL_TTL, máx 24h).
    """

    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            use_ssl=settings.MINIO_USE_SSL,
        )
        # Presigned URLs vão pro navegador do usuário, que não resolve o
        # hostname interno do Docker (ex: "minio") — geradas com um client
        # apontando pro endpoint público, credenciais e assinatura iguais.
        self._public_client = boto3.client(
            "s3",
            endpoint_url=settings.MINIO_PUBLIC_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            use_ssl=settings.MINIO_USE_SSL,
        )

    def ensure_bucket(self, bucket):
        existing = [b["Name"] for b in self._client.list_buckets().get("Buckets", [])]
        if bucket not in existing:
            self._client.create_bucket(Bucket=bucket)

    def upload_fileobj(self, bucket, key, fileobj, content_type=None):
        self.ensure_bucket(bucket)
        extra_args = {"ContentType": content_type} if content_type else {}
        self._client.upload_fileobj(fileobj, bucket, key, ExtraArgs=extra_args)
        return key

    def generate_presigned_url(self, bucket, key, ttl=None):
        ttl = ttl or settings.MINIO_PRESIGNED_URL_TTL
        return self._public_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=int(ttl.total_seconds()),
        )

    def download_bytes(self, bucket, key):
        response = self._client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()
