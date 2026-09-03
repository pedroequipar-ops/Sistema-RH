import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  alternarAtivoPerfil,
  atualizarPermissoesPerfil,
  criarPerfil,
  duplicarPerfil,
  editarPerfil,
  excluirPerfil,
  listPerfis,
} from '@/api/perfis'
import type { CriarPerfilValues, PerfilFunctionPermission } from '@/types/usuarios'

const perfisKeys = {
  all: ['perfis'] as const,
}

export function usePerfis() {
  return useQuery({
    queryKey: perfisKeys.all,
    queryFn: listPerfis,
  })
}

export function useCriarPerfil() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (values: CriarPerfilValues) => criarPerfil(values),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: perfisKeys.all }),
  })
}

export function useEditarPerfil(perfilId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (values: CriarPerfilValues) => editarPerfil(perfilId, values),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: perfisKeys.all }),
  })
}

export function useAlternarAtivoPerfil() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ perfilId, ativo }: { perfilId: string; ativo: boolean }) =>
      alternarAtivoPerfil(perfilId, ativo),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: perfisKeys.all }),
  })
}

export function useAtualizarPermissoesPerfil(perfilId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (permissoes: PerfilFunctionPermission[]) =>
      atualizarPermissoesPerfil(perfilId, permissoes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: perfisKeys.all })
      queryClient.invalidateQueries({ queryKey: ['usuarios'] })
    },
  })
}

export function useDuplicarPerfil() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (perfilId: string) => duplicarPerfil(perfilId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: perfisKeys.all }),
  })
}

export function useExcluirPerfil() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (perfilId: string) => excluirPerfil(perfilId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: perfisKeys.all }),
  })
}
