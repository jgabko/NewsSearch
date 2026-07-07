import { createClient } from '@/lib/supabase/server'
import { buscarNoticias } from '@/lib/data/noticias'
import { NavHeader } from '@/components/nav-header'
import { NewsCard } from '@/components/news-card'
import { DateFilter } from '@/components/date-filter'
import { Newspaper } from 'lucide-react'

interface HomeProps {
  searchParams: Promise<{ de?: string; ate?: string }>
}

export default async function Home({ searchParams }: HomeProps) {
  const { de, ate } = await searchParams
  const supabase = await createClient()
  const noticias = await buscarNoticias(supabase, { de, ate })

  return (
    <div className="min-h-screen bg-background">
      <NavHeader />

      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="mb-8 flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">
              Notícias monitoradas
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {noticias.length} notícia{noticias.length !== 1 ? 's' : ''} encontrada
              {noticias.length !== 1 ? 's' : ''}
              {de ? ' no período selecionado' : ''}.
            </p>
          </div>
          <DateFilter />
        </div>

        {noticias.length === 0 ? (
          <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-border py-20 text-center">
            <Newspaper className="h-8 w-8 text-muted-foreground/60" />
            <p className="text-sm text-muted-foreground">
              Nenhuma notícia encontrada{de ? ' para esse período' : ''}.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
            {noticias.map((noticia) => (
              <NewsCard key={noticia.id} noticia={noticia} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}