import { ArrowLeft, CalendarPlus, ClipboardCheck, MessageSquarePlus } from 'lucide-react'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { MoverEtapaModal } from '@/components/processos/MoverEtapaModal'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { Textarea } from '@/components/ui/Textarea'
import { useAuth } from '@/context/AuthContext'
import { useAvaliacoes, useCreateAvaliacao } from '@/hooks/useAvaliacoes'
import { useCreateEntrevista, useEntrevistas } from '@/hooks/useEntrevistas'
import { useMoverEtapa, useProcesso } from '@/hooks/useProcessos'
import { useAvaliarTeste, useCreateTeste, useTestes } from '@/hooks/useTestes'
import { getApiErrorMessage } from '@/lib/apiError'
import {
  ETAPA_LABEL,
  TESTE_STATUS_LABEL,
  TESTE_TIPO_LABEL,
  type Etapa,
  type TesteTipo,
} from '@/types/processos'

const ETAPA_TONE: Record<Etapa, 'slate' | 'amber' | 'sapphire' | 'green' | 'red'> = {
  triagem: 'slate',
  teste: 'amber',
  entrevista: 'sapphire',
  proposta: 'sapphire',
  contratado: 'green',
  reprovado: 'red',
}

export function ProcessoDetailPage() {
  const { id = '' } = useParams()
  const { hasPermission } = useAuth()
  const canEdit = hasPermission('processos-seletivos', 'edit')

  const { data: processo, isLoading, isError } = useProcesso(id)
  const moverEtapa = useMoverEtapa(id)
  const [moverAberto, setMoverAberto] = useState(false)
  const [moverErro, setMoverErro] = useState<string | null>(null)

  const { data: avaliacoes } = useAvaliacoes(id)
  const createAvaliacao = useCreateAvaliacao(id)
  const [nota, setNota] = useState('')
  const [comentario, setComentario] = useState('')

  const { data: testes } = useTestes(id)
  const createTeste = useCreateTeste(id)
  const avaliarTeste = useAvaliarTeste(id)
  const [testeTipo, setTesteTipo] = useState<TesteTipo>('tecnico')
  const [testeTitulo, setTesteTitulo] = useState('')
  const [notaTeste, setNotaTeste] = useState<Record<string, string>>({})

  const { data: entrevistas } = useEntrevistas(id)
  const createEntrevista = useCreateEntrevista(id)
  const [entrevistaForm, setEntrevistaForm] = useState({
    data_hora: '',
    duracao_minutos: 60,
    local_ou_link: '',
    observacoes: '',
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner />
      </div>
    )
  }

  if (isError || !processo) {
    return <p className="text-sm text-red-600">Não foi possível carregar este processo.</p>
  }

  async function onConfirmarMover(etapa: Etapa, observacao: string) {
    setMoverErro(null)
    try {
      await moverEtapa.mutateAsync({ etapa, observacao })
      setMoverAberto(false)
    } catch (error) {
      setMoverErro(getApiErrorMessage(error))
    }
  }

  async function onAddAvaliacao() {
    if (!comentario.trim() && !nota.trim()) return
    await createAvaliacao.mutateAsync({ nota, comentario })
    setNota('')
    setComentario('')
  }

  async function onAddTeste() {
    if (!testeTitulo.trim()) return
    await createTeste.mutateAsync({ tipo: testeTipo, titulo: testeTitulo })
    setTesteTitulo('')
  }

  async function onAvaliarTeste(testeId: string) {
    const valor = notaTeste[testeId]
    if (!valor?.trim()) return
    await avaliarTeste.mutateAsync({ id: testeId, nota: valor })
    setNotaTeste((prev) => ({ ...prev, [testeId]: '' }))
  }

  async function onAddEntrevista() {
    if (!entrevistaForm.data_hora) return
    await createEntrevista.mutateAsync(entrevistaForm)
    setEntrevistaForm({ data_hora: '', duracao_minutos: 60, local_ou_link: '', observacoes: '' })
  }

  const etapaFinal = processo.etapa_atual === 'contratado' || processo.etapa_atual === 'reprovado'

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      <Link
        to="/processos-seletivos"
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Voltar para o funil
      </Link>

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">{processo.candidato_nome}</h1>
          <p className="text-sm text-slate-500">
            {processo.candidato_email} · Vaga: {processo.vaga_cargo}
          </p>
        </div>
        <Badge tone={ETAPA_TONE[processo.etapa_atual]}>{ETAPA_LABEL[processo.etapa_atual]}</Badge>
      </div>

      {canEdit && !etapaFinal && (
        <Card className="p-4">
          <Button onClick={() => setMoverAberto(true)}>Mover etapa</Button>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Histórico do funil</CardTitle>
        </CardHeader>
        <CardContent>
          {processo.historico_etapas.length === 0 ? (
            <p className="text-sm text-slate-500">Sem histórico registrado.</p>
          ) : (
            <ol className="space-y-3">
              {processo.historico_etapas.map((item) => (
                <li key={item.id} className="flex gap-3 text-sm">
                  <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-sapphire-500" aria-hidden />
                  <div>
                    <p className="text-slate-700">
                      <span className="font-medium">
                        {ETAPA_LABEL[item.para_etapa as Etapa] ?? item.para_etapa}
                      </span>
                      {item.de_etapa && (
                        <span className="text-slate-400">
                          {' '}
                          (era {ETAPA_LABEL[item.de_etapa as Etapa] ?? item.de_etapa})
                        </span>
                      )}
                    </p>
                    <p className="text-xs text-slate-400">
                      {new Date(item.created_at).toLocaleString('pt-BR')}
                    </p>
                    {item.observacao && <p className="mt-1 text-slate-600">{item.observacao}</p>}
                  </div>
                </li>
              ))}
            </ol>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Avaliações</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {avaliacoes && avaliacoes.results.length > 0 ? (
            <ul className="divide-y divide-slate-100 text-sm">
              {avaliacoes.results.map((item) => (
                <li key={item.id} className="py-2">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-slate-800">{item.autor_nome}</p>
                    {item.nota && <Badge tone="sapphire">{item.nota}</Badge>}
                  </div>
                  {item.comentario && <p className="mt-1 text-slate-600">{item.comentario}</p>}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">Nenhuma avaliação registrada ainda.</p>
          )}

          {canEdit && (
            <div className="space-y-3 border-t border-slate-100 pt-4">
              <div className="flex gap-3">
                <div className="flex-1">
                  <Label htmlFor="comentario">Comentário</Label>
                  <Textarea
                    id="comentario"
                    rows={2}
                    value={comentario}
                    onChange={(event) => setComentario(event.target.value)}
                  />
                </div>
                <div className="w-24">
                  <Label htmlFor="nota">Nota</Label>
                  <Input
                    id="nota"
                    type="number"
                    step="0.01"
                    value={nota}
                    onChange={(event) => setNota(event.target.value)}
                  />
                </div>
              </div>
              <Button isLoading={createAvaliacao.isPending} onClick={onAddAvaliacao}>
                <MessageSquarePlus className="h-4 w-4" aria-hidden />
                Adicionar avaliação
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Testes aplicados</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {testes && testes.results.length > 0 ? (
            <ul className="divide-y divide-slate-100 text-sm">
              {testes.results.map((teste) => (
                <li key={teste.id} className="space-y-2 py-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-slate-800">{teste.titulo}</p>
                      <p className="text-xs text-slate-400">{TESTE_TIPO_LABEL[teste.tipo]}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {teste.nota && <Badge tone="sapphire">{teste.nota}</Badge>}
                      <Badge tone={teste.status === 'avaliado' ? 'green' : 'amber'}>
                        {TESTE_STATUS_LABEL[teste.status]}
                      </Badge>
                    </div>
                  </div>
                  {canEdit && teste.status !== 'avaliado' && (
                    <div className="flex gap-2">
                      <Input
                        type="number"
                        step="0.01"
                        placeholder="Nota"
                        className="w-28"
                        value={notaTeste[teste.id] ?? ''}
                        onChange={(event) =>
                          setNotaTeste((prev) => ({ ...prev, [teste.id]: event.target.value }))
                        }
                      />
                      <Button
                        variant="secondary"
                        isLoading={avaliarTeste.isPending}
                        onClick={() => onAvaliarTeste(teste.id)}
                      >
                        <ClipboardCheck className="h-4 w-4" aria-hidden />
                        Avaliar
                      </Button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">Nenhum teste aplicado ainda.</p>
          )}

          {canEdit && (
            <div className="flex items-end gap-3 border-t border-slate-100 pt-4">
              <div className="w-40">
                <Label htmlFor="teste-tipo">Tipo</Label>
                <Select
                  id="teste-tipo"
                  value={testeTipo}
                  onChange={(event) => setTesteTipo(event.target.value as TesteTipo)}
                >
                  <option value="tecnico">Técnico</option>
                  <option value="comportamental">Comportamental</option>
                </Select>
              </div>
              <div className="flex-1">
                <Label htmlFor="teste-titulo">Título</Label>
                <Input
                  id="teste-titulo"
                  value={testeTitulo}
                  onChange={(event) => setTesteTitulo(event.target.value)}
                />
              </div>
              <Button isLoading={createTeste.isPending} onClick={onAddTeste}>
                Aplicar teste
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Entrevistas</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {entrevistas && entrevistas.results.length > 0 ? (
            <ul className="divide-y divide-slate-100 text-sm">
              {entrevistas.results.map((entrevista) => (
                <li key={entrevista.id} className="py-2">
                  <p className="font-medium text-slate-800">
                    {new Date(entrevista.data_hora).toLocaleString('pt-BR')} ·{' '}
                    {entrevista.duracao_minutos} min
                  </p>
                  {entrevista.local_ou_link && (
                    <p className="text-slate-600">{entrevista.local_ou_link}</p>
                  )}
                  {entrevista.observacoes && (
                    <p className="text-xs text-slate-400">{entrevista.observacoes}</p>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">Nenhuma entrevista agendada ainda.</p>
          )}

          {canEdit && (
            <div className="space-y-3 border-t border-slate-100 pt-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor="data_hora">Data e hora</Label>
                  <Input
                    id="data_hora"
                    type="datetime-local"
                    value={entrevistaForm.data_hora}
                    onChange={(event) =>
                      setEntrevistaForm((prev) => ({ ...prev, data_hora: event.target.value }))
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="duracao_minutos">Duração (minutos)</Label>
                  <Input
                    id="duracao_minutos"
                    type="number"
                    value={entrevistaForm.duracao_minutos}
                    onChange={(event) =>
                      setEntrevistaForm((prev) => ({
                        ...prev,
                        duracao_minutos: Number(event.target.value),
                      }))
                    }
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="local_ou_link">Local ou link</Label>
                <Input
                  id="local_ou_link"
                  value={entrevistaForm.local_ou_link}
                  onChange={(event) =>
                    setEntrevistaForm((prev) => ({ ...prev, local_ou_link: event.target.value }))
                  }
                />
              </div>
              <div>
                <Label htmlFor="observacoes">Observações</Label>
                <Textarea
                  id="observacoes"
                  rows={2}
                  value={entrevistaForm.observacoes}
                  onChange={(event) =>
                    setEntrevistaForm((prev) => ({ ...prev, observacoes: event.target.value }))
                  }
                />
              </div>
              <Button isLoading={createEntrevista.isPending} onClick={onAddEntrevista}>
                <CalendarPlus className="h-4 w-4" aria-hidden />
                Agendar entrevista
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {moverAberto && (
        <MoverEtapaModal
          etapaAtual={processo.etapa_atual}
          error={moverErro}
          isLoading={moverEtapa.isPending}
          onConfirm={onConfirmarMover}
          onClose={() => {
            setMoverAberto(false)
            setMoverErro(null)
          }}
        />
      )}
    </div>
  )
}
