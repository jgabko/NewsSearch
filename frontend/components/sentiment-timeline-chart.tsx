'use client'

import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from 'recharts'
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart'

export interface PontoSerieDiaria {
  data: string // 'dd/MM'
  positivo: number
  negativo: number
  neutro: number
}

const chartConfig = {
  positivo: { label: 'Positivas', color: 'var(--color-positive)' },
  negativo: { label: 'Negativas', color: 'var(--color-negative)' },
  neutro: { label: 'Neutras', color: 'var(--color-neutral-sentiment)' },
} satisfies ChartConfig

interface SentimentTimelineChartProps {
  serie: PontoSerieDiaria[]
}

/** Volume de notícias por dia, empilhado por sentimento, dentro do período selecionado. */
export function SentimentTimelineChart({ serie }: SentimentTimelineChartProps) {
  return (
    <ChartContainer config={chartConfig} className="h-64 w-full">
      <BarChart data={serie}>
        <CartesianGrid vertical={false} strokeDasharray="3 3" />
        <XAxis
          dataKey="data"
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          className="text-xs"
        />
        <YAxis tickLine={false} axisLine={false} tickMargin={8} width={28} className="text-xs" allowDecimals={false} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar dataKey="positivo" stackId="sentimento" fill="var(--color-positive)" radius={[0, 0, 0, 0]} />
        <Bar dataKey="negativo" stackId="sentimento" fill="var(--color-negative)" />
        <Bar
          dataKey="neutro"
          stackId="sentimento"
          fill="var(--color-neutral-sentiment)"
          radius={[3, 3, 0, 0]}
        />
      </BarChart>
    </ChartContainer>
  )
}