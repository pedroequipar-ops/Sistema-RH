import { FileText, Search } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { useCandidatos } from '@/hooks/useCandidatos'
import { curriculoStatusTone } from '@/lib/candidatoStatus'
import {
  CURRICULO_STATUS_LABEL,
  SENIORIDADE_LABEL,
  type CandidatoFilters,
} from '@/types/candidatos'

const initialFilters: CandidatoFilters = {
  page: 1,
  search: '',
  senioridade: '',
  cidade: '',
  cargo_pretendido: '',
  skill: '',
}

export function CandidatosListPage() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<CandidatoFilters>(initialFilters)
  const { data, isLoading, isError } = useCandidatos(filters)

  function updateFilter<K extends keyof CandidatoFilters>(key: K, value: CandidatoFilters[K]) {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }))
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Candidatos</h1>
        <p className="text-sm text-slate-500">
          Banco de talentos da empresa. Candidatos entram pela candidatura pública ou pelo envio de
          currículo.
        </p>
      </div>

      <Card className="p-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="relative">
            <Search
              className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
              aria-hidden
            />
            <Input
              placeholder="Buscar por nome..."
              className="pl-9"
              value={filters.search}
              onChange={(event) => updateFilter('search', event.target.value)}
            />
          </div>
          <Select
            value={filters.senioridade}
            onChange={(event) =>
              updateFilter('senioridade', event.target.value as CandidatoFilters['senioridade'])
            }
          >
            <option value="">Senioridade: todas</option>
            {Object.entries(SENIORIDADE_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </Select>
          <Input
            placeholder="Cidade..."
            value={filters.cidade}
            onChange={(event) => updateFilter('cidade', event.target.value)}
          />
          <Input
            placeholder="Skill (ex: python)..."
            value={filters.skill}
            onChange={(event) => updateFilter('skill', event.target.value)}
          />
        </div>
      </Card>

      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner />
          </div>
        ) : isError ? (
          <p className="p-6 text-sm text-red-600">Não foi possível carregar os candidatos.</p>
        ) : data && data.results.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Nome</th>
                  <th className="px-4 py-3 font-medium">Cargo pretendido</th>
                  <th className="px-4 py-3 font-medium">Senioridade</th>
                  <th className="px-4 py-3 font-medium">Cidade</th>
                  <th className="px-4 py-3 font-medium">Skills</th>
                  <th className="px-4 py-3 font-medium">Currículo</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.results.map((candidato) => (
                  <tr
                    key={candidato.id}
                    onClick={() => navigate(`/candidatos/${candidato.id}`)}
                    className="cursor-pointer hover:bg-slate-50"
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-900">{candidato.nome || '(sem nome)'}</p>
                      <p className="text-xs text-slate-500">{candidato.email}</p>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{candidato.cargo_pretendido || '—'}</td>
                    <td className="px-4 py-3 text-slate-600">
                      {candidato.senioridade ? SENIORIDADE_LABEL[candidato.senioridade] : '—'}
                    </td>
                    <td className="px-4 py-3 text-slate-600">{candidato.cidade || '—'}</td>
                    <td className="px-4 py-3">
                      <div className="flex max-w-56 flex-wrap gap-1">
                        {candidato.skills.slice(0, 3).map((skill) => (
                          <Badge key={skill} tone="slate">
                            {skill}
                          </Badge>
                        ))}
                        {candidato.skills.length > 3 && (
                          <Badge tone="slate">+{candidato.skills.length - 3}</Badge>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge tone={curriculoStatusTone(candidato.curriculo_status)}>
                        <FileText className="mr-1 h-3 w-3" aria-hidden />
                        {CURRICULO_STATUS_LABEL[candidato.curriculo_status]}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="p-6 text-sm text-slate-500">Nenhum candidato encontrado.</p>
        )}
      </Card>

      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-between text-sm text-slate-500">
          <span>
            Página {data.current_page} de {data.total_pages} · {data.count} candidatos
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
