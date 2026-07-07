import { TrendingDown, TrendingUp, Minus, type LucideIcon } from 'lucide-react'
import type { Sentimento } from '@/lib/types'

interface SentimentoConfig {
  label: string
  icon: LucideIcon
  /** Classes para badges/indicadores compactos (fundo suave + texto colorido). */
  badgeClass: string
  /** Classes para a faixa de destaque na página de detalhe (fundo sólido). */
  heroClass: string
  /** Cor sólida usada em barras de progresso e gráficos. */
  barClass: string
}

const CONFIG: Record<Sentimento, SentimentoConfig> = {
  positivo: {
    label: 'Positivo',
    icon: TrendingUp,
    badgeClass: 'bg-positive-bg text-positive border-positive/20',
    heroClass: 'bg-positive-bg text-positive border-positive/30',
    barClass: 'bg-positive',
  },
  negativo: {
    label: 'Negativo',
    icon: TrendingDown,
    badgeClass: 'bg-negative-bg text-negative border-negative/20',
    heroClass: 'bg-negative-bg text-negative border-negative/30',
    barClass: 'bg-negative',
  },
  neutro: {
    label: 'Neutro',
    icon: Minus,
    badgeClass: 'bg-neutral-sentiment-bg text-neutral-sentiment border-neutral-sentiment/20',
    heroClass: 'bg-neutral-sentiment-bg text-neutral-sentiment border-neutral-sentiment/30',
    barClass: 'bg-neutral-sentiment',
  },
}

export function sentimentoConfig(sentimento: Sentimento): SentimentoConfig {
  return CONFIG[sentimento] ?? CONFIG.neutro
}