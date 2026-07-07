
// Configuração do Supabase — Projeto NewsSearch
// As credenciais SEMPRE vêm de variáveis de ambiente (.env.local), nunca
// hardcoded no código-fonte. A anon key é pública por design (protegida por
// Row Level Security no Supabase), mas ainda assim não deve ficar commitada.

function obrigatoria(nome: string, valor: string | undefined): string {
  if (!valor) {
    throw new Error(
      `Variável de ambiente obrigatória ausente: ${nome}. Verifique seu .env.local (veja .env.example).`,
    )
  }
  return valor
}

export const SUPABASE_CONFIG = {
  url: obrigatoria('NEXT_PUBLIC_SUPABASE_URL', process.env.NEXT_PUBLIC_SUPABASE_URL),
  anonKey: obrigatoria(
    'NEXT_PUBLIC_SUPABASE_ANON_KEY',
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  ),
}