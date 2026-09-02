// Formata um campo de data pura (YYYY-MM-DD, sem horário) sem passar por
// conversão de fuso horário — new Date('YYYY-MM-DD') é interpretado como
// UTC e, ao formatar no fuso local (America/Sao_Paulo, UTC-3), voltava um
// dia (ex: "2026-09-15" virava "14/09/2026").
export function formatDateOnly(value: string) {
  const [year, month, day] = value.split('-')
  return `${day}/${month}/${year}`
}
