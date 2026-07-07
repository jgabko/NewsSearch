/**
 * Tipos do domínio NewsSearch — espelham a tabela `newssearch_articles`
 * criada pelo backend (ver sql/schema.sql no repositório do backend).
 */

export type Sentimento = 'positivo' | 'negativo' | 'neutro'

export interface Noticia {
  id: number
  titulo: string
  url: string
  fonte: string | null
  corpo: string | null
  empresa_alvo: string | null
  data_publicacao: string | null
  sentimento: Sentimento
  sentimento_justificativa: string | null
  data_coleta: string
}

export interface ResumoSentimento {
  total: number
  positivas: number
  negativas: number
  neutras: number
}