import { isValid } from 'date-fns'

/**
 * Resolve a data de exibição de uma notícia com segurança.
 *
 * `data_publicacao` vem de uma extração best-effort de meta tags do site de
 * origem (ver scraper do backend) e pode vir ausente, vazia, ou em um
 * formato que o `Date` nativo não consegue interpretar. Nesses casos,
 * caímos para `data_coleta`, que é sempre um ISO 8601 válido gerado pelo
 * próprio backend — nunca deixamos `new Date(...)` explodir com "Invalid
 * time value" na tela do usuário.
 */
export function resolverDataExibicao(
  dataPublicacao: string | null | undefined,
  dataColeta: string,
): Date {
  if (dataPublicacao) {
    const data = new Date(dataPublicacao)
    if (isValid(data)) return data
  }
  return new Date(dataColeta)
}