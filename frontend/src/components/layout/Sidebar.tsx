import { Building2 } from 'lucide-react'
import { NavLink } from 'react-router-dom'

import { NAV_ITEMS } from '@/components/layout/navigation'
import { useAuth } from '@/context/AuthContext'
import { cn } from '@/lib/cn'

export function Sidebar() {
  const { hasPermission } = useAuth()
  const items = NAV_ITEMS.filter((item) => !item.functionSlug || hasPermission(item.functionSlug, 'view'))

  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="flex items-center gap-2 px-5 py-5">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-sapphire-600 text-white">
          <Building2 className="h-5 w-5" aria-hidden />
        </span>
        <span className="text-sm font-semibold text-slate-900">Sistema RH</span>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sapphire-50 text-sapphire-700'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
              )
            }
          >
            <item.icon className="h-4.5 w-4.5" aria-hidden />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
