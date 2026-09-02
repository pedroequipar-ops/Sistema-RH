import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createAvaliacao, listAvaliacoes } from '@/api/processos'

export function useAvaliacoes(processoId: string) {
  return useQuery({
    queryKey: ['avaliacoes', processoId],
    queryFn: () => listAvaliacoes(processoId),
    enabled: !!processoId,
  })
}

export function useCreateAvaliacao(processoId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ nota, comentario }: { nota: string; comentario: string }) =>
      createAvaliacao(processoId, nota, comentario),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['avaliacoes', processoId] }),
  })
}
