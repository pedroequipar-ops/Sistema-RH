import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowLeft } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Label } from '@/components/ui/Label'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { useAuth } from '@/context/AuthContext'
import { useCreateVaga } from '@/hooks/useVagas'
import { getApiErrorMessage } from '@/lib/apiError'
import { TIPO_VAGA_LABEL } from '@/types/vagas'

const vagaSchema = z.object({
  cargo: z.string().min(1, 'Informe o cargo.'),
  descricao: z.string().min(1, 'Informe a descrição.'),
  requisitos: z.string().min(1, 'Informe os requisitos.'),
  salario: z.string().optional(),
  area_solicitante: z.string().min(1, 'Informe a área.'),
  tipo: z.enum(['interna', 'externa']),
})

type VagaFormValues = z.infer<typeof vagaSchema>

export function VagaFormPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const createVaga = useCreateVaga()
  const isGestor = user?.role === 'gestor'

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<VagaFormValues>({
    resolver: zodResolver(vagaSchema),
    defaultValues: {
      tipo: 'externa',
      area_solicitante: isGestor ? user?.area ?? '' : '',
    },
  })

  async function onSubmit(values: VagaFormValues) {
    try {
      const vaga = await createVaga.mutateAsync({ ...values, salario: values.salario ?? '' })
      navigate(`/vagas/${vaga.id}`)
    } catch {
      // erro exibido abaixo do formulário
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <Link to="/vagas" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700">
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Voltar para vagas
      </Link>

      <Card>
        <CardHeader>
          <CardTitle>Nova vaga</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {createVaga.isError && (
              <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                {getApiErrorMessage(createVaga.error)}
              </p>
            )}

            <div>
              <Label htmlFor="cargo">Cargo</Label>
              <Input id="cargo" invalid={!!errors.cargo} {...register('cargo')} />
              {errors.cargo && <p className="mt-1 text-xs text-red-600">{errors.cargo.message}</p>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="area_solicitante">Área solicitante</Label>
                <Input
                  id="area_solicitante"
                  disabled={isGestor}
                  invalid={!!errors.area_solicitante}
                  {...register('area_solicitante')}
                />
                {isGestor && (
                  <p className="mt-1 text-xs text-slate-400">Definida automaticamente pela sua área.</p>
                )}
              </div>
              <div>
                <Label htmlFor="tipo">Tipo</Label>
                <Select id="tipo" {...register('tipo')}>
                  {Object.entries(TIPO_VAGA_LABEL).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </Select>
              </div>
            </div>

            <div>
              <Label htmlFor="salario">Salário (opcional)</Label>
              <Input id="salario" type="number" step="0.01" {...register('salario')} />
            </div>

            <div>
              <Label htmlFor="descricao">Descrição</Label>
              <Textarea
                id="descricao"
                rows={4}
                invalid={!!errors.descricao}
                {...register('descricao')}
              />
              {errors.descricao && (
                <p className="mt-1 text-xs text-red-600">{errors.descricao.message}</p>
              )}
            </div>

            <div>
              <Label htmlFor="requisitos">Requisitos</Label>
              <Textarea
                id="requisitos"
                rows={4}
                invalid={!!errors.requisitos}
                {...register('requisitos')}
              />
              {errors.requisitos && (
                <p className="mt-1 text-xs text-red-600">{errors.requisitos.message}</p>
              )}
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="secondary" onClick={() => navigate('/vagas')}>
                Cancelar
              </Button>
              <Button type="submit" isLoading={createVaga.isPending}>
                Criar vaga
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
