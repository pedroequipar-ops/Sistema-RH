import { apiClient } from '@/api/client'
import type {
  PaginatedResponse,
  Vaga,
  VagaFilters,
  VagaFormValues,
  VagaListItem,
} from '@/types/vagas'

export async function listVagasParaFiltro() {
  const { data } = await apiClient.get<PaginatedResponse<VagaListItem>>('/v1/vagas/', {
    params: { page_size: 100 },
  })
  return data
}

export async function listVagas(filters: VagaFilters) {
  const { data } = await apiClient.get<PaginatedResponse<VagaListItem>>('/v1/vagas/', {
    params: {
      page: filters.page,
      search: filters.search || undefined,
      status: filters.status || undefined,
      status_aprovacao: filters.status_aprovacao || undefined,
      tipo: filters.tipo || undefined,
    },
  })
  return data
}

export async function getVaga(id: string) {
  const { data } = await apiClient.get<Vaga>(`/v1/vagas/${id}/`)
  return data
}

export async function createVaga(values: VagaFormValues) {
  const { data } = await apiClient.post<Vaga>('/v1/vagas/', {
    ...values,
    salario: values.salario || null,
  })
  return data
}

export async function updateVaga(id: string, values: Partial<VagaFormValues>) {
  const { data } = await apiClient.patch<Vaga>(`/v1/vagas/${id}/`, values)
  return data
}

export async function deleteVaga(id: string) {
  await apiClient.delete(`/v1/vagas/${id}/`)
}

export async function aprovarVaga(id: string, observacao?: string) {
  const { data } = await apiClient.post<Vaga>(`/v1/vagas/${id}/aprovar/`, { observacao })
  return data
}

export async function reprovarVaga(id: string, observacao?: string) {
  const { data } = await apiClient.post<Vaga>(`/v1/vagas/${id}/reprovar/`, { observacao })
  return data
}

export async function pausarVaga(id: string, observacao?: string) {
  const { data } = await apiClient.post<Vaga>(`/v1/vagas/${id}/pausar/`, { observacao })
  return data
}

export async function cancelarVaga(id: string, observacao?: string) {
  const { data } = await apiClient.post<Vaga>(`/v1/vagas/${id}/cancelar/`, { observacao })
  return data
}
