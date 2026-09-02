from datetime import timedelta

import pytest
from django.utils import timezone

from apps.core.tests.factories import UserFactory
from apps.processos_seletivos.ics import gerar_ics
from apps.processos_seletivos.models import EntrevistaAgendamento
from apps.processos_seletivos.tests.factories import ProcessoSeletivoFactory

pytestmark = pytest.mark.django_db


def test_gerar_ics_contem_campos_essenciais():
    processo = ProcessoSeletivoFactory()
    entrevista = EntrevistaAgendamento.objects.create(
        company_id=processo.company_id,
        processo=processo,
        data_hora=timezone.now() + timedelta(days=1),
        duracao_minutos=30,
        local_ou_link="https://meet.example.com/xyz",
        criado_por=UserFactory(company_id=processo.company_id),
    )

    conteudo = gerar_ics(entrevista)

    assert conteudo.startswith("BEGIN:VCALENDAR")
    assert conteudo.strip().endswith("END:VCALENDAR")
    assert "BEGIN:VEVENT" in conteudo
    assert f"UID:{entrevista.id}@sistema-rh" in conteudo
    assert processo.vaga.cargo in conteudo
    assert "https://meet.example.com/xyz" in conteudo
