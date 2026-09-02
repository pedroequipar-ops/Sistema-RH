import type { PaginatedResponse } from '@/types/vagas'

export type Etapa = 'triagem' | 'teste' | 'entrevista' | 'proposta' | 'contratado' | 'reprovado'
export type TesteTipo = 'comportamental' | 'tecnico'
export type TesteStatus = 'pendente' | 'respondido' | 'avaliado'

export type HistoricoEtapaProcesso = {
  id: string
  de_etapa: string
  para_etapa: string
  alterado_por: string | null
  observacao: string
  created_at: string
}

export type ProcessoSeletivo = {
  id: string
  candidato: string
  candidato_nome: string
  candidato_email: string
  vaga: string
  vaga_cargo: string
  etapa_atual: Etapa
  historico_etapas: HistoricoEtapaProcesso[]
  created_at: string
  updated_at: string
  active: boolean
}

export type ProcessoFilters = {
  vaga?: string
  etapa_atual?: Etapa | ''
}

export type AvaliacaoProcesso = {
  id: string
  processo: string
  autor: string
  autor_nome: string
  nota: string | null
  comentario: string
  created_at: string
}

export type TesteAplicado = {
  id: string
  processo: string
  tipo: TesteTipo
  titulo: string
  perguntas: unknown[]
  respostas: Record<string, unknown>
  nota: string | null
  status: TesteStatus
  criado_por: string
  created_at: string
  updated_at: string
}

export type EntrevistaAgendamento = {
  id: string
  processo: string
  data_hora: string
  duracao_minutos: number
  local_ou_link: string
  observacoes: string
  criado_por: string
  created_at: string
  active: boolean
}

export type { PaginatedResponse }

export const ETAPA_LABEL: Record<Etapa, string> = {
  triagem: 'Triagem',
  teste: 'Teste',
  entrevista: 'Entrevista',
  proposta: 'Proposta',
  contratado: 'Contratado',
  reprovado: 'Reprovado',
}

export const ETAPA_ORDEM: Etapa[] = [
  'triagem',
  'teste',
  'entrevista',
  'proposta',
  'contratado',
  'reprovado',
]

// Espelha TRANSICOES_PERMITIDAS de apps/processos_seletivos/views.py — só
// para orientar a UI (o backend é quem valida de verdade).
export const TRANSICOES_PERMITIDAS: Record<Etapa, Etapa[]> = {
  triagem: ['teste', 'reprovado'],
  teste: ['entrevista', 'reprovado'],
  entrevista: ['proposta', 'reprovado'],
  proposta: ['contratado', 'reprovado'],
  contratado: [],
  reprovado: [],
}

export const TESTE_TIPO_LABEL: Record<TesteTipo, string> = {
  comportamental: 'Comportamental',
  tecnico: 'Técnico',
}

export const TESTE_STATUS_LABEL: Record<TesteStatus, string> = {
  pendente: 'Pendente',
  respondido: 'Respondido',
  avaliado: 'Avaliado',
}
