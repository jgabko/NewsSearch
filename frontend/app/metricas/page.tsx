import { TrendingUp, TrendingDown, Minus, Newspaper } from 'lucide-react'

import { createClient } from '@/lib/supabase/server'
import { buscarResumoPeriodo } from '@/lib/data/noticias'
import { resolverPeriodo, parsePeriodo } from '@/lib/periodo'
import { NavHeader } from '@/components/nav-header'
import { PeriodFilter } from '@/components/period-filter'
import { StatCard } from '@/components/stat-card'
import { SentimentBalanceBar } from '@/components/sentiment-balance-bar'
import { SentimentTimelineChart } from '@/components/sentiment-timeline-chart'

interface MetricasPageProps {
  searchParams: Promise<{ periodo?: string }>
}

export default async function MetricasPage({ searchParams }: MetricasPageProps) {
  const { periodo: periodoParam } = await searchParams
  const periodo = parsePeriodo(periodoParam)
  const intervalo = resolverPeriodo(periodo)

  const supabase = await createClient()
  const { resumo, serieDiaria } = await buscarResumoPeriodo(supabase, intervalo)

  return (
    <div className="min-h-screen bg-background">
      <NavHeader />

      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="mb-8 flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">
              Métricas e sentimento
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Volume e balanço de sentimento das notícias monitoradas.
            </p>
          </div>
          <PeriodFilter ativo={periodo} />
        </div>

        {resumo.total === 0 ? (
          <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border py-20 text-center">
            <Newspaper className="h-8 w-8 text-muted-foreground/60" />
            <p className="text-sm text-muted-foreground">
              Nenhuma notícia encontrada nesse período.
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <StatCard label="Total de notícias" valor={resumo.total} icon={Newspaper} />
              <StatCard
                label="Positivas"
                valor={resumo.positivas}
                icon={TrendingUp}
                colorClass="text-positive"
              />
              <StatCard
                label="Negativas"
                valor={resumo.negativas}
                icon={TrendingDown}
                colorClass="text-negative"
              />
              <StatCard
                label="Neutras"
                valor={resumo.neutras}
                icon={Minus}
                colorClass="text-neutral-sentiment"
              />
            </div>

            <section className="rounded-xl border border-border bg-card p-5">
              <h2 className="mb-4 text-sm font-semibold text-foreground">
                Balanço do período
              </h2>
              <SentimentBalanceBar
                positivas={resumo.positivas}
                negativas={resumo.negativas}
                neutras={resumo.neutras}
              />
            </section>

            <section className="rounded-xl border border-border bg-card p-5">
              <h2 className="mb-4 text-sm font-semibold text-foreground">
                Volume diário por sentimento
              </h2>
              <SentimentTimelineChart serie={serieDiaria} />
            </section>
          </div>
        )}
      </main>
    </div>
  )
}