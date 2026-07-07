'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { PERIODOS, type PeriodoKey } from '@/lib/periodo'

interface PeriodFilterProps {
  ativo: PeriodoKey
}

/**
 * Controle segmentado para escolher o escopo de tempo das métricas.
 * Sincroniza com a URL (?periodo=) para que a página (Server Component)
 * refaça a consulta agregada no servidor a cada mudança.
 */
export function PeriodFilter({ ativo }: PeriodFilterProps) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  function selecionar(periodo: PeriodoKey) {
    const params = new URLSearchParams(searchParams.toString())
    params.set('periodo', periodo)
    router.push(`${pathname}?${params.toString()}`)
  }

  return (
    <div className="inline-flex items-center gap-1 rounded-lg border border-border bg-muted/40 p-1">
      {PERIODOS.map((periodo) => (
        <button
          key={periodo.key}
          type="button"
          onClick={() => selecionar(periodo.key)}
          className={cn(
            'rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
            ativo === periodo.key
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground',
          )}
        >
          {periodo.label}
        </button>
      ))}
    </div>
  )
}