import { useQuery } from '@tanstack/react-query'
import { Clock, DollarSign, TrendingDown, Users } from 'lucide-react'
import { useState } from 'react'

import { listVagasParaFiltro } from '@/api/vagas'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import {
  useCandidatosPorVaga,
  useCustoContratacao,
  useFunilConversao,
  useTempoMedioContratacao,
} from '@/hooks/useRelatorios'
import { ETAPA_LABEL, type Etapa } from '@/types/processos'

function formatMoeda(valor: string | number | null) {
  if (valor === null) return '—'
  return Number(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function RelatoriosPage() {
  const [vagaId, setVagaId] = useState('')
  const { data: vagas } = useQuery({ queryKey: ['vagas-filtro'], queryFn: listVagasParaFiltro })

  const tempoMedio = useTempoMedioContratacao(vagaId)
  const candidatosPorVaga = useCandidatosPorVaga()
  const funilConversao = useFunilConversao()
  const custoContratacao = useCustoContratacao()

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Relatórios</h1>
        <p className="text-sm text-slate-500">Indicadores do processo de recrutamento e seleção.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-sapphire-600" aria-hidden />
              Tempo médio de contratação
            </CardTitle>
            <Select value={vagaId} onChange={(event) => setVagaId(event.target.value)} className="w-44">
              <option value="">Todas as vagas</option>
              {vagas?.results.map((vaga) => (
                <option key={vaga.id} value={vaga.id}>
                  {vaga.cargo}
                </option>
              ))}
            </Select>
          </CardHeader>
          <CardContent>
            {tempoMedio.isLoading ? (
              <Spinner />
            ) : (
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-semibold text-slate-900">
                  {tempoMedio.data?.tempo_medio_dias ?? '—'}
                </span>
                <span className="text-sm text-slate-500">
                  dias · {tempoMedio.data?.total_contratacoes ?? 0} contratações
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-sapphire-600" aria-hidden />
              Custo de contratação
            </CardTitle>
          </CardHeader>
          <CardContent>
            {custoContratacao.isLoading ? (
              <Spinner />
            ) : (
              <div className="space-y-3">
                <div className="flex gap-6">
                  <div>
                    <p className="text-xs text-slate-500">Custo médio</p>
                    <p className="text-xl font-semibold text-slate-900">
                      {formatMoeda(custoContratacao.data?.custo_medio ?? null)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Custo total</p>
                    <p className="text-xl font-semibold text-slate-900">
                      {formatMoeda(custoContratacao.data?.custo_total ?? '0')}
                    </p>
                  </div>
                </div>
                {custoContratacao.data && custoContratacao.data.vagas.length > 0 ? (
                  <ul className="divide-y divide-slate-100 text-sm">
                    {custoContratacao.data.vagas.map((vaga) => (
                      <li key={vaga.vaga_id} className="flex justify-between py-1.5">
                        <span className="text-slate-700">{vaga.cargo}</span>
                        <span className="text-slate-500">{formatMoeda(vaga.custo_contratacao)}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-slate-500">Nenhuma vaga fechada com custo registrado.</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-4 w-4 text-sapphire-600" aria-hidden />
              Candidatos por vaga
            </CardTitle>
          </CardHeader>
          <CardContent>
            {candidatosPorVaga.isLoading ? (
              <Spinner />
            ) : candidatosPorVaga.data && candidatosPorVaga.data.length > 0 ? (
              <ul className="space-y-2">
                {candidatosPorVaga.data.map((item) => {
                  const max = Math.max(...candidatosPorVaga.data!.map((i) => i.total_candidatos), 1)
                  return (
                    <li key={item.vaga_id}>
                      <div className="mb-1 flex justify-between text-sm">
                        <span className="text-slate-700">{item.vaga_cargo}</span>
                        <span className="font-medium text-slate-900">{item.total_candidatos}</span>
                      </div>
                      <div className="h-2 rounded-full bg-slate-100">
                        <div
                          className="h-2 rounded-full bg-sapphire-500"
                          style={{ width: `${(item.total_candidatos / max) * 100}%` }}
                        />
                      </div>
                    </li>
                  )
                })}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">Nenhum candidato em processo ainda.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-sapphire-600" aria-hidden />
              Conversão do funil
            </CardTitle>
          </CardHeader>
          <CardContent>
            {funilConversao.isLoading ? (
              <Spinner />
            ) : funilConversao.data && funilConversao.data.length > 0 ? (
              <ul className="space-y-3">
                {funilConversao.data.map((item) => (
                  <li key={item.etapa} className="text-sm">
                    <div className="mb-1 flex justify-between">
                      <span className="text-slate-700">{ETAPA_LABEL[item.etapa as Etapa]}</span>
                      <span className="text-slate-500">
                        {item.entraram} entraram
                        {item.taxa_conversao !== null && ` · ${item.taxa_conversao}% avançaram`}
                      </span>
                    </div>
                    {item.taxa_conversao !== null && (
                      <div className="h-2 rounded-full bg-slate-100">
                        <div
                          className="h-2 rounded-full bg-sapphire-500"
                          style={{ width: `${item.taxa_conversao}%` }}
                        />
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">Sem dados de funil ainda.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
