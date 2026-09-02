export type TempoMedioContratacao = {
  tempo_medio_dias: number | null
  total_contratacoes: number
}

export type CandidatosPorVaga = {
  vaga_id: string
  vaga_cargo: string
  total_candidatos: number
}

export type FunilEtapa = {
  etapa: string
  entraram: number
  avancaram: number | null
  taxa_conversao: number | null
}

export type CustoContratacaoVaga = {
  vaga_id: string
  cargo: string
  custo_contratacao: string
}

export type CustoContratacao = {
  vagas: CustoContratacaoVaga[]
  custo_medio: string | null
  custo_total: string
}
