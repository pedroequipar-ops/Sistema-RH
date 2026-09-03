import { apiClient } from '@/api/client'
import type {
  EmailEnviado,
  EmailFilters,
  Notificacao,
  NotificacaoFilters,
  PaginatedResponse,
} from '@/types/comunicacoes'

export async function listEmails(filters: EmailFilters) {
  const { data } = await apiClient.get<PaginatedResponse<EmailEnviado>>('/v1/emails-enviados/', {
    params: { status: filters.status || undefined, tipo: filters.tipo || undefined },
  })
  return data
}

export async function listNotificacoes(filters: NotificacaoFilters) {
  const { data } = await apiClient.get<PaginatedResponse<Notificacao>>('/v1/notificacoes/', {
    params: { lida: filters.lida || undefined, page_size: 50 },
  })
  return data
}

export async function marcarNotificacaoLida(id: string) {
  const { data } = await apiClient.post<Notificacao>(`/v1/notificacoes/${id}/marcar_lida/`)
  return data
}

export async function limparNotificacoes() {
  const { data } = await apiClient.post<{ limpas: number }>('/v1/notificacoes/limpar_todas/')
  return data
}

export async function contarNotificacoesNaoLidas() {
  const { data } = await apiClient.get<PaginatedResponse<Notificacao>>('/v1/notificacoes/', {
    params: { lida: 'false', page_size: 1 },
  })
  return data.count
}
