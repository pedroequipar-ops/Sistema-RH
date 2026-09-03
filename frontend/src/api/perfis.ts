import { apiClient } from '@/api/client'
import type { PaginatedResponse } from '@/types/vagas'
import type { CriarPerfilValues, Perfil, PerfilFunctionPermission } from '@/types/usuarios'

export async function listPerfis() {
  const { data } = await apiClient.get<PaginatedResponse<Perfil>>('/v1/perfis/', {
    params: { page_size: 100 },
  })
  return data
}

export async function criarPerfil(values: CriarPerfilValues) {
  const { data } = await apiClient.post<Perfil>('/v1/perfis/', values)
  return data
}

export async function editarPerfil(perfilId: string, values: CriarPerfilValues) {
  const { data } = await apiClient.patch<Perfil>(`/v1/perfis/${perfilId}/`, values)
  return data
}

export async function alternarAtivoPerfil(perfilId: string, ativo: boolean) {
  const { data } = await apiClient.patch<Perfil>(`/v1/perfis/${perfilId}/`, { ativo })
  return data
}

export async function atualizarPermissoesPerfil(
  perfilId: string,
  permissoes: PerfilFunctionPermission[],
) {
  const { data } = await apiClient.put<Perfil>(`/v1/perfis/${perfilId}/permissoes/`, permissoes)
  return data
}

export async function duplicarPerfil(perfilId: string) {
  const { data } = await apiClient.post<Perfil>(`/v1/perfis/${perfilId}/duplicar/`)
  return data
}

export async function excluirPerfil(perfilId: string) {
  await apiClient.delete(`/v1/perfis/${perfilId}/`)
}
