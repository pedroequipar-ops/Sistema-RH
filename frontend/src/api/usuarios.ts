import { apiClient } from '@/api/client'
import type { PaginatedResponse } from '@/types/vagas'
import type { CriarUsuarioValues, EditarUsuarioValues, Usuario } from '@/types/usuarios'

export async function listUsuarios() {
  const { data } = await apiClient.get<PaginatedResponse<Usuario>>('/v1/usuarios/', {
    params: { page_size: 100 },
  })
  return data
}

export async function criarUsuario(values: CriarUsuarioValues) {
  const { data } = await apiClient.post<Usuario>('/v1/usuarios/', values)
  return data
}

export async function editarUsuario(usuarioId: string, values: EditarUsuarioValues) {
  const { data } = await apiClient.patch<Usuario>(`/v1/usuarios/${usuarioId}/`, values)
  return data
}

export async function atribuirPerfil(usuarioId: string, perfil: string | null) {
  const { data } = await apiClient.patch<Usuario>(`/v1/usuarios/${usuarioId}/`, { perfil })
  return data
}

export async function alternarAtivoUsuario(usuarioId: string, is_active: boolean) {
  const { data } = await apiClient.patch<Usuario>(`/v1/usuarios/${usuarioId}/`, { is_active })
  return data
}

export async function excluirUsuario(usuarioId: string) {
  await apiClient.delete(`/v1/usuarios/${usuarioId}/`)
}
