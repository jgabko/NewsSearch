interface SentimentBalanceBarProps {
  positivas: number
  negativas: number
  neutras: number
}

/**
 * Barra horizontal única mostrando a proporção positivo/negativo/neutro do
 * período — o "balanço" pedido no requisito de métricas, num formato mais
 * rápido de ler do que um gráfico de pizza.
 */
export function SentimentBalanceBar({ positivas, negativas, neutras }: SentimentBalanceBarProps) {
  const total = positivas + negativas + neutras

  if (total === 0) {
    return (
      <div className="h-3 w-full rounded-full bg-muted" role="img" aria-label="Sem dados no período" />
    )
  }

  const pctPositivas = (positivas / total) * 100
  const pctNegativas = (negativas / total) * 100
  const pctNeutras = (neutras / total) * 100

  return (
    <div className="space-y-2">
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-muted">
        <div className="bg-positive" style={{ width: `${pctPositivas}%` }} title="Positivas" />
        <div className="bg-negative" style={{ width: `${pctNegativas}%` }} title="Negativas" />
        <div
          className="bg-neutral-sentiment"
          style={{ width: `${pctNeutras}%` }}
          title="Neutras"
        />
      </div>
      <div className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-muted-foreground">
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-positive" />
          Positivas — {pctPositivas.toFixed(0)}%
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-negative" />
          Negativas — {pctNegativas.toFixed(0)}%
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-neutral-sentiment" />
          Neutras — {pctNeutras.toFixed(0)}%
        </span>
      </div>
    </div>
  )
}