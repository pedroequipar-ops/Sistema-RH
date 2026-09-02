import uuid

from django.conf import settings

from apps.admissao.models import DOCUMENTOS_PADRAO_ADMISSAO, ChecklistItemAdmissao, Funcionario
from utils.storage import MinioStorage


def criar_funcionario_para_processo(processo):
    """Chamado quando um ProcessoSeletivo chega em 'contratado' (ver
    apps.processos_seletivos.views.ProcessoSeletivoViewSet.mover_etapa).
    Idempotente: se o Funcionario já existe pra este processo, só retorna.
    """
    funcionario, criado = Funcionario.objects.get_or_create(
        processo=processo,
        defaults={
            "company_id": processo.company_id,
            "candidato": processo.candidato,
            "vaga": processo.vaga,
            "cargo": processo.vaga.cargo,
        },
    )
    if criado:
        ChecklistItemAdmissao.objects.bulk_create(
            [
                ChecklistItemAdmissao(
                    company_id=processo.company_id,
                    funcionario=funcionario,
                    nome_documento=nome_documento,
                )
                for nome_documento in DOCUMENTOS_PADRAO_ADMISSAO
            ]
        )
    return funcionario


def processar_upload_documento(item, arquivo):
    """Sobe o documento pro MinIO (bucket admissao_documentos) e marca o
    item como enviado, aguardando revisão do RH."""
    storage = MinioStorage()
    key = f"{item.funcionario.company_id}/{item.funcionario_id}/{item.id}/{uuid.uuid4()}.pdf"
    storage.upload_fileobj(settings.MINIO_BUCKET_ADMISSAO, key, arquivo)

    item.documento_bucket = settings.MINIO_BUCKET_ADMISSAO
    item.documento_key = key
    item.status = ChecklistItemAdmissao.Status.ENVIADO
    item.observacao = ""
    item.save(
        update_fields=["documento_bucket", "documento_key", "status", "observacao", "updated_at"]
    )
