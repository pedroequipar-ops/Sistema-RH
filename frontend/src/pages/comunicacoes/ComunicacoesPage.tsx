import { useState } from 'react'

import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { Spinner } from '@/components/ui/Spinner'
import { useEmails } from '@/hooks/useComunicacoes'
import { EMAIL_STATUS_LABEL, type EmailFilters, type EmailStatus } from '@/types/comunicacoes'

export function ComunicacoesPage() {
  const [filters, setFilters] = useState<EmailFilters>({ status: '', tipo: '' })
  const { data, isLoading, isError } = useEmails(filters)

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Comunicações</h1>
        <p className="text-sm text-slate-500">Histórico de e-mails enviados aos candidatos.</p>
      </div>

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
