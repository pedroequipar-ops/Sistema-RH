import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  alternarAtivoUsuario,
  atribuirPerfil,
  criarUsuario,
  editarUsuario,
  excluirUsuario,
  listUsuarios,
} from '@/api/usuarios'
import type { CriarUsuarioValues, EditarUsuarioValues } from '@/types/usuarios'

const usuariosKeys = {
  all: ['usuarios'] as const,
}

export function useUsuarios() {
  return useQuery({
    queryKey: usuariosKeys.all,
    queryFn: listUsuarios,
  })
}

export function useCriarUsuario() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (values: CriarUsuarioValues) => criarUsuario(values),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: usuariosKeys.all }),
  })
}

export function useEditarUsuario(usuarioId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (values: EditarUsuarioValues) => editarUsuario(usuarioId, values),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: usuariosKeys.all }),
  })
}

export function useAtribuirPerfil() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ usuarioId, perfil }: { usuarioId: string; perfil: string | null }) =>
      atribuirPerfil(usuarioId, perfil),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: usuariosKeys.all }),
  })
}

export function useAlternarAtivoUsuario() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ usuarioId, is_active }: { usuarioId: string; is_active: boolean }) =>
      alternarAtivoUsuario(usuarioId, is_active),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: usuariosKeys.all }),
  })
}

export function useExcluirUsuario() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (usuarioId: string) => excluirUsuario(usuarioId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: usuariosKeys.all }),
  })
}
