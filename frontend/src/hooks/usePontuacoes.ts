import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createPontuacao, listPontuacoes } from '@/api/pontuacoes'

export function usePontuacoes(candidatoId: string) {
  return useQuery({
    queryKey: ['pontuacoes', candidatoId],
    queryFn: () => listPontuacoes(candidatoId),
    enabled: !!candidatoId,
  })
}

export function useCreatePontuacao(candidatoId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (values: { funcao: string; pontuacao: string }) =>
      createPontuacao({ candidato: candidatoId, ...values }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['pontuacoes', candidatoId] }),
  })
}
