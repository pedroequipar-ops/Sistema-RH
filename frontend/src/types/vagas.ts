export type StatusAprovacao = 'aguardando_rh' | 'aguardando_diretoria' | 'aprovada' | 'reprovada'
export type StatusOperacional = 'aberta' | 'em_andamento' | 'pausada' | 'fechada' | 'cancelada'
export type TipoVaga = 'interna' | 'externa'

export type HistoricoStatusVaga = {
  id: string
  tipo_status: 'aprovacao' | 'operacional'
  de_status: string
  para_status: string
  alterado_por: string | null
  alterado_por_nome: string | null
  observacao: string
  created_at: string
}

export type Vaga = {
  id: string
  cargo: string
  descricao: string
  requisitos: string
  salario: string | null
  area_solicitante: string
  tipo: TipoVaga
  status: StatusOperacional
  status_aprovacao: StatusAprovacao
  solicitante: string
  solicitante_nome: string
  custo_contratacao: string | null
  historico: HistoricoStatusVaga[]
  created_at: string
  updated_at: string
  active: boolean
}

export type VagaListItem = Omit<Vaga, 'historico'>

export type PaginatedResponse<T> = {
  count: number
  total_pages: number
  current_page: number
  page_size: number
  next: string | null
  previous: string | null
  results: T[]
}

export type VagaFilters = {
  page?: number
  search?: string
  status?: StatusOperacional | ''
  status_aprovacao?: StatusAprovacao | ''
  tipo?: TipoVaga | ''
}

export type VagaFormValues = {
  cargo: string
  descricao: string
  requisitos: string
  salario: string
  area_solicitante: string
  tipo: TipoVaga
}

export const STATUS_APROVACAO_LABEL: Record<StatusAprovacao, string> = {
  aguardando_rh: 'Aguardando RH',
  aguardando_diretoria: 'Aguardando diretoria',
  aprovada: 'Aprovada',
  reprovada: 'Reprovada',
}

export const STATUS_OPERACIONAL_LABEL: Record<StatusOperacional, string> = {
  aberta: 'Aberta',
  em_andamento: 'Em andamento',
  pausada: 'Pausada',
  fechada: 'Fechada',
  cancelada: 'Cancelada',
}

export const TIPO_VAGA_LABEL: Record<TipoVaga, string> = {
  interna: 'Interna',
  externa: 'Externa',
}
