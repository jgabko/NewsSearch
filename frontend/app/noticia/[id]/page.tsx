import Link from 'next/link'
import { notFound } from 'next/navigation'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { ArrowLeft, ExternalLink } from 'lucide-react'

import { createClient } from '@/lib/supabase/server'
import { buscarNoticiaPorId } from '@/lib/data/noticias'
import { NavHeader } from '@/components/nav-header'
import { SentimentBadge } from '@/components/sentiment-badge'
import { sentimentoConfig } from '@/lib/sentiment'
import { resolverDataExibicao } from '@/lib/format-date'

interface NoticiaPageProps {
  params: Promise<{ id: string }>
}

export default async function NoticiaPage({ params }: NoticiaPageProps) {
  const { id } = await params
  const supabase = await createClient()
  const noticia = await buscarNoticiaPorId(supabase, id)

  if (!noticia) {
    notFound()
  }

  const config = sentimentoConfig(noticia.sentimento)
  const dataReferencia = resolverDataExibicao(noticia.data_publicacao, noticia.data_coleta)
  const dataFormatada = format(dataReferencia, "d 'de' MMMM 'de' yyyy", { locale: ptBR })

  return (
    <div className="min-h-screen bg-background">
      <NavHeader />

      <main className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
        <Link
          href="/"
          className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Voltar para notícias
        </Link>

        {/* Sinalização de sentimento — requisito visual de destaque */}
        <div className={`mb-6 rounded-xl border p-4 ${config.heroClass}`}>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <SentimentBadge sentimento={noticia.sentimento} size="lg" />
            {noticia.empresa_alvo && (
              <span className="text-sm font-medium opacity-80">
                Sobre: {noticia.empresa_alvo}
              </span>
            )}
          </div>
          {noticia.sentimento_justificativa && (
            <p className="mt-3 text-sm leading-relaxed opacity-90">
              {noticia.sentimento_justificativa}
            </p>
          )}
        </div>

        <article>
          <header className="mb-6 border-b border-border pb-6">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {noticia.fonte ?? 'Fonte desconhecida'}
            </p>
            <h1 className="mt-2 text-2xl font-semibold leading-tight tracking-tight text-balance text-foreground sm:text-3xl">
              {noticia.titulo}
            </h1>
            <time
              dateTime={dataReferencia.toISOString()}
              className="mt-3 block font-mono text-sm text-muted-foreground tabular-nums"
            >
              {dataFormatada}
            </time>
          </header>

          {noticia.corpo ? (
            <p className="whitespace-pre-line text-base leading-relaxed text-foreground/90">
              {noticia.corpo}
            </p>
          ) : (
            <p className="text-sm text-muted-foreground">
              Prévia de conteúdo não disponível para esta notícia.
            </p>
          )}

          
            href={noticia.url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-8 inline-flex items-center gap-2 rounded-md bg-brand px-4 py-2.5 text-sm font-medium text-brand-foreground transition-opacity hover:opacity-90"
          >
            Ler notícia completa na fonte original
            <ExternalLink className="h-4 w-4" />
          </a>
        </article>
      </main>
    </div>
  )
}