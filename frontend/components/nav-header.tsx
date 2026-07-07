'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Radar } from 'lucide-react'
import { cn } from '@/lib/utils'

const LINKS = [
  { href: '/', label: 'Notícias' },
  { href: '/metricas', label: 'Métricas' },
]

export function NavHeader() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-10 border-b border-border bg-background/85 backdrop-blur supports-[backdrop-filter]:bg-background/70">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-md bg-brand text-brand-foreground">
            <Radar className="h-4.5 w-4.5" strokeWidth={2.25} />
          </span>
          <span className="text-base font-semibold tracking-tight text-foreground">
            NewsSearch
          </span>
        </Link>

        <nav className="flex items-center gap-1">
          {LINKS.map((link) => {
            const ativo = link.href === '/' ? pathname === '/' : pathname.startsWith(link.href)
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
                  ativo
                    ? 'bg-brand/10 text-brand'
                    : 'text-muted-foreground hover:bg-accent hover:text-foreground',
                )}
              >
                {link.label}
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}