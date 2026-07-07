"""
Producer da pipeline NewsSearch.

Transforma itens coletados (do Google News) em jobs na fila local,
substituindo o antigo `enviar_para_fila` baseado em AWS SQS.
"""
from __future__ import annotations

from newssearch.logger import get_logger
from newssearch.queue.local_queue import LocalQueue

logger = get_logger(__name__)


def enfileirar_noticias(fila: LocalQueue, noticias: list[dict]) -> int:
    """
    Enfileira uma lista de notícias, ignorando duplicatas pela URL.
    Retorna quantas notícias eram novas (efetivamente enfileiradas).
    """
    novas = 0
    for noticia in noticias:
        if not noticia.get("url"):
            continue
        job_id = fila.enqueue(payload=noticia, dedup_key=noticia["url"])
        if job_id:
            novas += 1
            logger.info("Enfileirado: %s", noticia["url"][:80])
        else:
            logger.debug("Já estava na fila (ignorado): %s", noticia["url"][:80])
    return novas
