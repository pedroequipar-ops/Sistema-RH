import { ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Card, CardContent } from '@/components/ui/Card'
import { NAV_ITEMS } from '@/components/layout/navigation'
import { useAuth } from '@/context/AuthContext'

export function DashboardPage() {
  const { user, hasPermission } = useAuth()
  const atalhos = NAV_ITEMS.filter(
    (item) => item.functionSlug && hasPermission(item.functionSlug, 'view'),
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Olá, {user?.full_name}</h1>
        <p className="text-sm text-slate-500">Visão geral do processo de recrutamento.</p>
      </div>

      {atalhos.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {atalhos.map((item) => (
            <Link key={item.to} to={item.to}>
              <Card className="flex h-full items-center gap-3 p-4 transition-colors hover:border-sapphire-300">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-sapphire-50">
                  <item.icon className="h-5 w-5 text-sapphire-600" aria-hidden />
                </span>
                <span className="flex-1 text-sm font-medium text-slate-800">{item.label}</span>
                <ChevronRight className="h-4 w-4 text-slate-400" aria-hidden />
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="text-sm text-slate-600">
            Sua conta ainda não tem permissão de acesso a nenhum módulo. Fale com o RH para liberar
            seu perfil.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
