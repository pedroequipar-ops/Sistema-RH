export type Usuario = {
  id: string
  email: string
  full_name: string
  area: string
  perfil: string | null
  perfil_nome: string | null
  is_active: boolean
}

export type CriarUsuarioValues = {
  email: string
  full_name: string
  password: string
}

export type EditarUsuarioValues = {
  full_name: string
  email: string
  area: string
}

export type ModuloSlug =
  | 'vagas'
  | 'candidatos'
  | 'processos-seletivos'
  | 'comunicacoes'
  | 'relatorios'
  | 'admissao'

export const MODULOS: { slug: ModuloSlug; label: string }[] = [
  { slug: 'vagas', label: 'Vagas' },
  { slug: 'candidatos', label: 'Candidatos' },
  { slug: 'processos-seletivos', label: 'Processos seletivos' },
  { slug: 'comunicacoes', label: 'Comunicações' },
  { slug: 'relatorios', label: 'Relatórios' },
  { slug: 'admissao', label: 'Admissão' },
]

export type PerfilTipo = 'sistema' | 'personalizado'

export type PerfilFunctionPermission = {
  function: ModuloSlug
  can_view: boolean
  can_create: boolean
  can_edit: boolean
  can_delete: boolean
}

export type Perfil = {
  id: string
  nome: string
  slug: string
  descricao: string
  tipo: PerfilTipo
  ativo: boolean
  usuarios_count: number
  function_permissions: PerfilFunctionPermission[]
}

export type CriarPerfilValues = {
  nome: string
  descricao: string
}
