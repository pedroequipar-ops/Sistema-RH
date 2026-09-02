import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { getFuncionario, listFuncionarios, revisarChecklistItem, updateFuncionario } from '@/api/admissao'
import type { ChecklistStatus, FuncionarioFilters } from '@/types/admissao'

const funcionariosKeys = {
  all: ['funcionarios'] as const,
  list: (filters: FuncionarioFilters) => [...funcionariosKeys.all, 'list', filters] as const,
  detail: (id: string) => [...funcionariosKeys.all, 'detail', id] as const,
}

export function useFuncionarios(filters: FuncionarioFilters) {
  return useQuery({
    queryKey: funcionariosKeys.list(filters),
    queryFn: () => listFuncionarios(filters),
  })
}

export function useFuncionario(id: string) {
  return useQuery({
    queryKey: funcionariosKeys.detail(id),
    queryFn: () => getFuncionario(id),
    enabled: !!id,
  })
}

export function useUpdateFuncionario(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (dataAdmissao: string) => updateFuncionario(id, dataAdmissao),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: funcionariosKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: funcionariosKeys.all })
    },
  })
}

export function useRevisarChecklistItem(funcionarioId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status, observacao }: { id: string; status: ChecklistStatus; observacao: string }) =>
      revisarChecklistItem(id, status, observacao),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: funcionariosKeys.detail(funcionarioId) })
      queryClient.invalidateQueries({ queryKey: funcionariosKeys.all })
    },
  })
}
