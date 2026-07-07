import { subDays, startOfDay, endOfDay } from 'date-fns'

export type PeriodoKey = '7d' | '30d' | '90d' | 'tudo'

export const PERIODOS: { key: PeriodoKey; label: string }[] = [
  { key: '7d', label: '7 dias' },
  { key: '30d', label: '30 dias' },
  { key: '90d', label: '90 dias' },
  { key: 'tudo', label: 'Tudo' },
]

/**
 * Resolve um `PeriodoKey` (ex: "30d") em um intervalo [inicio, fim] de datas.
 * `fim` é sempre o instante atual; `inicio` é `null` para "tudo" (sem filtro).
 */
export function resolverPeriodo(periodo: PeriodoKey): { inicio: Date | null; fim: Date } {
  const fim = new Date()

  switch (periodo) {
    case '7d':
      return { inicio: startOfDay(subDays(fim, 7)), fim }
    case '30d':
      return { inicio: startOfDay(subDays(fim, 30)), fim }
    case '90d':
      return { inicio: startOfDay(subDays(fim, 90)), fim }
    case 'tudo':
    default:
      return { inicio: null, fim }
  }
}

export function parsePeriodo(valor: string | undefined): PeriodoKey {
  const chaves = PERIODOS.map((p) => p.key)
  return (chaves as string[]).includes(valor ?? '') ? (valor as PeriodoKey) : '30d'
}

/** Converte um valor de data (YYYY-MM-DD vindo da URL) para o fim do dia, em ISO. */
export function fimDoDiaISO(data: string): string {
  return endOfDay(new Date(`${data}T00:00:00`)).toISOString()
}

/** Converte um valor de data (YYYY-MM-DD vindo da URL) para o início do dia, em ISO. */
export function inicioDoDiaISO(data: string): string {
  return startOfDay(new Date(`${data}T00:00:00`)).toISOString()
}