import type { PaginatedResponse } from '@/types/vagas'

export type EmailStatus = 'enviado' | 'falha'

export type EmailEnviado = {
  id: string
  tipo: string
  destinatario: string
  assunto: string
  candidato: string | null
  candidato_nome: string | null
  processo: string | null
  status: EmailStatus
  erro: string
  created_at: string
}

export type Notificacao = {
  id: string
  tipo: string
  mensagem: string
  lida: boolean
  processo: string | null
  dados: Record<string, unknown>
  created_at: string
}

export type EmailFilters = {
  status?: EmailStatus | ''
  tipo?: string
}

export type NotificacaoFilters = {
  lida?: 'true' | 'false' | ''
}

export const EMAIL_STATUS_LABEL: Record<EmailStatus, string> = {
  enviado: 'Enviado',
  falha: 'Falha',
}

export type { PaginatedResponse }
