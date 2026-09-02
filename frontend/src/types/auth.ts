export type Role = 'rh' | 'gestor' | 'diretoria'

export type FunctionPermission = {
  function: string
  can_view: boolean
  can_create: boolean
  can_edit: boolean
  can_delete: boolean
}

export type CurrentUser = {
  id: string
  email: string
  full_name: string
  role: Role
  area: string
  company_id: string
  is_superuser: boolean
  function_permissions: FunctionPermission[]
}
