import { useState } from 'react'

import { Button } from '@/components/ui/Button'
import { Label } from '@/components/ui/Label'
import { Modal } from '@/components/ui/Modal'
import { Textarea } from '@/components/ui/Textarea'

export function ConfirmActionModal({
  title,
  description,
  error,
  confirmLabel,
  variant = 'primary',
  isLoading,
  onConfirm,
  onClose,
}: {
  title: string
  description: string
  error?: string | null
  confirmLabel: string
  variant?: 'primary' | 'danger'
  isLoading: boolean
  onConfirm: (observacao: string) => void
  onClose: () => void
}) {
  const [observacao, setObservacao] = useState('')

  return (
    <Modal title={title} onClose={onClose}>
      <p className="mb-4 text-sm text-slate-600">{description}</p>
      {error && (
        <p className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}
      <div className="mb-5">
        <Label htmlFor="observacao">Observação (opcional)</Label>
        <Textarea
          id="observacao"
          rows={3}
          value={observacao}
          onChange={(event) => setObservacao(event.target.value)}
        />
      </div>
      <div className="flex justify-end gap-2">
        <Button type="button" variant="secondary" onClick={onClose}>
          Cancelar
        </Button>
        <Button
          type="button"
          variant={variant}
          isLoading={isLoading}
          onClick={() => onConfirm(observacao)}
        >
          {confirmLabel}
        </Button>
      </div>
    </Modal>
  )
}
