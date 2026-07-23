# lambdas/collector_handler.py
import os
from supabase import create_client
from newssearch.collector.google_news_client import GoogleNewsSource
from newssearch.storage.supabase_queue_repository import SupabaseQueueRepository

def _montar_dependencias():
    """Composition root: único lugar onde implementações concretas são escolhidas (DIP)."""
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    return GoogleNewsSource(), SupabaseQueueRepository(client)

def handler(event, context):
    empresa_alvo = os.environ["EMPRESA_ALVO"]
    max_itens = int(os.environ.get("MAX_ITENS_COLETA", "15"))

    fonte, fila = _montar_dependencias()
    noticias = fonte.buscar(empresa_alvo, max_itens)

    for noticia in noticias:
        fila.enfileirar(noticia, empresa_alvo)

    return {"coletadas": len(noticias)}