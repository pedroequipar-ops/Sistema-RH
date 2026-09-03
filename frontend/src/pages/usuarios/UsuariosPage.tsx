import { Pencil, Plus, Search, Trash2 } from 'lucide-react'
import { type FormEvent, useMemo, useState } from 'react'

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Modal } from '@/components/ui/Modal'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { Switch } from '@/components/ui/Switch'
import { usePerfis } from '@/hooks/usePerfis'
import {
  useAlternarAtivoUsuario,
  useAtribuirPerfil,
  useCriarUsuario,
  useEditarUsuario,
  useExcluirUsuario,
  useUsuarios,
} from '@/hooks/useUsuarios'
import { getApiErrorMessage } from '@/lib/apiError'
import type { CriarUsuarioValues, EditarUsuarioValues, Usuario } from '@/types/usuarios'

export function UsuariosPage() {
  const { data, isLoading, isError } = useUsuarios()
  const { data: perfisData } = usePerfis()
  const [busca, setBusca] = useState('')
  const [modalAberto, setModalAberto] = useState(false)
  const [usuarioEditando, setUsuarioEditando] = useState<Usuario | null>(null)
  const [usuarioExcluindo, setUsuarioExcluindo] = useState<Usuario | null>(null)

  const perfis = perfisData?.results ?? []

  const usuariosFiltrados = useMemo(() => {
    const termo = busca.trim().toLowerCase()
    if (!termo) return data?.results ?? []
    return (data?.results ?? []).filter(
      (usuario) =>
        usuario.full_name.toLowerCase().includes(termo) ||
        usuario.email.toLowerCase().includes(termo),
    )
  }, [data, busca])

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Usuários</h1>
          <p className="text-sm text-slate-500">Gerencie usuários e perfis de acesso.</p>
        </div>
        <Button onClick={() => setModalAberto(true)}>
          <Plus className="h-4 w-4" aria-hidden />
          Novo usuário
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
          aria-hidden
        />
        <Input
          placeholder="Buscar por nome..."
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
          <p className="p-6 text-sm text-red-600">Não foi possível carregar os usuários.</p>
        ) : usuariosFiltrados.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Nome</th>
                  <th className="px-4 py-3 font-medium">Email</th>
                  <th className="px-4 py-3 font-medium">Perfil de acesso</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Ativo</th>
                  <th className="px-4 py-3 font-medium" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {usuariosFiltrados.map((usuario) => (
                  <UsuarioRow
                    key={usuario.id}
                    usuario={usuario}
                    perfis={perfis}
                    onEditar={() => setUsuarioEditando(usuario)}
                    onExcluir={() => setUsuarioExcluindo(usuario)}
                  />
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="p-6 text-sm text-slate-500">Nenhum usuário encontrado.</p>
        )}
      </Card>

      {modalAberto && <NovoUsuarioModal onClose={() => setModalAberto(false)} />}
      {usuarioEditando && (
        <EditarUsuarioModal usuario={usuarioEditando} onClose={() => setUsuarioEditando(null)} />
      )}
      {usuarioExcluindo && (
        <ExcluirUsuarioModal usuario={usuarioExcluindo} onClose={() => setUsuarioExcluindo(null)} />
      )}
    </div>
  )
}

function UsuarioRow({
  usuario,
  perfis,
  onEditar,
  onExcluir,
}: {
  usuario: Usuario
  perfis: { id: string; nome: string; ativo: boolean }[]
  onEditar: () => void
  onExcluir: () => void
}) {
  const atribuirPerfil = useAtribuirPerfil()
  const alternarAtivo = useAlternarAtivoUsuario()

  return (
    <tr>
      <td className="px-4 py-3 font-medium text-slate-900">{usuario.full_name}</td>
      <td className="px-4 py-3 text-slate-600">{usuario.email}</td>
      <td className="px-4 py-3">
        <Select
          className="min-w-[10rem]"
          value={usuario.perfil ?? ''}
          onChange={(event) =>
            atribuirPerfil.mutate({ usuarioId: usuario.id, perfil: event.target.value || null })
          }
        >
          <option value="">Selecione um perfil</option>
          {perfis.map((perfil) => (
            <option key={perfil.id} value={perfil.id}>
              {perfil.nome}
            </option>
          ))}
        </Select>
      </td>
      <td className="px-4 py-3">
        <Badge tone={usuario.is_active ? 'green' : 'slate'}>
          {usuario.is_active ? 'Ativo' : 'Inativo'}
        </Badge>
      </td>
      <td className="px-4 py-3">
        <Switch
          checked={usuario.is_active}
          onChange={(checked) => alternarAtivo.mutate({ usuarioId: usuario.id, is_active: checked })}
          aria-label={`Ativar/desativar ${usuario.full_name}`}
        />
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-1">
          <button
            onClick={onEditar}
            className="rounded-md p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
            aria-label={`Editar ${usuario.full_name}`}
          >
            <Pencil className="h-4 w-4" aria-hidden />
          </button>
          <button
            onClick={onExcluir}
            className="rounded-md p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600"
            aria-label={`Excluir ${usuario.full_name}`}
          >
            <Trash2 className="h-4 w-4" aria-hidden />
          </button>
        </div>
      </td>
    </tr>
  )
}

function NovoUsuarioModal({ onClose }: { onClose: () => void }) {
  const [values, setValues] = useState<CriarUsuarioValues>({ email: '', full_name: '', password: '' })
  const [erro, setErro] = useState<string | null>(null)
  const criar = useCriarUsuario()

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setErro(null)
    try {
      await criar.mutateAsync(values)
      onClose()
    } catch (error) {
      setErro(getApiErrorMessage(error))
    }
  }

  return (
    <Modal title="Novo usuário" onClose={onClose}>
      <form onSubmit={onSubmit} className="space-y-4">
        {erro && (
          <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {erro}
          </p>
        )}
        <div>
          <Label htmlFor="full_name">Nome</Label>
          <Input
            id="full_name"
            required
            value={values.full_name}
            onChange={(event) => setValues((v) => ({ ...v, full_name: event.target.value }))}
          />
        </div>
        <div>
          <Label htmlFor="email">E-mail</Label>
          <Input
            id="email"
            type="email"
            required
            value={values.email}
            onChange={(event) => setValues((v) => ({ ...v, email: event.target.value }))}
          />
        </div>
        <div>
          <Label htmlFor="password">Senha</Label>
          <Input
            id="password"
            type="password"
            required
            minLength={6}
            value={values.password}
            onChange={(event) => setValues((v) => ({ ...v, password: event.target.value }))}
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" isLoading={criar.isPending}>
            Criar
          </Button>
        </div>
      </form>
    </Modal>
  )
}

function EditarUsuarioModal({ usuario, onClose }: { usuario: Usuario; onClose: () => void }) {
  const [values, setValues] = useState<EditarUsuarioValues>({
    full_name: usuario.full_name,
    email: usuario.email,
    area: usuario.area,
  })
  const [erro, setErro] = useState<string | null>(null)
  const editar = useEditarUsuario(usuario.id)

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setErro(null)
    try {
      await editar.mutateAsync(values)
      onClose()
    } catch (error) {
      setErro(getApiErrorMessage(error))
    }
  }

  return (
    <Modal title="Editar usuário" onClose={onClose}>
      <form onSubmit={onSubmit} className="space-y-4">
        {erro && (
          <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {erro}
          </p>
        )}
        <div>
          <Label htmlFor="edit_full_name">Nome</Label>
          <Input
            id="edit_full_name"
            required
            value={values.full_name}
            onChange={(event) => setValues((v) => ({ ...v, full_name: event.target.value }))}
          />
        </div>
        <div>
          <Label htmlFor="edit_email">E-mail</Label>
          <Input
            id="edit_email"
            type="email"
            required
            value={values.email}
            onChange={(event) => setValues((v) => ({ ...v, email: event.target.value }))}
          />
        </div>
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" isLoading={editar.isPending}>
            Salvar
          </Button>
        </div>
      </form>
    </Modal>
  )
}

function ExcluirUsuarioModal({ usuario, onClose }: { usuario: Usuario; onClose: () => void }) {
  const excluir = useExcluirUsuario()
  const [erro, setErro] = useState<string | null>(null)

  async function onConfirm() {
    setErro(null)
    try {
      await excluir.mutateAsync(usuario.id)
      onClose()
    } catch (error) {
      setErro(getApiErrorMessage(error))
    }
  }

  return (
    <Modal title="Excluir usuário" onClose={onClose}>
      <div className="space-y-4">
        {erro && (
          <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {erro}
          </p>
        )}
        <p className="text-sm text-slate-600">
          Tem certeza que deseja excluir <strong>{usuario.full_name}</strong>? O acesso ao sistema
          será removido.
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
