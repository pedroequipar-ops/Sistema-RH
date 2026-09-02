import type { ChecklistStatus, StatusOnboarding } from '@/types/admissao'

export function statusOnboardingTone(status: StatusOnboarding) {
  switch (status) {
    case 'concluido':
      return 'green' as const
    case 'em_analise':
      return 'amber' as const
    default:
      return 'slate' as const
  }
}

export function checklistStatusTone(status: ChecklistStatus) {
  switch (status) {
    case 'aprovado':
      return 'green' as const
    case 'rejeitado':
      return 'red' as const
    case 'enviado':
      return 'amber' as const
    default:
      return 'slate' as const
  }
}
