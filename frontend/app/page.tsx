import { createClient } from '@/lib/supabase/server'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { ExternalLink } from 'lucide-react'

interface Noticia {
  id: string
  titulo: string
  url: string
  fonte: string
  corpo: string | null
  data_coleta: string
}

export default async function Home() {
  const supabase = await createClient()

  const { data: noticias, error } = await supabase
    .from('noticias')
    .select('*')
    .order('data_coleta', { ascending: false })

  if (error) {
    console.error('Erro ao buscar notícias:', error)
  }

  const newsItems: Noticia[] = noticias || []

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <header className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                Tech Pulse
              </h1>
              <p className="text-slate-600 dark:text-slate-400 mt-1">
                Notícias de tecnologia em tempo real
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-slate-600 dark:text-slate-400">
                {newsItems.length} notícia{newsItems.length !== 1 ? 's' : ''}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-12">
        {newsItems.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-600 dark:text-slate-400 text-lg">
              Nenhuma notícia encontrada
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {newsItems.map((noticia) => {
              const dataFormatada = new Date(noticia.data_coleta)
              const tempoDecorrido = formatDistanceToNow(dataFormatada, {
                addSuffix: true,
                locale: ptBR,
              })

              return (
                <Card
                  key={noticia.id}
                  className="hover:shadow-lg transition-shadow duration-300 flex flex-col h-full border-slate-200 dark:border-slate-800 hover:border-blue-400 dark:hover:border-blue-600"
                >
                  <CardHeader>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <CardTitle className="text-lg line-clamp-2 text-slate-900 dark:text-white">
                          {noticia.titulo}
                        </CardTitle>
                      </div>
                    </div>
                    <CardDescription className="text-sm">
                      {noticia.fonte}
                    </CardDescription>
                  </CardHeader>

                  <CardContent className="flex-1 flex flex-col justify-between">
                    {/* Resumo do corpo — aparece só se existir */}
                    {noticia.corpo && (
                      <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-3 mb-3">
                        {noticia.corpo}
                      </p>
                    )}

                    <div className="text-xs text-slate-500 dark:text-slate-400 mb-4">
                      {tempoDecorrido}
                    </div>

                    <a
                      href={noticia.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-3 py-2 rounded-md bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium transition-colors w-fit"
                    >
                      Ler notícia
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </main>
  )
}