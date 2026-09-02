import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { avaliarTeste, createTeste, listTestes } from '@/api/processos'

export function useTestes(processoId: string) {
  return useQuery({
    queryKey: ['testes', processoId],
    queryFn: () => listTestes(processoId),
    enabled: !!processoId,
  })
}

export function useCreateTeste(processoId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ tipo, titulo }: { tipo: string; titulo: string }) =>
      createTeste(processoId, tipo, titulo),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['testes', processoId] }),
  })
}

export function useAvaliarTeste(processoId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, nota }: { id: string; nota: string }) => avaliarTeste(id, nota),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['testes', processoId] }),
  })
}
