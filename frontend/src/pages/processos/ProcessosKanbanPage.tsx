import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { listVagasParaFiltro } from '@/api/vagas'
import { MoverEtapaModal } from '@/components/processos/MoverEtapaModal'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { useMoverEtapa, useProcessos } from '@/hooks/useProcessos'
import { getApiErrorMessage } from '@/lib/apiError'
import { ETAPA_LABEL, ETAPA_ORDEM, type Etapa, type ProcessoSeletivo } from '@/types/processos'

const COLUNA_TONE: Record<Etapa, 'slate' | 'amber' | 'sapphire' | 'green' | 'red'> = {
  triagem: 'slate',
  teste: 'amber',
  entrevista: 'sapphire',
  proposta: 'sapphire',
  contratado: 'green',
  reprovado: 'red',
}

export function ProcessosKanbanPage() {
  const navigate = useNavigate()
  const [vagaId, setVagaId] = useState('')
  const [moverProcesso, setMoverProcesso] = useState<ProcessoSeletivo | null>(null)
  const [moverErro, setMoverErro] = useState<string | null>(null)

  const { data: vagas } = useQuery({ queryKey: ['vagas-filtro'], queryFn: listVagasParaFiltro })
  const { data, isLoading, isError } = useProcessos({ vaga: vagaId })
  const moverEtapa = useMoverEtapa(moverProcesso?.id ?? '')

  const colunas = ETAPA_ORDEM.reduce<Record<Etapa, ProcessoSeletivo[]>>(
    (acc, etapa) => {
      acc[etapa] = data?.results.filter((processo) => processo.etapa_atual === etapa) ?? []
      return acc
    },
    { triagem: [], teste: [], entrevista: [], proposta: [], contratado: [], reprovado: [] },
  )

  async function onConfirmarMover(etapa: Etapa, observacao: string) {
    setMoverErro(null)
    try {
      await moverEtapa.mutateAsync({ etapa, observacao })
      setMoverProcesso(null)
    } catch (error) {
      setMoverErro(getApiErrorMessage(error))
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Processos seletivos</h1>
          <p className="text-sm text-slate-500">Funil de seleção, do candidato à contratação.</p>
        </div>
        <Select value={vagaId} onChange={(event) => setVagaId(event.target.value)} className="w-64">
          <option value="">Todas as vagas</option>
          {vagas?.results.map((vaga) => (
            <option key={vaga.id} value={vaga.id}>
              {vaga.cargo}
            </option>
          ))}
        </Select>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-16">
          <Spinner />
        </div>
      ) : isError ? (
        <p className="text-sm text-red-600">Não foi possível carregar os processos.</p>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-2">
          {ETAPA_ORDEM.map((etapa) => (
            <div key={etapa} className="w-64 shrink-0 space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-slate-700">{ETAPA_LABEL[etapa]}</h2>
                <Badge tone={COLUNA_TONE[etapa]}>{colunas[etapa].length}</Badge>
              </div>
              <div className="space-y-2">
                {colunas[etapa].map((processo) => (
                  <Card
                    key={processo.id}
                    className="cursor-pointer p-3 hover:border-sapphire-300"
                    onClick={() => navigate(`/processos-seletivos/${processo.id}`)}
                  >
                    <p className="text-sm font-medium text-slate-900">{processo.candidato_nome}</p>
                    <p className="text-xs text-slate-500">{processo.vaga_cargo}</p>
                    {etapa !== 'contratado' && etapa !== 'reprovado' && (
                      <button
                        onClick={(event) => {
                          event.stopPropagation()
                          setMoverErro(null)
                          setMoverProcesso(processo)
                        }}
                        className="mt-2 text-xs font-medium text-sapphire-700 hover:text-sapphire-800"
                      >
                        Mover etapa
                      </button>
                    )}
                  </Card>
                ))}
                {colunas[etapa].length === 0 && (
                  <p className="rounded-lg border border-dashed border-slate-200 p-3 text-center text-xs text-slate-400">
                    Vazio
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {moverProcesso && (
        <MoverEtapaModal
          etapaAtual={moverProcesso.etapa_atual}
          error={moverErro}
          isLoading={moverEtapa.isPending}
          onConfirm={onConfirmarMover}
          onClose={() => {
            setMoverProcesso(null)
            setMoverErro(null)
          }}
        />
      )}
    </div>
  )
}
