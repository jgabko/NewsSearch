# lambdas/scraper_handler.py
import os
from supabase import create_client
from newssearch.scraper.http_article_scraper import HttpArticleScraper
from newssearch.storage.supabase_queue_repository import SupabaseQueueRepository

def _montar_dependencias():
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    return HttpArticleScraper(), SupabaseQueueRepository(client)

def handler(event, context):
    lote_tamanho = int(os.environ.get("SCRAPER_LOTE", "10"))
    scraper, fila = _montar_dependencias()

    itens = fila.buscar_lote_por_status("pending_scraping", lote_tamanho)
    processados, falhas = 0, 0

    for item in itens:
        try:
            conteudo = scraper.extrair_conteudo(item["url"])
            fila.atualizar_status(
                item["id"], "pending_classification", conteudo_scraped=conteudo
            )
            processados += 1
        except Exception as erro:
            fila.registrar_falha(item["id"], str(erro))
            falhas += 1

    return {"processados": processados, "falhas": falhas}