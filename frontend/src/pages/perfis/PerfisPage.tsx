import { Copy, Pencil, Plus, Search, ShieldCheck, Trash2 } from 'lucide-react'
import { type FormEvent, useMemo, useState } from 'react'

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Modal } from '@/components/ui/Modal'
import { Spinner } from '@/components/ui/Spinner'
import { Switch } from '@/components/ui/Switch'
import {
  useAlternarAtivoPerfil,
  useAtualizarPermissoesPerfil,
  useCriarPerfil,
  useDuplicarPerfil,
  useEditarPerfil,
  useExcluirPerfil,
  usePerfis,
} from '@/hooks/usePerfis'
import { getApiErrorMessage } from '@/lib/apiError'
import { cn } from '@/lib/cn'
import { MODULOS, type CriarPerfilValues, type ModuloSlug, type Perfil } from '@/types/usuarios'

const CAMPOS_PERMISSAO = [
  { campo: 'can_view', label: 'Visualizar' },
  { campo: 'can_create', label: 'Criar' },
  { campo: 'can_edit', label: 'Editar' },
  { campo: 'can_delete', label: 'Excluir' },
] as const

export function PerfisPage() {
  const { data, isLoading, isError } = usePerfis()
  const [busca, setBusca] = useState('')
  const [modalAberto, setModalAberto] = useState(false)
  const [perfilEditando, setPerfilEditando] = useState<Perfil | null>(null)
  const [perfilPermissoes, setPerfilPermissoes] = useState<Perfil | null>(null)
  const [perfilExcluindo, setPerfilExcluindo] = useState<Perfil | null>(null)

  const duplicar = useDuplicarPerfil()
  const alternarAtivo = useAlternarAtivoPerfil()

  const perfisFiltrados = useMemo(() => {
    const termo = busca.trim().toLowerCase()
    if (!termo) return data?.results ?? []
    return (data?.results ?? []).filter((perfil) => perfil.nome.toLowerCase().includes(termo))
  }, [data, busca])

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Perfis de acesso</h1>
          <p className="text-sm text-slate-500">Gerencie perfis e suas permissões por módulo.</p>
        </div>
        <Button onClick={() => setModalAberto(true)}>
          <Plus className="h-4 w-4" aria-hidden />
          Novo perfil
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
          aria-hidden
        />
        <Input
          placeholder="Buscar perfil..."
          className="pl-9"
          value={busca}
          onChange={(event) => setBusca(event.target.value)}
        />
      </div>

      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner />
          </div>
        ) : isError ? (
          <p className="p-6 text-sm text-red-600">Não foi possível carregar os perfis.</p>
        ) : perfisFiltrados.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Perfil</th>
                  <th className="px-4 py-3 font-medium">Descrição</th>
                  <th className="px-4 py-3 font-medium">Usuários</th>
                  <th className="px-4 py-3 font-medium">Tipo</th>
                  <th className="px-4 py-3 font-medium">Ativo</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {perfisFiltrados.map((perfil) => {
                  const sistema = perfil.tipo === 'sistema'
                  return (
                    <tr key={perfil.id}>
                      <td className="px-4 py-3">
                        <span className="font-medium text-slate-900">{perfil.nome}</span>
                        <br />
                        <span className="text-xs text-slate-400">{perfil.slug}</span>
                      </td>
                      <td className="px-4 py-3 text-slate-600">{perfil.descricao || '—'}</td>
                      <td className="px-4 py-3 text-slate-600">{perfil.usuarios_count}</td>
                      <td className="px-4 py-3">
                        <Badge tone={sistema ? 'sapphire' : 'slate'}>
                          {sistema ? 'Sistema' : 'Personalizado'}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        <Switch
                          checked={perfil.ativo}
                          disabled={sistema}
                          onChange={(ativo) => alternarAtivo.mutate({ perfilId: perfil.id, ativo })}
                          aria-label={`Ativar/desativar ${perfil.nome}`}
                        />
                      </td>
                      <td className="px-4 py-3">
                        <Badge tone={perfil.ativo ? 'green' : 'slate'}>
                          {perfil.ativo ? 'Ativo' : 'Inativo'}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => setPerfilPermissoes(perfil)}
                            className="rounded-md p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                            aria-label={`Permissões de ${perfil.nome}`}
                          >
                            <ShieldCheck className="h-4 w-4" aria-hidden />
                          </button>
                          <button
                            onClick={() => !sistema && setPerfilEditando(perfil)}
                            disabled={sistema}
                            className="rounded-md p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
                            aria-label={`Editar ${perfil.nome}`}
                          >
                            <Pencil className="h-4 w-4" aria-hidden />
                          </button>
                          <button
                            onClick={() => duplicar.mutate(perfil.id)}
                            className="rounded-md p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                            aria-label={`Duplicar ${perfil.nome}`}
                          >
                            <Copy className="h-4 w-4" aria-hidden />
                          </button>
                          <button
                            onClick={() => !sistema && setPerfilExcluindo(perfil)}
                            disabled={sistema}
                            className="rounded-md p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-40"
                            aria-label={`Excluir ${perfil.nome}`}
                          >
                            <Trash2 className="h-4 w-4" aria-hidden />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="p-6 text-sm text-slate-500">Nenhum perfil encontrado.</p>
        )}
      </Card>

      {modalAberto && <PerfilFormModal title="Novo perfil" onClose={() => setModalAberto(false)} />}
      {perfilEditando && (
        <PerfilFormModal
          title="Editar perfil"
          perfil={perfilEditando}
          onClose={() => setPerfilEditando(null)}
        />
      )}
      {perfilPermissoes && (
        <PermissoesPerfilModal perfil={perfilPermissoes} onClose={() => setPerfilPermissoes(null)} />
      )}
      {perfilExcluindo && (
        <ExcluirPerfilModal perfil={perfilExcluindo} onClose={() => setPerfilExcluindo(null)} />
      )}
    </div>
  )
}

function PerfilFormModal({
  title,
  perfil,
  onClose,
}: {
  title: string
  perfil?: Perfil
  onClose: () => void
}) {
  const [values, setValues] = useState<CriarPerfilValues>({
    nome: perfil?.nome ?? '',
    descricao: perfil?.descricao ?? '',
  })
  const [erro, setErro] = useState<string | null>(null)
  const criar = useCriarPerfil()
  const editar = useEditarPerfil(perfil?.id ?? '')

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setErro(null)
    try {
      if (perfil) {
        await editar.mutateAsync(values)
      } else {
        await criar.mutateAsync(values)
      }
      onClose()
    } catch (error) {
      setErro(getApiErrorMessage(error))
    }
  }

  const salvando = criar.isPending || editar.isPending

  return (
    <Modal title={title} onClose={onClose}>
      <form onSubmit={onSubmit} className="space-y-4">
        {erro && (
          <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {erro}
          </p>
        )}
        <div>
          <Label htmlFor="nome">Nome</Label>
          <Input
            id="nome"
            required
            value={values.nome}
            onChange={(event) => setValues((v) => ({ ...v, nome: event.target.value }))}
          />
        </div>
        <div>
          <Label htmlFor="descricao">Descrição</Label>
          <Input
            id="descricao"
            value={values.descricao}
            onChange={(event) => setValues((v) => ({ ...v, descricao: event.target.value }))}
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" isLoading={salvando}>
            Salvar
          </Button>
        </div>
      </form>
    </Modal>
  )
}

function permissoesIniciais(perfil: Perfil) {
  const mapa = {} as Record<ModuloSlug, (typeof perfil.function_permissions)[number]>
  for (const { slug } of MODULOS) {
    const existente = perfil.function_permissions.find((p) => p.function === slug)
    mapa[slug] = existente ?? {
      function: slug,
      can_view: false,
      can_create: false,
      can_edit: false,
      can_delete: false,
    }
  }
  return mapa
}

function PermissoesPerfilModal({ perfil, onClose }: { perfil: Perfil; onClose: () => void }) {
  const somenteLeitura = perfil.tipo === 'sistema'
  const [permissoes, setPermissoes] = useState(() => permissoesIniciais(perfil))
  const atualizar = useAtualizarPermissoesPerfil(perfil.id)

  function alternar(slug: ModuloSlug, campo: (typeof CAMPOS_PERMISSAO)[number]['campo']) {
    if (somenteLeitura) return
    setPermissoes((prev) => ({ ...prev, [slug]: { ...prev[slug], [campo]: !prev[slug][campo] } }))
  }

  function desmarcarTodos(slug: ModuloSlug) {
    if (somenteLeitura) return
    setPermissoes((prev) => ({
      ...prev,
      [slug]: { function: slug, can_view: false, can_create: false, can_edit: false, can_delete: false },
    }))
  }

  async function onSalvar() {
    await atualizar.mutateAsync(Object.values(permissoes))
    onClose()
  }

  return (
    <Modal title={`Permissões — ${perfil.nome}`} onClose={onClose}>
      <div className="space-y-4">
        <p className="text-sm text-slate-500">
          {somenteLeitura
            ? 'Perfil de sistema: acesso total e fixo, não pode ser alterado.'
            : 'Marque as ações que este perfil pode executar em cada módulo.'}
        </p>

        <div className="max-h-[26rem] space-y-3 overflow-y-auto pr-1">
          {MODULOS.map(({ slug, label }) => (
            <div key={slug} className="rounded-lg border border-slate-200 p-3">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-800">{label}</span>
                {!somenteLeitura && (
                  <button
                    type="button"
                    onClick={() => desmarcarTodos(slug)}
                    className="text-xs font-medium text-slate-500 hover:text-slate-700"
                  >
                    Desmarcar todos
                  </button>
                )}
              </div>
              <div className="flex flex-wrap gap-x-6 gap-y-2">
                {CAMPOS_PERMISSAO.map(({ campo, label: campoLabel }) => (
                  <label
                    key={campo}
                    className={cn(
                      'flex items-center gap-2 text-sm text-slate-700',
                      somenteLeitura && 'opacity-60',
                    )}
                  >
                    <input
                      type="checkbox"
                      checked={permissoes[slug][campo]}
                      onChange={() => alternar(slug, campo)}
                      disabled={somenteLeitura}
                      className="h-4 w-4 accent-sapphire-600"
                    />
                    {campoLabel}
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        {atualizar.isError && (
          <p className="text-xs text-red-600">Não foi possível salvar as permissões.</p>
        )}

        <div className="flex justify-end gap-2 border-t border-slate-200 pt-4">
          <Button type="button" variant="secondary" onClick={onClose}>
            {somenteLeitura ? 'Fechar' : 'Cancelar'}
          </Button>
          {!somenteLeitura && (
            <Button onClick={onSalvar} isLoading={atualizar.isPending}>
              Salvar permissões
            </Button>
          )}
        </div>
      </div>
    </Modal>
  )
}

function ExcluirPerfilModal({ perfil, onClose }: { perfil: Perfil; onClose: () => void }) {
  const excluir = useExcluirPerfil()
  const [erro, setErro] = useState<string | null>(null)

  async function onConfirm() {
    setErro(null)
    try {
      await excluir.mutateAsync(perfil.id)
      onClose()
    } catch (error) {
      setErro(getApiErrorMessage(error))
    }
  }

  return (
    <Modal title="Excluir perfil" onClose={onClose}>
      <div className="space-y-4">
        {erro && (
          <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {erro}
          </p>
        )}
        <p className="text-sm text-slate-600">
          Tem certeza que deseja excluir o perfil <strong>{perfil.nome}</strong>?
          {perfil.usuarios_count > 0 && (
            <>
              {' '}
              Não será possível excluir enquanto {perfil.usuarios_count} usuário(s) estiverem
              vinculados a ele.
            </>
          )}
        </p>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button variant="danger" onClick={onConfirm} isLoading={excluir.isPending}>
            Excluir
          </Button>
        </div>
      </div>
    </Modal>
  )
}
