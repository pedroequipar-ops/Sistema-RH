import { LogOut, User as UserIcon } from 'lucide-react'

import { Badge } from '@/components/ui/Badge'
import { useAuth } from '@/context/AuthContext'

const ROLE_LABEL: Record<string, string> = {
  rh: 'RH',
  gestor: 'Gestor',
  diretoria: 'Diretoria',
}

export function Topbar() {
  const { user, logout } = useAuth()

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
      <div />
      <div className="flex items-center gap-3">
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
