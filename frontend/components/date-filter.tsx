'use client'

import { useState, useMemo } from 'react'
import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { format, subDays } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { CalendarIcon, X } from 'lucide-react'
import type { DateRange } from 'react-day-picker'

import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { cn } from '@/lib/utils'

const PRESETS = [
  { label: 'Hoje', dias: 0 },
  { label: '7 dias', dias: 7 },
  { label: '30 dias', dias: 30 },
]

/**
 * Filtro de data da tela inicial. É um componente cliente que sincroniza o
 * intervalo escolhido com a URL (?de=YYYY-MM-DD&ate=YYYY-MM-DD), para que o
 * `page.tsx` (Server Component) leia os parâmetros e consulte o Supabase já
 * filtrado — sem necessidade de um client-side data-fetching à parte.
 */
export function DateFilter() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const [open, setOpen] = useState(false)

  const de = searchParams.get('de')
  const ate = searchParams.get('ate')

  const range: DateRange | undefined = useMemo(() => {
    if (!de) return undefined
    return { from: new Date(`${de}T00:00:00`), to: ate ? new Date(`${ate}T00:00:00`) : undefined }
  }, [de, ate])

  function aplicarIntervalo(from?: Date, to?: Date) {
    const params = new URLSearchParams(searchParams.toString())
    if (from) params.set('de', format(from, 'yyyy-MM-dd'))
    else params.delete('de')
    if (to) params.set('ate', format(to, 'yyyy-MM-dd'))
    else params.delete('ate')
    router.push(`${pathname}?${params.toString()}`)
  }

  function aplicarPreset(dias: number) {
    const hoje = new Date()
    const inicio = subDays(hoje, dias)
    aplicarIntervalo(inicio, hoje)
    setOpen(false)
  }

  function limpar() {
    aplicarIntervalo(undefined, undefined)
    setOpen(false)
  }

  const rotuloIntervalo =
    de && ate
      ? `${format(new Date(`${de}T00:00:00`), 'dd/MM/yy')} – ${format(new Date(`${ate}T00:00:00`), 'dd/MM/yy')}`
      : 'Todo o período'

  return (
    <div className="flex flex-wrap items-center gap-2">
      {PRESETS.map((preset) => (
        <Button
          key={preset.label}
          type="button"
          variant="outline"
          size="sm"
          onClick={() => aplicarPreset(preset.dias)}
          className="text-xs"
        >
          {preset.label}
        </Button>
      ))}

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className={cn('gap-1.5 text-xs', de && 'border-brand/40 text-brand')}
          >
            <CalendarIcon className="h-3.5 w-3.5" />
            {rotuloIntervalo}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="range"
            locale={ptBR}
            defaultMonth={range?.from}
            selected={range}
            onSelect={(novoRange) => {
              if (novoRange?.from && novoRange?.to) {
                aplicarIntervalo(novoRange.from, novoRange.to)
              }
            }}
            numberOfMonths={2}
          />
        </PopoverContent>
      </Popover>

      {de && (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={limpar}
          className="gap-1 text-xs text-muted-foreground"
        >
          <X className="h-3.5 w-3.5" />
          Limpar
        </Button>
      )}
    </div>
  )
}