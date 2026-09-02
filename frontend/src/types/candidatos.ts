export type Senioridade = 'junior' | 'pleno' | 'senior'
export type CurriculoStatus = 'pendente' | 'processando' | 'processado' | 'falha'

export type Candidato = {
  id: string
  email: string
  nome: string
  telefone: string
  cidade: string
  cargo_pretendido: string
  senioridade: Senioridade | ''
  skills: string[]
  resumo_experiencia: string
  curriculo_status: CurriculoStatus
  curriculo_url: string | null
  created_at: string
  updated_at: string
  active: boolean
}

export type CandidatoFilters = {
  page?: number
  search?: string
  senioridade?: Senioridade | ''
  cidade?: string
  cargo_pretendido?: string
  skill?: string
}

export type Origem = 'manual' | 'motor_automatico'

export type PontuacaoCandidato = {
  id: string
  candidato: string
  funcao: string
  pontuacao: string
  origem: Origem
  avaliador: string | null
  avaliador_nome: string | null
  detalhes: Record<string, unknown>
  created_at: string
}

export const SENIORIDADE_LABEL: Record<Senioridade, string> = {
  junior: 'Júnior',
  pleno: 'Pleno',
  senior: 'Sênior',
}

export const CURRICULO_STATUS_LABEL: Record<CurriculoStatus, string> = {
  pendente: 'Pendente',
  processando: 'Processando',
  processado: 'Processado',
  falha: 'Falha ao processar',
}
