import { cn } from '@/lib/utils'
import { sentimentoConfig } from '@/lib/sentiment'
import type { Sentimento } from '@/lib/types'

interface SentimentBadgeProps {
  sentimento: Sentimento
  size?: 'sm' | 'lg'
  className?: string
}

/**
 * Sinalização visual do sentimento de uma notícia. Cores intuitivas
 * (verde/vermelho/âmbar) + ícone, para que o resultado da análise de IA
 * seja reconhecível de imediato, tanto nos cards quanto na página de detalhe.
 */
export function SentimentBadge({ sentimento, size = 'sm', className }: SentimentBadgeProps) {
  const config = sentimentoConfig(sentimento)
  const Icon = config.icon

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border font-medium',
        config.badgeClass,
        size === 'sm' ? 'px-2.5 py-1 text-xs' : 'px-4 py-2 text-sm',
        className,
      )}
    >
      <Icon className={size === 'sm' ? 'h-3.5 w-3.5' : 'h-4 w-4'} strokeWidth={2.5} />
      {config.label}
    </span>
  )
}