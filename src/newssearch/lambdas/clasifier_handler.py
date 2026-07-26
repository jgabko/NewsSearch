# lambdas/classifier_handler.py
import os
from supabase import create_client
from newssearch.ai.openrouter_classifier import OpenRouterClassifier
from newssearch.storage.supabase_queue_repository import SupabaseQueueRepository

def _montar_dependencias():
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    classificador = OpenRouterClassifier(
        api_key=os.environ["OPENROUTER_API_KEY"],
        modelo=os.environ["OPENROUTER_MODEL"],
    )
    return classificador, SupabaseQueueRepository(client)

def handler(event, context):
    lote_tamanho = int(os.environ.get("CLASSIFIER_LOTE", "10"))
    classificador, fila = _montar_dependencias()

    itens = fila.buscar_lote_por_status("pending_classification", lote_tamanho)
    processados, falhas = 0, 0

    for item in itens:
        try:
            resultado = classificador.classificar(
                item["conteudo_scraped"], item["empresa_alvo"]
            )
            fila.atualizar_status(
                item["id"], "pending_persistence",
                sentimento=resultado.sentimento,
                sentimento_score=resultado.score,
            )
            processados += 1
        except Exception as erro:
            fila.registrar_falha(item["id"], str(erro))
            falhas += 1

    return {"processados": processados, "falhas": falhas}