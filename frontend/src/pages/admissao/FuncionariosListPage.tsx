import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { useFuncionarios } from '@/hooks/useAdmissao'
import { statusOnboardingTone } from '@/lib/admissaoStatus'
import { formatDateOnly } from '@/lib/date'
import { STATUS_ONBOARDING_LABEL, type FuncionarioFilters } from '@/types/admissao'

export function FuncionariosListPage() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<FuncionarioFilters>({ status_onboarding: '' })
  const { data, isLoading, isError } = useFuncionarios(filters)

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Admissão</h1>
        <p className="text-sm text-slate-500">Onboarding dos candidatos contratados.</p>
      </div>

      <Card className="p-4">
        <Select
          value={filters.status_onboarding}
          onChange={(event) =>
            setFilters({ status_onboarding: event.target.value as FuncionarioFilters['status_onboarding'] })
          }
          className="w-56"
        >
          <option value="">Status: todos</option>
          {Object.entries(STATUS_ONBOARDING_LABEL).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </Select>
      </Card>

      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner />
          </div>
        ) : isError ? (
          <p className="p-6 text-sm text-red-600">Não foi possível carregar os funcionários.</p>
        ) : data && data.results.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Candidato</th>
                  <th className="px-4 py-3 font-medium">Cargo</th>
                  <th className="px-4 py-3 font-medium">Data de admissão</th>
                  <th className="px-4 py-3 font-medium">Onboarding</th>
                  <th className="px-4 py-3 font-medium">Checklist</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.results.map((funcionario) => (
                  <tr
                    key={funcionario.id}
                    onClick={() => navigate(`/admissao/${funcionario.id}`)}
                    className="cursor-pointer hover:bg-slate-50"
                  >
                    <td className="px-4 py-3 font-medium text-slate-900">
                      {funcionario.candidato_nome}
                    </td>
                    <td className="px-4 py-3 text-slate-600">{funcionario.cargo || '—'}</td>
                    <td className="px-4 py-3 text-slate-600">
                      {funcionario.data_admissao ? formatDateOnly(funcionario.data_admissao) : '—'}
                    </td>
                    <td className="px-4 py-3">
                      <Badge tone={statusOnboardingTone(funcionario.status_onboarding)}>
                        {STATUS_ONBOARDING_LABEL[funcionario.status_onboarding]}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {funcionario.checklist.filter((i) => i.status === 'aprovado').length}/
                      {funcionario.checklist.length} aprovados
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="p-6 text-sm text-slate-500">Nenhum funcionário em onboarding ainda.</p>
        )}
      </Card>
    </div>
  )
}
