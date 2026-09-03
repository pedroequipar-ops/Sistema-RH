import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  contarNotificacoesNaoLidas,
  limparNotificacoes,
  listEmails,
  listNotificacoes,
  marcarNotificacaoLida,
} from '@/api/comunicacoes'
import type { EmailFilters, NotificacaoFilters } from '@/types/comunicacoes'

export function useEmails(filters: EmailFilters) {
  return useQuery({
    queryKey: ['emails-enviados', filters],
    queryFn: () => listEmails(filters),
  })
}

export function useNotificacoes(filters: NotificacaoFilters) {
  return useQuery({
    queryKey: ['notificacoes', filters],
    queryFn: () => listNotificacoes(filters),
  })
}

export function useMarcarNotificacaoLida() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => marcarNotificacaoLida(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notificacoes'] })
      queryClient.invalidateQueries({ queryKey: ['notificacoes-nao-lidas'] })
    },
  })
}

export function useLimparNotificacoes() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => limparNotificacoes(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notificacoes'] })
      queryClient.invalidateQueries({ queryKey: ['notificacoes-nao-lidas'] })
    },
  })
}

export function useNotificacoesNaoLidasCount({ enabled }: { enabled: boolean }) {
  return useQuery({
    queryKey: ['notificacoes-nao-lidas'],
    queryFn: contarNotificacoesNaoLidas,
    refetchInterval: 30_000,
    enabled,
  })
}
