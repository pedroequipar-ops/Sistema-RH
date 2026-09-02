import { useState } from 'react'

import { Button } from '@/components/ui/Button'
import { Label } from '@/components/ui/Label'
import { Modal } from '@/components/ui/Modal'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { ETAPA_LABEL, TRANSICOES_PERMITIDAS, type Etapa } from '@/types/processos'

export function MoverEtapaModal({
  etapaAtual,
  error,
  isLoading,
  onConfirm,
  onClose,
}: {
  etapaAtual: Etapa
  error?: string | null
  isLoading: boolean
  onConfirm: (etapa: Etapa, observacao: string) => void
  onClose: () => void
}) {
  const opcoes = TRANSICOES_PERMITIDAS[etapaAtual]
  const [etapa, setEtapa] = useState<Etapa | ''>(opcoes[0] ?? '')
  const [observacao, setObservacao] = useState('')

  return (
    <Modal title="Mover etapa" onClose={onClose}>
      {opcoes.length === 0 ? (
        <p className="text-sm text-slate-600">
          Esta é uma etapa final ({ETAPA_LABEL[etapaAtual]}); não há para onde mover.
        </p>
      ) : (
        <>
          {error && (
            <p className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          )}
          <div className="mb-4">
            <Label htmlFor="etapa">Nova etapa</Label>
            <Select id="etapa" value={etapa} onChange={(event) => setEtapa(event.target.value as Etapa)}>
              {opcoes.map((opcao) => (
                <option key={opcao} value={opcao}>
                  {ETAPA_LABEL[opcao]}
                </option>
              ))}
            </Select>
          </div>
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
              isLoading={isLoading}
              onClick={() => etapa && onConfirm(etapa, observacao)}
            >
              Confirmar
            </Button>
          </div>
        </>
      )}
    </Modal>
  )
}
