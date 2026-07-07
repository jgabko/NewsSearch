import type { SupabaseClient } from '@supabase/supabase-js'
import { format } from 'date-fns'
import type { Noticia, ResumoSentimento } from '@/lib/types'
import type { PontoSerieDiaria } from '@/components/sentiment-timeline-chart'

const TABELA = 'newssearch_articles'

interface FiltroData {
  de?: string | null // 'YYYY-MM-DD'
  ate?: string | null // 'YYYY-MM-DD'
}

/** Lista notícias mais recentes primeiro, com filtro opcional de intervalo de datas. */
export async function buscarNoticias(
  supabase: SupabaseClient,
  filtro: FiltroData = {},
): Promise<Noticia[]> {
  let query = supabase.from(TABELA).select('*').order('data_coleta', { ascending: false })

  if (filtro.de) {
    query = query.gte('data_coleta', `${filtro.de}T00:00:00.000Z`)
  }
  if (filtro.ate) {
    query = query.lte('data_coleta', `${filtro.ate}T23:59:59.999Z`)
  }

  const { data, error } = await query

  if (error) {
    console.error('[NewsSearch] Erro ao buscar notícias:', error.message)
    return []
  }

  return data ?? []
}

/** Busca uma única notícia pelo id, para a página de detalhe. */
export async function buscarNoticiaPorId(
  supabase: SupabaseClient,
  id: string | number,
): Promise<Noticia | null> {
  const { data, error } = await supabase.from(TABELA).select('*').eq('id', id).single()

  if (error) {
    console.error('[NewsSearch] Erro ao buscar notícia por id:', error.message)
    return null
  }

  return data
}

/**
 * Busca as notícias dentro de um intervalo e retorna tanto o resumo total
 * (contadores) quanto a série diária, prontos para a página de métricas.
 *
 * Observação de engenharia: a agregação é feita em memória após buscar as
 * linhas do período. Para volumes muito grandes, o ideal seria mover essa
 * contagem para uma view/RPC no Postgres — mantido simples aqui de propósito,
 * compatível com o volume esperado da pipeline local.
 */
export async function buscarResumoPeriodo(
  supabase: SupabaseClient,
  intervalo: { inicio: Date | null; fim: Date },
): Promise<{ resumo: ResumoSentimento; serieDiaria: PontoSerieDiaria[] }> {
  let query = supabase
    .from(TABELA)
    .select('sentimento, data_coleta')
    .lte('data_coleta', intervalo.fim.toISOString())
    .order('data_coleta', { ascending: true })

  if (intervalo.inicio) {
    query = query.gte('data_coleta', intervalo.inicio.toISOString())
  }

  const { data, error } = await query

  if (error) {
    console.error('[NewsSearch] Erro ao buscar resumo de métricas:', error.message)
    return { resumo: { total: 0, positivas: 0, negativas: 0, neutras: 0 }, serieDiaria: [] }
  }

  const linhas = data ?? []

  const resumo: ResumoSentimento = {
    total: linhas.length,
    positivas: linhas.filter((l) => l.sentimento === 'positivo').length,
    negativas: linhas.filter((l) => l.sentimento === 'negativo').length,
    neutras: linhas.filter((l) => l.sentimento === 'neutro').length,
  }

  const porDia = new Map<string, PontoSerieDiaria>()
  for (const linha of linhas) {
    const chave = format(new Date(linha.data_coleta), 'dd/MM')
    const ponto = porDia.get(chave) ?? { data: chave, positivo: 0, negativo: 0, neutro: 0 }
    if (linha.sentimento === 'positivo') ponto.positivo += 1
    else if (linha.sentimento === 'negativo') ponto.negativo += 1
    else ponto.neutro += 1
    porDia.set(chave, ponto)
  }

  const serieDiaria = Array.from(porDia.values())

  return { resumo, serieDiaria }
}