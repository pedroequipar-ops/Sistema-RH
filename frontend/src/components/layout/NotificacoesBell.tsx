import { Bell } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

import { Spinner } from '@/components/ui/Spinner'
import { useMarcarNotificacaoLida, useNotificacoes, useNotificacoesNaoLidasCount } from '@/hooks/useComunicacoes'
import { cn } from '@/lib/cn'

export function NotificacoesBell() {
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const { data: naoLidas } = useNotificacoesNaoLidasCount({ enabled: true })
  const { data, isLoading, isError } = useNotificacoes({ lida: '' })
  const marcarLida = useMarcarNotificacaoLida()

  useEffect(() => {
    if (!open) return
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [open])

  return (
    <div className="relative" ref={containerRef}>
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label={naoLidas ? `Notificações, ${naoLidas} não lidas` : 'Notificações'}
        aria-expanded={open}
        className="relative flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-700"
      >
        <Bell className="h-4.5 w-4.5" aria-hidden />
        {!!naoLidas && (
          <span className="absolute right-1 top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-semibold text-white">
            {naoLidas > 9 ? '9+' : naoLidas}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full z-20 mt-2 w-80 rounded-xl border border-slate-200 bg-white shadow-lg">
          <div className="border-b border-slate-200 px-4 py-3">
            <p className="text-sm font-semibold text-slate-900">Notificações</p>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : isError ? (
              <p className="p-4 text-sm text-red-600">Não foi possível carregar as notificações.</p>
            ) : data && data.results.length > 0 ? (
              <ul className="divide-y divide-slate-100">
                {data.results.map((notificacao) => (
                  <li key={notificacao.id} className={cn('px-4 py-3', !notificacao.lida && 'bg-sapphire-50/50')}>
                    <p className={cn('text-sm', notificacao.lida ? 'text-slate-600' : 'font-medium text-slate-900')}>
                      {notificacao.mensagem}
                    </p>
                    <div className="mt-1 flex items-center justify-between">
                      <p className="text-xs text-slate-400">
                        {new Date(notificacao.created_at).toLocaleString('pt-BR')}
                      </p>
                      {!notificacao.lida && (
                        <button
                          onClick={() => marcarLida.mutate(notificacao.id)}
                          disabled={marcarLida.isPending}
                          className="text-xs font-medium text-sapphire-600 hover:text-sapphire-700 disabled:opacity-50"
                        >
                          Marcar como lida
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="p-4 text-sm text-slate-500">Nenhuma notificação encontrada.</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
