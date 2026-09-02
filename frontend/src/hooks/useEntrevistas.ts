import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createEntrevista, listEntrevistas } from '@/api/processos'

export function useEntrevistas(processoId: string) {
  return useQuery({
    queryKey: ['entrevistas', processoId],
    queryFn: () => listEntrevistas(processoId),
    enabled: !!processoId,
  })
}

export function useCreateEntrevista(processoId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (values: {
      data_hora: string
      duracao_minutos: number
      local_ou_link: string
      observacoes: string
    }) => createEntrevista(processoId, values),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['entrevistas', processoId] }),
  })
}
