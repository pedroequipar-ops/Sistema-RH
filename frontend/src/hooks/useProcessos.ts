import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { getProcesso, listProcessos, moverEtapa } from '@/api/processos'
import type { Etapa, ProcessoFilters } from '@/types/processos'

const processosKeys = {
  all: ['processos'] as const,
  list: (filters: ProcessoFilters) => [...processosKeys.all, 'list', filters] as const,
  detail: (id: string) => [...processosKeys.all, 'detail', id] as const,
}

export function useProcessos(filters: ProcessoFilters) {
  return useQuery({
    queryKey: processosKeys.list(filters),
    queryFn: () => listProcessos(filters),
  })
}

export function useProcesso(id: string) {
  return useQuery({
    queryKey: processosKeys.detail(id),
    queryFn: () => getProcesso(id),
    enabled: !!id,
  })
}

export function useMoverEtapa(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ etapa, observacao }: { etapa: Etapa; observacao?: string }) =>
      moverEtapa(id, etapa, observacao),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: processosKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: processosKeys.all })
    },
  })
}

// Variante do mover-etapa que recebe o id do processo a cada chamada, em vez
// de fixá-lo no momento de montar o hook — usada pelo drag-and-drop do
// Kanban, onde o card arrastado pode ser qualquer um da coluna.
export function useMoverEtapaDireto() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, etapa }: { id: string; etapa: Etapa }) => moverEtapa(id, etapa),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: processosKeys.detail(variables.id) })
      queryClient.invalidateQueries({ queryKey: processosKeys.all })
    },
  })
}
