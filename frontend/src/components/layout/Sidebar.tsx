import { PanelLeftClose, PanelLeftOpen } from 'lucide-react'
import { NavLink } from 'react-router-dom'

import { NAV_ITEMS } from '@/components/layout/navigation'
import { useAuth } from '@/context/AuthContext'
import { cn } from '@/lib/cn'

type SidebarProps = {
  collapsed: boolean
  onToggle: () => void
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { hasPermission } = useAuth()
  const items = NAV_ITEMS.filter((item) => !item.functionSlug || hasPermission(item.functionSlug, 'view'))

  return (
    <aside
      className={cn(
        'flex shrink-0 flex-col border-r border-slate-200 bg-white transition-[width] duration-200 ease-in-out',
        collapsed ? 'w-[68px]' : 'w-64',
      )}
    >
      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-3">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            title={collapsed ? item.label : undefined}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 overflow-hidden rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                collapsed && 'justify-center',
                isActive
                  ? 'bg-sapphire-50 text-sapphire-700'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
              )
            }
          >
            <item.icon className="h-4.5 w-4.5 shrink-0" aria-hidden />
            {!collapsed && <span className="whitespace-nowrap">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className={cn('flex border-t border-slate-200 p-3', collapsed ? 'justify-center' : 'justify-end')}>
        <button
          onClick={onToggle}
          aria-label={collapsed ? 'Expandir menu' : 'Recolher menu'}
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-slate-50 text-slate-500 hover:bg-slate-100 hover:text-slate-700"
        >
          {collapsed ? (
            <PanelLeftOpen className="h-4.5 w-4.5" aria-hidden />
          ) : (
            <PanelLeftClose className="h-4.5 w-4.5" aria-hidden />
          )}
        </button>
      </div>
    </aside>
  )
}
