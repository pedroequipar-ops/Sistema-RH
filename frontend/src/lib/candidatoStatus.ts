import type { CurriculoStatus } from '@/types/candidatos'

export function curriculoStatusTone(status: CurriculoStatus) {
  switch (status) {
    case 'processado':
      return 'green' as const
    case 'falha':
      return 'red' as const
    case 'processando':
      return 'amber' as const
    default:
      return 'slate' as const
  }
}
