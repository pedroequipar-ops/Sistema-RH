import { Bell, Mail } from 'lucide-react'
import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { useEmails, useMarcarNotificacaoLida, useNotificacoes } from '@/hooks/useComunicacoes'
import { cn } from '@/lib/cn'
import { EMAIL_STATUS_LABEL, type EmailFilters, type EmailStatus } from '@/types/comunicacoes'

type Tab = 'emails' | 'notificacoes'

export function ComunicacoesPage() {
  const [searchParams] = useSearchParams()
  const [tab, setTab] = useState<Tab>(searchParams.get('tab') === 'notificacoes' ? 'notificacoes' : 'emails')

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Comunicações</h1>
        <p className="text-sm text-slate-500">Histórico de e-mails enviados e notificações internas.</p>
      </div>

      <div className="flex gap-1 border-b border-slate-200">
        <button
          onClick={() => setTab('emails')}
          className={cn(
            'flex items-center gap-1.5 border-b-2 px-3 py-2 text-sm font-medium',
            tab === 'emails'
              ? 'border-sapphire-600 text-sapphire-700'
              : 'border-transparent text-slate-500 hover:text-slate-700',
          )}
        >
          <Mail className="h-4 w-4" aria-hidden />
          E-mails enviados
        </button>
        <button
          onClick={() => setTab('notificacoes')}
          className={cn(
            'flex items-center gap-1.5 border-b-2 px-3 py-2 text-sm font-medium',
            tab === 'notificacoes'
              ? 'border-sapphire-600 text-sapphire-700'
              : 'border-transparent text-slate-500 hover:text-slate-700',
          )}
        >
          <Bell className="h-4 w-4" aria-hidden />
          Notificações
        </button>
      </div>

      {tab === 'emails' ? <EmailsTab /> : <NotificacoesTab />}
    </div>
  )
}

function EmailsTab() {
  const [filters, setFilters] = useState<EmailFilters>({ status: '', tipo: '' })
  const { data, isLoading, isError } = useEmails(filters)

  return (
    <div className="space-y-4">
      <Card className="p-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Select
            value={filters.status}
            onChange={(event) =>
              setFilters((prev) => ({ ...prev, status: event.target.value as EmailStatus | '' }))
            }
          >
            <option value="">Status: todos</option>
            {Object.entries(EMAIL_STATUS_LABEL).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </Select>
        </div>
      </Card>

      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner />
          </div>
        ) : isError ? (
          <p className="p-6 text-sm text-red-600">Não foi possível carregar os e-mails.</p>
        ) : data && data.results.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Destinatário</th>
                  <th className="px-4 py-3 font-medium">Assunto</th>
                  <th className="px-4 py-3 font-medium">Tipo</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Enviado em</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.results.map((email) => (
                  <tr key={email.id}>
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-900">{email.candidato_nome ?? '—'}</p>
                      <p className="text-xs text-slate-500">{email.destinatario}</p>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{email.assunto}</td>
                    <td className="px-4 py-3 text-slate-600">{email.tipo}</td>
                    <td className="px-4 py-3">
                      <Badge tone={email.status === 'enviado' ? 'green' : 'red'}>
                        {EMAIL_STATUS_LABEL[email.status]}
                      </Badge>
                      {email.status === 'falha' && email.erro && (
                        <p className="mt-1 max-w-xs text-xs text-red-500">{email.erro}</p>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {new Date(email.created_at).toLocaleString('pt-BR')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="p-6 text-sm text-slate-500">Nenhum e-mail encontrado.</p>
        )}
      </Card>
    </div>
  )
}

function NotificacoesTab() {
  const [somenteNaoLidas, setSomenteNaoLidas] = useState(false)
  const { data, isLoading, isError } = useNotificacoes({ lida: somenteNaoLidas ? 'false' : '' })
  const marcarLida = useMarcarNotificacaoLida()

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button variant={somenteNaoLidas ? 'primary' : 'secondary'} onClick={() => setSomenteNaoLidas((v) => !v)}>
          {somenteNaoLidas ? 'Mostrando só não lidas' : 'Mostrar só não lidas'}
        </Button>
      </div>

      <Card className="overflow-hidden">
        {isLoading ? (
          <div className="flex justify-center py-16">
            <Spinner />
          </div>
        ) : isError ? (
          <p className="p-6 text-sm text-red-600">Não foi possível carregar as notificações.</p>
        ) : data && data.results.length > 0 ? (
          <ul className="divide-y divide-slate-100">
            {data.results.map((notificacao) => (
              <li
                key={notificacao.id}
                className={cn('flex items-center justify-between gap-4 px-4 py-3', !notificacao.lida && 'bg-sapphire-50/50')}
              >
                <div>
                  <p className={cn('text-sm', notificacao.lida ? 'text-slate-600' : 'font-medium text-slate-900')}>
                    {notificacao.mensagem}
                  </p>
                  <p className="text-xs text-slate-400">
                    {new Date(notificacao.created_at).toLocaleString('pt-BR')}
                  </p>
                </div>
                {!notificacao.lida && (
                  <Button
                    variant="secondary"
                    isLoading={marcarLida.isPending}
                    onClick={() => marcarLida.mutate(notificacao.id)}
                  >
                    Marcar como lida
                  </Button>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="p-6 text-sm text-slate-500">Nenhuma notificação encontrada.</p>
        )}
      </Card>
    </div>
  )
}
