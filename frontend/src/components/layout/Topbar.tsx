import { Bell, LogOut, User as UserIcon } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Badge } from '@/components/ui/Badge'
import { useAuth } from '@/context/AuthContext'
import { useNotificacoesNaoLidasCount } from '@/hooks/useComunicacoes'

const ROLE_LABEL: Record<string, string> = {
  rh: 'RH',
  gestor: 'Gestor',
  diretoria: 'Diretoria',
}

export function Topbar() {
  const { user, hasPermission, logout } = useAuth()
  const podeVerNotificacoes = hasPermission('comunicacoes', 'view')
  const { data: naoLidas } = useNotificacoesNaoLidasCount({ enabled: podeVerNotificacoes })

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
      <div />
      <div className="flex items-center gap-3">
        {podeVerNotificacoes && (
          <Link
            to="/comunicacoes?tab=notificacoes"
            aria-label={naoLidas ? `Notificações, ${naoLidas} não lidas` : 'Notificações'}
            className="relative flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-700"
          >
            <Bell className="h-4.5 w-4.5" aria-hidden />
            {!!naoLidas && (
              <span className="absolute right-1 top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-semibold text-white">
                {naoLidas > 9 ? '9+' : naoLidas}
              </span>
            )}
          </Link>
        )}
        {user && (
          <>
            <Badge tone="sapphire">{ROLE_LABEL[user.role] ?? user.role}</Badge>
            <div className="flex items-center gap-2 text-sm text-slate-700">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100">
                <UserIcon className="h-4 w-4 text-slate-500" aria-hidden />
              </span>
              {user.full_name}
            </div>
          </>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm text-slate-500 hover:bg-slate-100 hover:text-slate-700"
        >
          <LogOut className="h-4 w-4" aria-hidden />
          Sair
        </button>
      </div>
    </header>
  )
}
