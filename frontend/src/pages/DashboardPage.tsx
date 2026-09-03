import { useQuery } from '@tanstack/react-query'
import { Briefcase, KanbanSquare, UserCheck, Users, type LucideIcon } from 'lucide-react'
import { useState } from 'react'

import { listFuncionarios } from '@/api/admissao'
import { listCandidatos } from '@/api/candidatos'
import { listProcessos } from '@/api/processos'
import { listVagas, listVagasParaFiltro } from '@/api/vagas'
import { Card, CardContent } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { useAuth } from '@/context/AuthContext'
import { STATUS_ONBOARDING_LABEL, type StatusOnboarding } from '@/types/admissao'
import { SENIORIDADE_LABEL, type Senioridade } from '@/types/candidatos'
import { ETAPA_LABEL, type Etapa } from '@/types/processos'

const REFETCH_MS = 30_000

type StatCardProps = {
  icon: LucideIcon
  label: string
  value: number | undefined
  loading: boolean
  isError: boolean
}

function StatCard({ icon: Icon, label, value, loading, isError }: StatCardProps) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-sapphire-50">
          <Icon className="h-5 w-5 text-sapphire-600" aria-hidden />
        </span>
        <div>
          <p className="text-xs font-medium text-slate-500">{label}</p>
          {loading ? (
            <Spinner className="mt-1 h-4 w-4" />
          ) : isError ? (
            <p className="text-sm text-red-600">Erro ao carregar</p>
          ) : (
            <p className="text-2xl font-semibold text-slate-900">{value}</p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export function DashboardPage() {
  const { user, hasPermission } = useAuth()

  const podeVerVagas = hasPermission('vagas', 'view')
  const podeVerCandidatos = hasPermission('candidatos', 'view')
  const podeVerProcessos = hasPermission('processos-seletivos', 'view')
  const podeVerAdmissao = hasPermission('admissao', 'view')
  const nenhumaPermissao = !podeVerVagas && !podeVerCandidatos && !podeVerProcessos && !podeVerAdmissao

  const [vagaId, setVagaId] = useState('')
  const [etapa, setEtapa] = useState<Etapa | ''>('')
  const [senioridade, setSenioridade] = useState<Senioridade | ''>('')
  const [statusOnboarding, setStatusOnboarding] = useState<StatusOnboarding | ''>('')

  const { data: vagasFiltro } = useQuery({
    queryKey: ['vagas-filtro'],
    queryFn: listVagasParaFiltro,
    enabled: podeVerVagas,
  })

  const vagasAbertas = useQuery({
    queryKey: ['dashboard-vagas-abertas'],
    queryFn: () => listVagas({ status: 'aberta' }),
    enabled: podeVerVagas,
    refetchInterval: REFETCH_MS,
  })

  const candidatos = useQuery({
    queryKey: ['dashboard-candidatos', senioridade],
    queryFn: () => listCandidatos({ senioridade }),
    enabled: podeVerCandidatos,
    refetchInterval: REFETCH_MS,
  })

  const processos = useQuery({
    queryKey: ['dashboard-processos', vagaId, etapa],
    queryFn: () => listProcessos({ vaga: vagaId, etapa_atual: etapa }),
    enabled: podeVerProcessos,
    refetchInterval: REFETCH_MS,
  })

  const funcionarios = useQuery({
    queryKey: ['dashboard-funcionarios', statusOnboarding],
    queryFn: () => listFuncionarios({ status_onboarding: statusOnboarding }),
    enabled: podeVerAdmissao,
    refetchInterval: REFETCH_MS,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Olá, {user?.full_name}</h1>
        <p className="text-sm text-slate-500">Visão geral do processo de recrutamento.</p>
      </div>

      {nenhumaPermissao ? (
        <Card>
          <CardContent className="text-sm text-slate-600">
            Sua conta ainda não tem permissão de acesso a nenhum módulo. Fale com o RH para liberar
            seu perfil.
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="flex flex-wrap gap-3">
            {podeVerProcessos && (
              <Select
                value={vagaId}
                onChange={(event) => setVagaId(event.target.value)}
                className="w-52"
                aria-label="Filtrar por vaga"
              >
                <option value="">Todas as vagas</option>
                {vagasFiltro?.results.map((vaga) => (
                  <option key={vaga.id} value={vaga.id}>
                    {vaga.cargo}
                  </option>
                ))}
              </Select>
            )}
            {podeVerProcessos && (
              <Select
                value={etapa}
                onChange={(event) => setEtapa(event.target.value as Etapa | '')}
                className="w-44"
                aria-label="Filtrar por etapa"
              >
                <option value="">Todas as etapas</option>
                {Object.entries(ETAPA_LABEL).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </Select>
            )}
            {podeVerCandidatos && (
              <Select
                value={senioridade}
                onChange={(event) => setSenioridade(event.target.value as Senioridade | '')}
                className="w-44"
                aria-label="Filtrar por senioridade"
              >
                <option value="">Toda senioridade</option>
                {Object.entries(SENIORIDADE_LABEL).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </Select>
            )}
            {podeVerAdmissao && (
              <Select
                value={statusOnboarding}
                onChange={(event) => setStatusOnboarding(event.target.value as StatusOnboarding | '')}
                className="w-48"
                aria-label="Filtrar por status de onboarding"
              >
                <option value="">Todo onboarding</option>
                {Object.entries(STATUS_ONBOARDING_LABEL).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </Select>
            )}
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {podeVerVagas && (
              <StatCard
                icon={Briefcase}
                label="Vagas abertas"
                value={vagasAbertas.data?.count}
                loading={vagasAbertas.isLoading}
                isError={vagasAbertas.isError}
              />
            )}
            {podeVerCandidatos && (
              <StatCard
                icon={Users}
                label="Candidatos"
                value={candidatos.data?.count}
                loading={candidatos.isLoading}
                isError={candidatos.isError}
              />
            )}
            {podeVerProcessos && (
              <StatCard
                icon={KanbanSquare}
                label="Processos ativos"
                value={processos.data?.count}
                loading={processos.isLoading}
                isError={processos.isError}
              />
            )}
            {podeVerAdmissao && (
              <StatCard
                icon={UserCheck}
                label="Funcionários em admissão"
                value={funcionarios.data?.count}
                loading={funcionarios.isLoading}
                isError={funcionarios.isError}
              />
            )}
          </div>
        </>
      )}
    </div>
  )
}
