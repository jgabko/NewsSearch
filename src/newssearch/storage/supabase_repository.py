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
