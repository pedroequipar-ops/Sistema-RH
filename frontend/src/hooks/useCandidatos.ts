import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { deleteCandidato, getCandidato, listCandidatos, uploadCurriculo } from '@/api/candidatos'
import type { CandidatoFilters } from '@/types/candidatos'

const candidatosKeys = {
  all: ['candidatos'] as const,
  list: (filters: CandidatoFilters) => [...candidatosKeys.all, 'list', filters] as const,
  detail: (id: string) => [...candidatosKeys.all, 'detail', id] as const,
}

export function useCandidatos(filters: CandidatoFilters) {
  return useQuery({
    queryKey: candidatosKeys.list(filters),
    queryFn: () => listCandidatos(filters),
  })
}

export function useCandidato(id: string) {
  return useQuery({
    queryKey: candidatosKeys.detail(id),
    queryFn: () => getCandidato(id),
    enabled: !!id,
  })
}

export function useDeleteCandidato() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteCandidato(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: candidatosKeys.all }),
  })
}

export function useUploadCurriculo(id: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => uploadCurriculo(id, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: candidatosKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: candidatosKeys.all })
    },
  })
}
