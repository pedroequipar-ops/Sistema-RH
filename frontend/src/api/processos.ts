import { apiClient } from '@/api/client'
import type {
  AvaliacaoProcesso,
  EntrevistaAgendamento,
  Etapa,
  PaginatedResponse,
  ProcessoFilters,
  ProcessoSeletivo,
  TesteAplicado,
} from '@/types/processos'

export async function listProcessos(filters: ProcessoFilters) {
  const { data } = await apiClient.get<PaginatedResponse<ProcessoSeletivo>>(
    '/v1/processos-seletivos/',
    { params: { vaga: filters.vaga || undefined, etapa_atual: filters.etapa_atual || undefined, page_size: 100 } },
  )
  return data
}

export async function getProcesso(id: string) {
  const { data } = await apiClient.get<ProcessoSeletivo>(`/v1/processos-seletivos/${id}/`)
  return data
}

export async function moverEtapa(id: string, etapa: Etapa, observacao?: string) {
  const { data } = await apiClient.post<ProcessoSeletivo>(
    `/v1/processos-seletivos/${id}/mover_etapa/`,
    { etapa, observacao },
  )
  return data
}

export async function listAvaliacoes(processoId: string) {
  const { data } = await apiClient.get<PaginatedResponse<AvaliacaoProcesso>>(
    '/v1/avaliacoes-processo/',
    { params: { processo: processoId } },
  )
  return data
}

export async function createAvaliacao(processoId: string, nota: string, comentario: string) {
  const { data } = await apiClient.post<AvaliacaoProcesso>('/v1/avaliacoes-processo/', {
    processo: processoId,
    nota: nota || null,
    comentario,
  })
  return data
}

export async function listTestes(processoId: string) {
  const { data } = await apiClient.get<PaginatedResponse<TesteAplicado>>('/v1/testes-processo/', {
    params: { processo: processoId },
  })
  return data
}

export async function createTeste(processoId: string, tipo: string, titulo: string) {
  const { data } = await apiClient.post<TesteAplicado>('/v1/testes-processo/', {
    processo: processoId,
    tipo,
    titulo,
  })
  return data
}

export async function avaliarTeste(id: string, nota: string) {
  const { data } = await apiClient.post<TesteAplicado>(`/v1/testes-processo/${id}/avaliar/`, {
    nota,
  })
  return data
}

export async function listEntrevistas(processoId: string) {
  const { data } = await apiClient.get<PaginatedResponse<EntrevistaAgendamento>>('/v1/entrevistas/', {
    params: { processo: processoId },
  })
  return data
}

export async function createEntrevista(
  processoId: string,
  values: { data_hora: string; duracao_minutos: number; local_ou_link: string; observacoes: string },
) {
  const { data } = await apiClient.post<EntrevistaAgendamento>('/v1/entrevistas/', {
    processo: processoId,
    ...values,
  })
  return data
}
