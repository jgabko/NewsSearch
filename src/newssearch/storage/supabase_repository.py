"""
Persistência das notícias classificadas no Supabase.
"""
from __future__ import annotations

import datetime

from supabase import Client, create_client

from newssearch.config import get_settings

_TABLE_NAME = "newssearch_articles"

_client: Client | None = None


def get_supabase_client() -> Client:
    global _client
    if _client is None:
        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.supabase_key)
    return _client


def salvar_noticia(dados: dict, sentimento: dict) -> None:
    """
    Salva o payload completo da notícia (título, link, data, conteúdo) junto
    com o sentimento retornado pela IA no Supabase.

    Faz upsert por `url` para manter idempotência — reprocessar a mesma
    notícia (ex: reexecutar a carga histórica) não gera duplicatas.
    """
    agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
    client = get_supabase_client()

    client.table(_TABLE_NAME).upsert(
        {
            "titulo": dados["titulo"],
            "url": dados["url"],
            "fonte": dados["fonte"],
            "corpo": dados.get("corpo", ""),
            "empresa_alvo": dados.get("empresa_alvo"),
            "data_publicacao": dados.get("data_publicacao"),
            "sentimento": sentimento["sentimento"],
            "sentimento_justificativa": sentimento.get("justificativa", ""),
            "data_coleta": agora,
        },
        on_conflict="url",
    ).execute()


def listar_noticias(empresa: str | None = None, page_size: int = 1000) -> list[dict]:
    """
    Retorna todas as notícias da tabela (paginando em blocos de `page_size`
    para não estourar o limite de linhas por request do Supabase).

    Se `empresa` for informado, filtra por `empresa_alvo` (igualdade exata).
    Traz `corpo` também, pois o cleaner agora verifica a menção real no
    conteúdo do artigo (título + corpo), e não só no texto da justificativa
    que a IA escreveu.
    """
    client = get_supabase_client()
    colunas = "id, titulo, url, corpo, empresa_alvo, sentimento, sentimento_justificativa"

    todas: list[dict] = []
    inicio = 0
    while True:
        query = client.table(_TABLE_NAME).select(colunas)
        if empresa:
            query = query.eq("empresa_alvo", empresa)
        resposta = query.range(inicio, inicio + page_size - 1).execute()
        pagina = resposta.data or []
        todas.extend(pagina)

        if len(pagina) < page_size:
            break
        inicio += page_size

    return todas


def deletar_noticias_por_id(ids: list[int]) -> int:
    """
    Apaga da tabela as notícias cujo `id` estiver em `ids`.

    Faz em lotes de 500 ids por requisição (limite prático de filtro `in_`
    do PostgREST) e retorna o total de ids solicitados para exclusão.
    """
    if not ids:
        return 0

    client = get_supabase_client()
    lote = 500
    for i in range(0, len(ids), lote):
        pedaco = ids[i : i + lote]
        client.table(_TABLE_NAME).delete().in_("id", pedaco).execute()

    return len(ids)