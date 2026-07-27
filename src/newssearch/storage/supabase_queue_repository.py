# src/newssearch/storage/supabase_queue_repository.py
from supabase import Client
from newssearch.interfaces import IQueueRepository, NoticiaBruta

class SupabaseQueueRepository(IQueueRepository):
    def __init__(self, client: Client):
        self._client = client

    def enfileirar(self, noticia: NoticiaBruta, empresa_alvo: str) -> None:
        self._client.table("news_queue").upsert({
            "empresa_alvo": empresa_alvo,
            "titulo": noticia.titulo,
            "url": noticia.url,
            "fonte": noticia.fonte,
            "data_publicacao": noticia.data_publicacao,
            "status": "pending_scraping",
        }, on_conflict="url").execute()  # on_conflict evita duplicar (url é unique)

    # buscar_lote_por_status, atualizar_status, registrar_falha:
    # não usados por essa Lambda, mas precisam existir pra satisfazer o contrato
    # (implementados de fato na etapa 4, reaproveitando esta mesma classe)