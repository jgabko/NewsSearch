# lambdas/persistence_handler.py
import os
from supabase import create_client
from newssearch.storage.supabase_queue_repository import SupabaseQueueRepository
from newssearch.storage.supabase_article_repository import SupabaseArticleRepository

def _montar_dependencias():
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    return SupabaseQueueRepository(client), SupabaseArticleRepository(client)

def handler(event, context):
    lote_tamanho = int(os.environ.get("PERSISTENCE_LOTE", "10"))
    fila, artigos = _montar_dependencias()

    itens = fila.buscar_lote_por_status("pending_persistence", lote_tamanho)
    processados, falhas = 0, 0

    for item in itens:
        try:
            artigos.salvar(item["id"], item)
            fila.atualizar_status(item["id"], "done")
            processados += 1
        except Exception as erro:
            fila.registrar_falha(item["id"], str(erro))
            falhas += 1

    return {"processados": processados, "falhas": falhas}