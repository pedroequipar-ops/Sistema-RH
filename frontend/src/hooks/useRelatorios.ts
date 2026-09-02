import { useQuery } from '@tanstack/react-query'

import {
  getCandidatosPorVaga,
  getCustoContratacao,
  getFunilConversao,
  getTempoMedioContratacao,
} from '@/api/relatorios'

export function useTempoMedioContratacao(vagaId: string) {
  return useQuery({
    queryKey: ['relatorio-tempo-medio', vagaId],
    queryFn: () => getTempoMedioContratacao(vagaId),
  })
}

export function useCandidatosPorVaga() {
  return useQuery({ queryKey: ['relatorio-candidatos-por-vaga'], queryFn: getCandidatosPorVaga })
}

export function useFunilConversao() {
  return useQuery({ queryKey: ['relatorio-funil-conversao'], queryFn: getFunilConversao })
}

export function useCustoContratacao() {
  return useQuery({ queryKey: ['relatorio-custo-contratacao'], queryFn: getCustoContratacao })
}
