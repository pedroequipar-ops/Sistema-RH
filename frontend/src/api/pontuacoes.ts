import { apiClient } from '@/api/client'
import type { PontuacaoCandidato } from '@/types/candidatos'
import type { PaginatedResponse } from '@/types/vagas'

export async function listPontuacoes(candidatoId: string) {
  const { data } = await apiClient.get<PaginatedResponse<PontuacaoCandidato>>(
    '/v1/pontuacoes-candidato/',
    { params: { candidato: candidatoId } },
  )
  return data
}

export async function createPontuacao(values: { candidato: string; funcao: string; pontuacao: string }) {
  const { data } = await apiClient.post<PontuacaoCandidato>('/v1/pontuacoes-candidato/', values)
  return data
}
