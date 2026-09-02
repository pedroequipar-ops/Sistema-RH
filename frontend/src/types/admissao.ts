import type { PaginatedResponse } from '@/types/vagas'

export type StatusOnboarding = 'documentos_pendentes' | 'em_analise' | 'concluido'
export type ChecklistStatus = 'pendente' | 'enviado' | 'aprovado' | 'rejeitado'

export type ChecklistItemAdmissao = {
  id: string
  funcionario: string
  nome_documento: string
  obrigatorio: boolean
  status: ChecklistStatus
  documento_url: string | null
  observacao: string
  revisado_por: string | null
  created_at: string
  updated_at: string
}

export type Funcionario = {
  id: string
  processo: string
  candidato: string
  candidato_nome: string
  vaga: string
  cargo: string
  data_admissao: string | null
  status_onboarding: StatusOnboarding
  checklist: ChecklistItemAdmissao[]
  created_at: string
  updated_at: string
  active: boolean
}

export type FuncionarioFilters = {
  status_onboarding?: StatusOnboarding | ''
}

export const STATUS_ONBOARDING_LABEL: Record<StatusOnboarding, string> = {
  documentos_pendentes: 'Documentos pendentes',
  em_analise: 'Em análise',
  concluido: 'Concluído',
}

export const CHECKLIST_STATUS_LABEL: Record<ChecklistStatus, string> = {
  pendente: 'Pendente',
  enviado: 'Enviado',
  aprovado: 'Aprovado',
  rejeitado: 'Rejeitado',
}

export type { PaginatedResponse }
