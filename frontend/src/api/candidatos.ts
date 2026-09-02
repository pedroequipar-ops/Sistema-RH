import { apiClient } from '@/api/client'
import type { Candidato, CandidatoFilters } from '@/types/candidatos'
import type { PaginatedResponse } from '@/types/vagas'

export async function listCandidatos(filters: CandidatoFilters) {
  const { data } = await apiClient.get<PaginatedResponse<Candidato>>('/v1/candidatos/', {
    params: {
      page: filters.page,
      search: filters.search || undefined,
      senioridade: filters.senioridade || undefined,
      cidade: filters.cidade || undefined,
      cargo_pretendido: filters.cargo_pretendido || undefined,
      skill: filters.skill || undefined,
    },
  })
  return data
}

export async function getCandidato(id: string) {
  const { data } = await apiClient.get<Candidato>(`/v1/candidatos/${id}/`)
  return data
}

export async function deleteCandidato(id: string) {
  await apiClient.delete(`/v1/candidatos/${id}/`)
}

export async function uploadCurriculo(id: string, file: File) {
  const formData = new FormData()
  formData.append('curriculo', file)
  const { data } = await apiClient.post<Candidato>(
    `/v1/candidatos/${id}/upload_curriculo/`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}
