import { ArrowLeft, Check, Download, X } from 'lucide-react'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { ConfirmActionModal } from '@/components/shared/ConfirmActionModal'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Spinner } from '@/components/ui/Spinner'
import { useAuth } from '@/context/AuthContext'
import { useFuncionario, useRevisarChecklistItem, useUpdateFuncionario } from '@/hooks/useAdmissao'
import { checklistStatusTone, statusOnboardingTone } from '@/lib/admissaoStatus'
import { getApiErrorMessage } from '@/lib/apiError'
import { formatDateOnly } from '@/lib/date'
import { CHECKLIST_STATUS_LABEL, STATUS_ONBOARDING_LABEL } from '@/types/admissao'

type Acao = { itemId: string; tipo: 'aprovado' | 'rejeitado' } | null

export function FuncionarioDetailPage() {
  const { id = '' } = useParams()
  const { hasPermission } = useAuth()
  const canEdit = hasPermission('admissao', 'edit')

  const { data: funcionario, isLoading, isError } = useFuncionario(id)
  const updateFuncionario = useUpdateFuncionario(id)
  const revisar = useRevisarChecklistItem(id)
  const [dataAdmissao, setDataAdmissao] = useState('')
  const [acao, setAcao] = useState<Acao>(null)
  const [erro, setErro] = useState<string | null>(null)

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner />
      </div>
    )
  }

  if (isError || !funcionario) {
    return <p className="text-sm text-red-600">Não foi possível carregar este funcionário.</p>
  }

  async function onSalvarDataAdmissao() {
    if (!dataAdmissao) return
    await updateFuncionario.mutateAsync(dataAdmissao)
    setDataAdmissao('')
  }

  async function onConfirmarRevisao(observacao: string) {
    if (!acao) return
    setErro(null)
    try {
      await revisar.mutateAsync({ id: acao.itemId, status: acao.tipo, observacao })
      setAcao(null)
    } catch (error) {
      setErro(getApiErrorMessage(error))
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      <Link to="/admissao" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700">
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Voltar para admissão
      </Link>

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">{funcionario.candidato_nome}</h1>
          <p className="text-sm text-slate-500">{funcionario.cargo}</p>
        </div>
        <Badge tone={statusOnboardingTone(funcionario.status_onboarding)}>
          {STATUS_ONBOARDING_LABEL[funcionario.status_onboarding]}
        </Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Data de admissão</CardTitle>
        </CardHeader>
        <CardContent className="flex items-end gap-3">
          <div>
            <p className="text-lg font-medium text-slate-800">
              {funcionario.data_admissao ? formatDateOnly(funcionario.data_admissao) : 'Não definida'}
            </p>
          </div>
          {canEdit && (
            <>
              <div className="ml-auto">
                <Label htmlFor="data_admissao">Definir/alterar</Label>
                <Input
                  id="data_admissao"
                  type="date"
                  value={dataAdmissao}
                  onChange={(event) => setDataAdmissao(event.target.value)}
                />
              </div>
              <Button isLoading={updateFuncionario.isPending} onClick={onSalvarDataAdmissao}>
                Salvar
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Checklist de documentos</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="divide-y divide-slate-100">
            {funcionario.checklist.map((item) => (
              <li key={item.id} className="flex items-center justify-between gap-4 py-3">
                <div>
                  <p className="text-sm font-medium text-slate-800">
                    {item.nome_documento}
                    {!item.obrigatorio && <span className="ml-1.5 text-xs text-slate-400">(opcional)</span>}
                  </p>
                  {item.observacao && <p className="text-xs text-slate-500">{item.observacao}</p>}
                  {item.documento_url && (
                    <a
                      href={item.documento_url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-xs font-medium text-sapphire-700 hover:text-sapphire-800"
                    >
                      <Download className="h-3 w-3" aria-hidden />
                      Baixar documento
                    </a>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Badge tone={checklistStatusTone(item.status)}>{CHECKLIST_STATUS_LABEL[item.status]}</Badge>
                  {canEdit && item.status === 'enviado' && (
                    <>
                      <Button
                        variant="secondary"
                        onClick={() => setAcao({ itemId: item.id, tipo: 'aprovado' })}
                      >
                        <Check className="h-4 w-4" aria-hidden />
                      </Button>
                      <Button
                        variant="danger"
                        onClick={() => setAcao({ itemId: item.id, tipo: 'rejeitado' })}
                      >
                        <X className="h-4 w-4" aria-hidden />
                      </Button>
                    </>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {acao && (
        <ConfirmActionModal
          title={acao.tipo === 'aprovado' ? 'Aprovar documento' : 'Rejeitar documento'}
          description="Confirme a ação abaixo. Você pode registrar uma observação."
          error={erro}
          confirmLabel="Confirmar"
          variant={acao.tipo === 'rejeitado' ? 'danger' : 'primary'}
          isLoading={revisar.isPending}
          onConfirm={onConfirmarRevisao}
          onClose={() => {
            setAcao(null)
            setErro(null)
          }}
        />
      )}
    </div>
  )
}
