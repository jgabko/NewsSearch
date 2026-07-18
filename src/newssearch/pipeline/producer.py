"""
Producer da pipeline NewsSearch.

Transforma itens coletados (do Google News) em jobs na fila local,
substituindo o antigo `enviar_para_fila` baseado em AWS SQS.

Antes de enfileirar, aplica um filtro LEVE de menção real à empresa (usando
só o título/snippet do RSS, que é tudo que se tem nesse ponto — o corpo
completo só existe depois do scraping no worker). Isso evita gastar uma
raspagem + chamada de IA inteira em notícias que o Google News trouxe só
por casar uma palavra solta do nome da empresa (ex: "coffee" sozinho para
"Go Coffee"). O filtro rigoroso (com o corpo completo) roda depois, no
worker, antes da classificação de sentimento.
"""
from __future__ import annotations

from newssearch.logger import get_logger
from newssearch.matching.empresa_matcher import mencao_real
from newssearch.queue.local_queue import LocalQueue

logger = get_logger(__name__)


def enfileirar_noticias(fila: LocalQueue, noticias: list[dict]) -> int:
    """
    Enfileira uma lista de notícias, ignorando duplicatas pela URL e
    descartando de cara as que não mencionam a empresa pelo nome completo
    no título (filtro leve — o filtro definitivo é feito no worker, com o
    corpo raspado).
    Retorna quantas notícias eram novas (efetivamente enfileiradas).
    """
    novas = 0
    for noticia in noticias:
        if not noticia.get("url"):
            continue

        empresa = noticia.get("empresa_alvo")
        titulo = noticia.get("titulo", "")
        if empresa and not mencao_real(titulo, empresa):
            logger.info(
                'Descartado (título não menciona "%s"): %s', empresa, titulo[:80]
            )
            continue

        job_id = fila.enqueue(payload=noticia, dedup_key=noticia["url"])
        if job_id:
            novas += 1
            logger.info("Enfileirado: %s", noticia["url"][:80])
        else:
            logger.debug("Já estava na fila (ignorado): %s", noticia["url"][:80])
    return novas