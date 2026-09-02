import type { StatusAprovacao, StatusOperacional } from '@/types/vagas'

export function statusAprovacaoTone(status: StatusAprovacao) {
  switch (status) {
    case 'aprovada':
      return 'green' as const
    case 'reprovada':
      return 'red' as const
    default:
      return 'amber' as const
  }
}

export function statusOperacionalTone(status: StatusOperacional) {
  switch (status) {
    case 'aberta':
    case 'em_andamento':
      return 'green' as const
    case 'pausada':
      return 'amber' as const
    case 'cancelada':
      return 'red' as const
    case 'fechada':
      return 'slate' as const
    default:
      return 'slate' as const
  }
}
