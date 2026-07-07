import Link from 'next/link'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { SentimentBadge } from '@/components/sentiment-badge'
import { sentimentoConfig } from '@/lib/sentiment'
import { resolverDataExibicao } from '@/lib/format-date'
import type { Noticia } from '@/lib/types'

interface NewsCardProps {
  noticia: Noticia
}

/**
 * Card clicável de notícia. A faixa colorida à esquerda ("signal bar") é o
 * elemento de assinatura visual do NewsSearch: o sentimento fica perceptível
 * antes mesmo de ler o badge, escaneando a grade de cards.
 */
export function NewsCard({ noticia }: NewsCardProps) {
  const config = sentimentoConfig(noticia.sentimento)
  const dataReferencia = resolverDataExibicao(noticia.data_publicacao, noticia.data_coleta)
  const dataFormatada = format(dataReferencia, "d 'de' MMMM, yyyy", { locale: ptBR })

  return (
    <Link href={`/noticia/${noticia.id}`} className="group block h-full">
      <Card className="relative h-full flex-col overflow-hidden border-border py-0 shadow-sm transition-all duration-200 group-hover:-translate-y-0.5 group-hover:shadow-md">
        <span className={`absolute inset-y-0 left-0 w-1 ${config.barClass}`} aria-hidden="true" />

        <CardHeader className="gap-2 pt-5 pl-6">
          <div className="flex items-center justify-between gap-2">
            <CardDescription className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {noticia.fonte ?? 'Fonte desconhecida'}
            </CardDescription>
            <SentimentBadge sentimento={noticia.sentimento} size="sm" />
          </div>
          <CardTitle className="text-base leading-snug font-semibold text-balance text-foreground line-clamp-3">
            {noticia.titulo}
          </CardTitle>
        </CardHeader>

        <CardContent className="pb-5 pl-6">
          {noticia.corpo && (
            <p className="mb-3 line-clamp-2 text-sm text-muted-foreground">{noticia.corpo}</p>
          )}
          <time
            dateTime={dataReferencia.toISOString()}
            className="font-mono text-xs text-muted-foreground/80 tabular-nums"
          >
            {dataFormatada}
          </time>
        </CardContent>
      </Card>
    </Link>
  )
}