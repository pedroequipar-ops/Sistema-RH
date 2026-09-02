import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { useAuth } from '@/context/AuthContext'

export function DashboardPage() {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Olá, {user?.full_name}</h1>
        <p className="text-sm text-slate-500">Visão geral do processo de recrutamento.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Base do frontend concluída</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-slate-600">
          Autenticação, layout e navegação por permissão estão prontos. Os módulos de vagas,
          candidatos, processos seletivos, comunicações, relatórios e admissão serão implementados
          nas próximas etapas.
        </CardContent>
      </Card>
    </div>
  )
}
