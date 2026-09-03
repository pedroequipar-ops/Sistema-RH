import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { listVagasParaFiltro } from '@/api/vagas'
import { MoverEtapaModal } from '@/components/processos/MoverEtapaModal'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { useMoverEtapa, useMoverEtapaDireto, useProcessos } from '@/hooks/useProcessos'
import { getApiErrorMessage } from '@/lib/apiError'
import { cn } from '@/lib/cn'
import {
  ETAPA_LABEL,
  ETAPA_ORDEM,
  TRANSICOES_PERMITIDAS,
  type Etapa,
  type ProcessoSeletivo,
} from '@/types/processos'

const COLUNA_TONE: Record<Etapa, 'slate' | 'amber' | 'sapphire' | 'green' | 'red'> = {
  triagem: 'slate',
  teste: 'amber',
  entrevista: 'sapphire',
  proposta: 'sapphire',
  contratado: 'green',
  reprovado: 'red',
}

type DragPayload = { id: string; etapaOrigem: Etapa }

export function ProcessosKanbanPage() {
  const navigate = useNavigate()
  const [vagaId, setVagaId] = useState('')
  const [moverProcesso, setMoverProcesso] = useState<ProcessoSeletivo | null>(null)
  const [moverErro, setMoverErro] = useState<string | null>(null)
  const [dragErro, setDragErro] = useState<string | null>(null)
  const [dragOverEtapa, setDragOverEtapa] = useState<Etapa | null>(null)

  const { data: vagas } = useQuery({ queryKey: ['vagas-filtro'], queryFn: listVagasParaFiltro })
  const { data, isLoading, isError } = useProcessos({ vaga: vagaId })
  const moverEtapa = useMoverEtapa(moverProcesso?.id ?? '')
  const moverEtapaDireto = useMoverEtapaDireto()

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

  function onDrop(etapaDestino: Etapa, event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault()
    setDragOverEtapa(null)
    const raw = event.dataTransfer.getData('text/plain')
    if (!raw) return
    const { id, etapaOrigem } = JSON.parse(raw) as DragPayload
    if (etapaOrigem === etapaDestino) return
    if (!TRANSICOES_PERMITIDAS[etapaOrigem].includes(etapaDestino)) {
      setDragErro(
        `Não é possível mover direto de "${ETAPA_LABEL[etapaOrigem]}" para "${ETAPA_LABEL[etapaDestino]}".`,
      )
      return
    }
    setDragErro(null)
    moverEtapaDireto.mutate(
      { id, etapa: etapaDestino },
      { onError: (error) => setDragErro(getApiErrorMessage(error)) },
    )
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

      {dragErro && (
        <div className="flex items-center justify-between gap-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          <span>{dragErro}</span>
          <button onClick={() => setDragErro(null)} className="font-medium hover:underline">
            Fechar
          </button>
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-16">
          <Spinner />
        </div>
      ) : isError ? (
        <p className="text-sm text-red-600">Não foi possível carregar os processos.</p>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-2">
          {ETAPA_ORDEM.map((etapa) => (
            <div
              key={etapa}
              className={cn(
                'w-64 shrink-0 space-y-3 rounded-lg p-1 transition-colors',
                dragOverEtapa === etapa && 'bg-sapphire-50 ring-2 ring-sapphire-300',
              )}
              onDragOver={(event) => {
                event.preventDefault()
                if (dragOverEtapa !== etapa) setDragOverEtapa(etapa)
              }}
              onDragLeave={(event) => {
                if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
                  setDragOverEtapa(null)
                }
              }}
              onDrop={(event) => onDrop(etapa, event)}
            >
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-slate-700">{ETAPA_LABEL[etapa]}</h2>
                <Badge tone={COLUNA_TONE[etapa]}>{colunas[etapa].length}</Badge>
              </div>
              <div className="space-y-2">
                {colunas[etapa].map((processo) => {
                  const podeArrastar = etapa !== 'contratado' && etapa !== 'reprovado'
                  return (
                    <Card
                      key={processo.id}
                      draggable={podeArrastar}
                      onDragStart={(event) => {
                        event.dataTransfer.effectAllowed = 'move'
                        event.dataTransfer.setData(
                          'text/plain',
                          JSON.stringify({ id: processo.id, etapaOrigem: etapa } satisfies DragPayload),
                        )
                      }}
                      onDragEnd={() => setDragOverEtapa(null)}
                      onClick={() => navigate(`/processos-seletivos/${processo.id}`)}
                      className={cn(
                        'p-3 hover:border-sapphire-300',
                        podeArrastar ? 'cursor-grab active:cursor-grabbing' : 'cursor-pointer',
                      )}
                    >
                      <p className="text-sm font-medium text-slate-900">{processo.candidato_nome}</p>
                      <p className="text-xs text-slate-500">{processo.vaga_cargo}</p>
                      {podeArrastar && (
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
                  )
                })}
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
