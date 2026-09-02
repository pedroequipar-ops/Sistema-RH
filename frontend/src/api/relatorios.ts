import { apiClient } from '@/api/client'
import type {
  CandidatosPorVaga,
  CustoContratacao,
  FunilEtapa,
  TempoMedioContratacao,
} from '@/types/relatorios'

export async function getTempoMedioContratacao(vagaId?: string) {
  const { data } = await apiClient.get<TempoMedioContratacao>(
    '/v1/relatorios/tempo-medio-contratacao/',
    { params: { vaga: vagaId || undefined } },
  )
  return data
}

export async function getCandidatosPorVaga() {
  const { data } = await apiClient.get<CandidatosPorVaga[]>('/v1/relatorios/candidatos-por-vaga/')
  return data
}

export async function getFunilConversao() {
  const { data } = await apiClient.get<FunilEtapa[]>('/v1/relatorios/funil-conversao/')
  return data
}

export async function getCustoContratacao() {
  const { data } = await apiClient.get<CustoContratacao>('/v1/relatorios/custo-contratacao/')
  return data
}
