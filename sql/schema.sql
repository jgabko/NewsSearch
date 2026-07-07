-- NewsSearch — Schema Supabase (PostgreSQL)
-- Tabela principal de notícias coletadas e classificadas pela pipeline local.
-- Execute isso no SQL Editor do seu projeto Supabase.

create table if not exists newssearch_articles (
    id                          bigint generated always as identity primary key,
    titulo                      text not null,
    url                         text not null unique,
    fonte                       text,
    corpo                       text,
    empresa_alvo                text,
    data_publicacao             text,
    sentimento                  text not null check (sentimento in ('positivo', 'negativo', 'neutro')),
    sentimento_justificativa    text,
    data_coleta                 timestamptz not null default now()
);

create index if not exists idx_newssearch_articles_empresa    on newssearch_articles (empresa_alvo);
create index if not exists idx_newssearch_articles_sentimento on newssearch_articles (sentimento);
create index if not exists idx_newssearch_articles_data_coleta on newssearch_articles (data_coleta);

comment on table newssearch_articles is 'Notícias coletadas e classificadas por sentimento pela pipeline NewsSearch.';
