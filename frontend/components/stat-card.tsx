import { cn } from '@/lib/utils'
import type { LucideIcon } from 'lucide-react'

interface StatCardProps {
  label: string
  valor: number
  icon: LucideIcon
  /** Classe de cor do texto/ícone (ex: "text-positive"). Padrão: texto neutro. */
  colorClass?: string
}

export function StatCard({ label, valor, icon: Icon, colorClass }: StatCardProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </span>
        <Icon className={cn('h-4 w-4 text-muted-foreground', colorClass)} />
      </div>
      <p className={cn('mt-3 font-mono text-3xl font-semibold tabular-nums text-foreground', colorClass)}>
        {valor.toLocaleString('pt-BR')}
      </p>
    </div>
  )
}