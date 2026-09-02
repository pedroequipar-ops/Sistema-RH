import { ArrowLeft, Download, Trash2, Upload } from 'lucide-react'
import { useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Spinner } from '@/components/ui/Spinner'
import { useAuth } from '@/context/AuthContext'
import { useCandidato, useDeleteCandidato, useUploadCurriculo } from '@/hooks/useCandidatos'
import { useCreatePontuacao, usePontuacoes } from '@/hooks/usePontuacoes'
import { curriculoStatusTone } from '@/lib/candidatoStatus'
import { CURRICULO_STATUS_LABEL, SENIORIDADE_LABEL } from '@/types/candidatos'

export function CandidatoDetailPage() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const { hasPermission } = useAuth()
  const { data: candidato, isLoading, isError } = useCandidato(id)
  const { data: pontuacoes } = usePontuacoes(id)
  const uploadCurriculo = useUploadCurriculo(id)
  const deleteCandidato = useDeleteCandidato()
  const createPontuacao = useCreatePontuacao(id)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [funcao, setFuncao] = useState('')
  const [pontuacao, setPontuacao] = useState('')

  const canEdit = hasPermission('candidatos', 'edit')
  const canDelete = hasPermission('candidatos', 'delete')

  if (isLoading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner />
      </div>
    )
  }

  if (isError || !candidato) {
    return <p className="text-sm text-red-600">Não foi possível carregar este candidato.</p>
  }

  function onFileSelected(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (file) uploadCurriculo.mutate(file)
    event.target.value = ''
  }

  async function onExcluir() {
    if (!window.confirm('Tem certeza que deseja excluir este candidato?')) return
    await deleteCandidato.mutateAsync(id)
    navigate('/candidatos')
  }

  async function onAddPontuacao() {
    if (!funcao.trim() || !pontuacao.trim()) return
    await createPontuacao.mutateAsync({ funcao, pontuacao })
    setFuncao('')
    setPontuacao('')
  }

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      <Link
        to="/candidatos"
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Voltar para candidatos
      </Link>

      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">{candidato.nome || '(sem nome)'}</h1>
          <p className="text-sm text-slate-500">
            {candidato.email}
            {candidato.cargo_pretendido && ` · ${candidato.cargo_pretendido}`}
          </p>
        </div>
        <div className="flex gap-2">
          {candidato.senioridade && (
            <Badge tone="sapphire">{SENIORIDADE_LABEL[candidato.senioridade]}</Badge>
          )}
          <Badge tone={curriculoStatusTone(candidato.curriculo_status)}>
            {CURRICULO_STATUS_LABEL[candidato.curriculo_status]}
          </Badge>
        </div>
      </div>

      {canDelete && (
        <Card className="p-4">
          <Button variant="danger" onClick={onExcluir} isLoading={deleteCandidato.isPending}>
            <Trash2 className="h-4 w-4" aria-hidden />
            Excluir candidato
          </Button>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Perfil</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="font-medium text-slate-700">Telefone</p>
              <p className="text-slate-600">{candidato.telefone || '—'}</p>
            </div>
            <div>
              <p className="font-medium text-slate-700">Cidade</p>
              <p className="text-slate-600">{candidato.cidade || '—'}</p>
            </div>
          </div>
          <div>
            <p className="mb-1.5 font-medium text-slate-700">Skills</p>
            {candidato.skills.length > 0 ? (
              <div className="flex flex-wrap gap-1.5">
                {candidato.skills.map((skill) => (
                  <Badge key={skill} tone="slate">
                    {skill}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-slate-500">Nenhuma skill registrada.</p>
            )}
          </div>
          {candidato.resumo_experiencia && (
            <div>
              <p className="font-medium text-slate-700">Resumo de experiência</p>
              <p className="whitespace-pre-wrap text-slate-600">{candidato.resumo_experiencia}</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Currículo</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-3">
          <Badge tone={curriculoStatusTone(candidato.curriculo_status)}>
            {CURRICULO_STATUS_LABEL[candidato.curriculo_status]}
          </Badge>
          {candidato.curriculo_url && (
            <a
              href={candidato.curriculo_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-sapphire-700 hover:text-sapphire-800"
            >
              <Download className="h-4 w-4" aria-hidden />
              Baixar currículo
            </a>
          )}
          {canEdit && (
            <>
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={onFileSelected}
              />
              <Button
                variant="secondary"
                isLoading={uploadCurriculo.isPending}
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="h-4 w-4" aria-hidden />
                {candidato.curriculo_url ? 'Substituir currículo' : 'Enviar currículo'}
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Pontuações por função</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {pontuacoes && pontuacoes.results.length > 0 ? (
            <ul className="divide-y divide-slate-100 text-sm">
              {pontuacoes.results.map((item) => (
                <li key={item.id} className="flex items-center justify-between py-2">
                  <div>
                    <p className="font-medium text-slate-800">{item.funcao}</p>
                    <p className="text-xs text-slate-400">
                      {item.origem === 'manual' ? 'Avaliação manual' : 'Motor automático'}
                      {item.avaliador_nome && ` · ${item.avaliador_nome}`}
                    </p>
                  </div>
                  <Badge tone="sapphire">{item.pontuacao}</Badge>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">Nenhuma pontuação registrada ainda.</p>
          )}

          {canEdit && (
            <div className="flex items-end gap-3 border-t border-slate-100 pt-4">
              <div className="flex-1">
                <Label htmlFor="funcao">Função</Label>
                <Input
                  id="funcao"
                  placeholder="Ex: Desenvolvedor Backend"
                  value={funcao}
                  onChange={(event) => setFuncao(event.target.value)}
                />
              </div>
              <div className="w-28">
                <Label htmlFor="pontuacao">Nota</Label>
                <Input
                  id="pontuacao"
                  type="number"
                  step="0.01"
                  value={pontuacao}
                  onChange={(event) => setPontuacao(event.target.value)}
                />
              </div>
              <Button isLoading={createPontuacao.isPending} onClick={onAddPontuacao}>
                Adicionar
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
