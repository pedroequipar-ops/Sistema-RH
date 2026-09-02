import { Plus, Search } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { useAuth } from '@/context/AuthContext'
import { useVagas } from '@/hooks/useVagas'
import { statusAprovacaoTone, statusOperacionalTone } from '@/lib/vagaStatus'
import {
  STATUS_APROVACAO_LABEL,
  STATUS_OPERACIONAL_LABEL,
  TIPO_VAGA_LABEL,
  type VagaFilters,
} from '@/types/vagas'

const initialFilters: VagaFilters = { page: 1, search: '', status: '', status_aprovacao: '', tipo: '' }

export function VagasListPage() {
  const { hasPermission } = useAuth()
  const navigate = useNavigate()
  const [filters, setFilters] = useState<VagaFilters>(initialFilters)
  const { data, isLoading, isError } = useVagas(filters)

  function updateFilter<K extends keyof VagaFilters>(key: K, value: VagaFilters[K]) {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }))
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Vagas</h1>
          <p className="text-sm text-slate-500">Abertura, aprovação e acompanhamento de vagas.</p>
        </div>
        {hasPermission('vagas', 'create') && (
          <Link to="/vagas/nova">
            <Button>
              <Plus className="h-4 w-4" aria-hidden />
              Nova vaga
            </Button>
          </Link>
        )}
      </div>

      <Card className="p-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="relative">
            <Search
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
              aria-hidden
            />
            <Input
              placeholder="Buscar por cargo..."
              className="pl-9"
              value={filters.search}
              onChange={(event) => updateFilter('search', event.target.value)}
            />
          </div>
          <Select
            value={filters.status}
            onChange={(event) => updateFilter('status', event.target.value as VagaFilters['status'])}
          >
            <option value="">Status: todos</option>
            {Object.entries(STATUS_OPERACIONAL_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </Select>
          <Select
            value={filters.status_aprovacao}
            onChange={(event) =>
              updateFilter('status_aprovacao', event.target.value as VagaFilters['status_aprovacao'])
            }
          >
            <option value="">Aprovação: todas</option>
            {Object.entries(STATUS_APROVACAO_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </Select>
          <Select
            value={filters.tipo}
            onChange={(event) => updateFilter('tipo', event.target.value as VagaFilters['tipo'])}
          >
            <option value="">Tipo: todos</option>
            {Object.entries(TIPO_VAGA_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </Select>
        </div>
      </Card>

      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner />
          </div>
        ) : isError ? (
          <p className="p-6 text-sm text-red-600">Não foi possível carregar as vagas.</p>
        ) : data && data.results.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Cargo</th>
                  <th className="px-4 py-3 font-medium">Área</th>
                  <th className="px-4 py-3 font-medium">Tipo</th>
                  <th className="px-4 py-3 font-medium">Aprovação</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Solicitante</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.results.map((vaga) => (
                  <tr
                    key={vaga.id}
                    onClick={() => navigate(`/vagas/${vaga.id}`)}
                    className="cursor-pointer hover:bg-slate-50"
                  >
                    <td className="px-4 py-3">
                      <span className="font-medium text-slate-900">{vaga.cargo}</span>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{vaga.area_solicitante}</td>
                    <td className="px-4 py-3 text-slate-600">{TIPO_VAGA_LABEL[vaga.tipo]}</td>
                    <td className="px-4 py-3">
                      <Badge tone={statusAprovacaoTone(vaga.status_aprovacao)}>
                        {STATUS_APROVACAO_LABEL[vaga.status_aprovacao]}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Badge tone={statusOperacionalTone(vaga.status)}>
                        {STATUS_OPERACIONAL_LABEL[vaga.status]}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{vaga.solicitante_nome}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="p-6 text-sm text-slate-500">Nenhuma vaga encontrada.</p>
        )}
      </Card>

      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-between text-sm text-slate-500">
          <span>
            Página {data.current_page} de {data.total_pages} · {data.count} vagas
          </span>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              disabled={!data.previous}
              onClick={() => setFilters((prev) => ({ ...prev, page: (prev.page ?? 1) - 1 }))}
            >
              Anterior
            </Button>
            <Button
              variant="secondary"
              disabled={!data.next}
              onClick={() => setFilters((prev) => ({ ...prev, page: (prev.page ?? 1) + 1 }))}
            >
              Próxima
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
