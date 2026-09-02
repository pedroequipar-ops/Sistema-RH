import { ArrowLeft, Ban, CircleCheck, CircleX, Pause, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { ConfirmActionModal } from '@/components/shared/ConfirmActionModal'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import { useAuth } from '@/context/AuthContext'
import {
  useAprovarVaga,
  useCancelarVaga,
  useDeleteVaga,
  usePausarVaga,
  useReprovarVaga,
  useVaga,
} from '@/hooks/useVagas'
import { getApiErrorMessage } from '@/lib/apiError'
import { statusAprovacaoTone, statusOperacionalTone } from '@/lib/vagaStatus'
import {
  STATUS_APROVACAO_LABEL,
  STATUS_OPERACIONAL_LABEL,
  TIPO_VAGA_LABEL,
  type StatusAprovacao,
  type StatusOperacional,
} from '@/types/vagas'

type ActionKind = 'aprovar' | 'reprovar' | 'pausar' | 'cancelar' | null

function historicoStatusLabel(tipo: 'aprovacao' | 'operacional', status: string) {
  if (tipo === 'aprovacao') return STATUS_APROVACAO_LABEL[status as StatusAprovacao] ?? status
  return STATUS_OPERACIONAL_LABEL[status as StatusOperacional] ?? status
}

export function VagaDetailPage() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const { user, hasPermission } = useAuth()
  const { data: vaga, isLoading, isError } = useVaga(id)
  const [actionOpen, setActionOpen] = useState<ActionKind>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const aprovar = useAprovarVaga(id)
  const reprovar = useReprovarVaga(id)
  const pausar = usePausarVaga(id)
  const cancelar = useCancelarVaga(id)
  const deleteVaga = useDeleteVaga()

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner />
      </div>
    )
  }

  if (isError || !vaga) {
    return <p className="text-sm text-red-600">Não foi possível carregar esta vaga.</p>
  }

  const isDono =
    !!user &&
    (user.is_superuser ||
      user.role === 'rh' ||
      user.role === 'diretoria' ||
      (user.role === 'gestor' && vaga.solicitante === user.id))

  const canEdit = hasPermission('vagas', 'edit')
  const canAprovarEtapaRh =
    canEdit && vaga.status_aprovacao === 'aguardando_rh' && (user?.role === 'rh' || user?.is_superuser)
  const canAprovarEtapaDiretoria =
    canEdit &&
    vaga.status_aprovacao === 'aguardando_diretoria' &&
    (user?.role === 'diretoria' || user?.is_superuser)
  const canAprovarOuReprovar = canAprovarEtapaRh || canAprovarEtapaDiretoria
  const canPausar = canEdit && isDono && (vaga.status === 'aberta' || vaga.status === 'em_andamento')
  const canCancelar = canEdit && isDono && vaga.status !== 'cancelada'
  const canExcluir = hasPermission('vagas', 'delete')

  async function runAction(observacao: string) {
    setActionError(null)
    try {
      if (actionOpen === 'aprovar') await aprovar.mutateAsync(observacao)
      if (actionOpen === 'reprovar') await reprovar.mutateAsync(observacao)
      if (actionOpen === 'pausar') await pausar.mutateAsync(observacao)
      if (actionOpen === 'cancelar') await cancelar.mutateAsync(observacao)
      setActionOpen(null)
    } catch (error) {
      setActionError(getApiErrorMessage(error))
    }
  }

  async function onExcluir() {
    if (!window.confirm('Tem certeza que deseja excluir esta vaga?')) return
    await deleteVaga.mutateAsync(id)
    navigate('/vagas')
  }

  const isActionPending =
    aprovar.isPending || reprovar.isPending || pausar.isPending || cancelar.isPending

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      <Link to="/vagas" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700">
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Voltar para vagas
      </Link>

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">{vaga.cargo}</h1>
          <p className="text-sm text-slate-500">
            {vaga.area_solicitante} · {TIPO_VAGA_LABEL[vaga.tipo]} · Solicitado por {vaga.solicitante_nome}
          </p>
        </div>
        <div className="flex gap-2">
          <Badge tone={statusAprovacaoTone(vaga.status_aprovacao)}>
            {STATUS_APROVACAO_LABEL[vaga.status_aprovacao]}
          </Badge>
          <Badge tone={statusOperacionalTone(vaga.status)}>{STATUS_OPERACIONAL_LABEL[vaga.status]}</Badge>
        </div>
      </div>

      {(canAprovarOuReprovar || canPausar || canCancelar || canExcluir) && (
        <Card className="p-4">
          <div className="flex flex-wrap gap-2">
            {canAprovarOuReprovar && (
              <Button onClick={() => setActionOpen('aprovar')}>
                <CircleCheck className="h-4 w-4" aria-hidden />
                Aprovar
              </Button>
            )}
            {canAprovarOuReprovar && (
              <Button variant="danger" onClick={() => setActionOpen('reprovar')}>
                <CircleX className="h-4 w-4" aria-hidden />
                Reprovar
              </Button>
            )}
            {canPausar && (
              <Button variant="secondary" onClick={() => setActionOpen('pausar')}>
                <Pause className="h-4 w-4" aria-hidden />
                Pausar
              </Button>
            )}
            {canCancelar && (
              <Button variant="secondary" onClick={() => setActionOpen('cancelar')}>
                <Ban className="h-4 w-4" aria-hidden />
                Cancelar vaga
              </Button>
            )}
            {canExcluir && (
              <Button variant="danger" onClick={onExcluir} isLoading={deleteVaga.isPending}>
                <Trash2 className="h-4 w-4" aria-hidden />
                Excluir
              </Button>
            )}
          </div>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Detalhes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div>
            <p className="font-medium text-slate-700">Descrição</p>
            <p className="whitespace-pre-wrap text-slate-600">{vaga.descricao}</p>
          </div>
          <div>
            <p className="font-medium text-slate-700">Requisitos</p>
            <p className="whitespace-pre-wrap text-slate-600">{vaga.requisitos}</p>
          </div>
          {vaga.salario && (
            <div>
              <p className="font-medium text-slate-700">Salário</p>
              <p className="text-slate-600">R$ {vaga.salario}</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Histórico</CardTitle>
        </CardHeader>
        <CardContent>
          {vaga.historico.length === 0 ? (
            <p className="text-sm text-slate-500">Sem histórico registrado.</p>
          ) : (
            <ol className="space-y-4">
              {vaga.historico.map((item) => (
                <li key={item.id} className="flex gap-3 text-sm">
                  <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-sapphire-500" aria-hidden />
                  <div>
                    <p className="text-slate-700">
                      <span className="font-medium">{historicoStatusLabel(item.tipo_status, item.para_status)}</span>
                      {item.de_status && (
                        <span className="text-slate-400">
                          {' '}
                          (era {historicoStatusLabel(item.tipo_status, item.de_status)})
                        </span>
                      )}
                    </p>
                    <p className="text-xs text-slate-400">
                      {new Date(item.created_at).toLocaleString('pt-BR')}
                      {item.alterado_por_nome && ` · ${item.alterado_por_nome}`}
                    </p>
                    {item.observacao && <p className="mt-1 text-slate-600">{item.observacao}</p>}
                  </div>
                </li>
              ))}
            </ol>
          )}
        </CardContent>
      </Card>

      {actionOpen && (
        <ConfirmActionModal
          title={
            { aprovar: 'Aprovar vaga', reprovar: 'Reprovar vaga', pausar: 'Pausar vaga', cancelar: 'Cancelar vaga' }[
              actionOpen
            ]
          }
          description="Confirme a ação abaixo. Você pode registrar uma observação."
          error={actionError}
          confirmLabel="Confirmar"
          variant={actionOpen === 'reprovar' || actionOpen === 'cancelar' ? 'danger' : 'primary'}
          isLoading={isActionPending}
          onConfirm={runAction}
          onClose={() => {
            setActionOpen(null)
            setActionError(null)
          }}
        />
      )}
    </div>
  )
}
