import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  aprovarVaga,
  cancelarVaga,
  createVaga,
  deleteVaga,
  getVaga,
  listVagas,
  pausarVaga,
  reprovarVaga,
  updateVaga,
} from '@/api/vagas'
import type { VagaFilters, VagaFormValues } from '@/types/vagas'

const vagasKeys = {
  all: ['vagas'] as const,
  list: (filters: VagaFilters) => [...vagasKeys.all, 'list', filters] as const,
  detail: (id: string) => [...vagasKeys.all, 'detail', id] as const,
}

export function useVagas(filters: VagaFilters) {
  return useQuery({
    queryKey: vagasKeys.list(filters),
    queryFn: () => listVagas(filters),
  })
}

export function useVaga(id: string) {
  return useQuery({
    queryKey: vagasKeys.detail(id),
    queryFn: () => getVaga(id),
    enabled: !!id,
  })
}

export function useCreateVaga() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (values: VagaFormValues) => createVaga(values),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: vagasKeys.all }),
  })
}

export function useUpdateVaga(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (values: Partial<VagaFormValues>) => updateVaga(id, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: vagasKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: vagasKeys.all })
    },
  })
}

export function useDeleteVaga() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteVaga(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: vagasKeys.all }),
  })
}

function useVagaAction(action: (id: string, observacao?: string) => Promise<unknown>, id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (observacao?: string) => action(id, observacao),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: vagasKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: vagasKeys.all })
    },
  })
}

export const useAprovarVaga = (id: string) => useVagaAction(aprovarVaga, id)
export const useReprovarVaga = (id: string) => useVagaAction(reprovarVaga, id)
export const usePausarVaga = (id: string) => useVagaAction(pausarVaga, id)
export const useCancelarVaga = (id: string) => useVagaAction(cancelarVaga, id)
