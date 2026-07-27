# src/newssearch/storage/supabase_article_repository.py
from supabase import Client
from newssearch.interfaces import IArticleRepository

class SupabaseArticleRepository(IArticleRepository):
    """Implementação concreta de IArticleRepository — grava na tabela final de artigos."""

    def __init__(self, client: Client):
        self._client = client

    def salvar(self, item_id: int, dados: dict) -> None:
        self._client.table("newssearch_articles").insert({
            "empresa_alvo": dados["empresa_alvo"],
            "titulo": dados["titulo"],
            "url": dados["url"],
            "fonte": dados["fonte"],
            "data_publicacao": dados["data_publicacao"],
            "conteudo": dados["conteudo_scraped"],
            "sentimento": dados["sentimento"],
            "sentimento_score": dados["sentimento_score"],
        }).execute()