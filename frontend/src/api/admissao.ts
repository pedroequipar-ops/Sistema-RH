import { apiClient } from '@/api/client'
import type {
  ChecklistStatus,
  Funcionario,
  FuncionarioFilters,
  PaginatedResponse,
} from '@/types/admissao'

export async function listFuncionarios(filters: FuncionarioFilters) {
  const { data } = await apiClient.get<PaginatedResponse<Funcionario>>('/v1/funcionarios/', {
    params: { status_onboarding: filters.status_onboarding || undefined },
  })
  return data
}

export async function getFuncionario(id: string) {
  const { data } = await apiClient.get<Funcionario>(`/v1/funcionarios/${id}/`)
  return data
}

export async function updateFuncionario(id: string, data_admissao: string) {
  const { data } = await apiClient.patch<Funcionario>(`/v1/funcionarios/${id}/`, { data_admissao })
  return data
}

export async function revisarChecklistItem(
  id: string,
  status: ChecklistStatus,
  observacao: string,
) {
  const { data } = await apiClient.post(`/v1/checklist-admissao/${id}/revisar/`, {
    status,
    observacao,
  })
  return data
}
