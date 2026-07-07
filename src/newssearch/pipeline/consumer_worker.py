"""
Worker (consumer) da pipeline NewsSearch.

Loop contínuo 100% local que substitui o antigo worker baseado em AWS SQS:

  1. Consome um job da fila local (SQLite).
  2. Faz o scraping do conteúdo completo do artigo.
  3. Classifica o sentimento da notícia via OpenRouter.
  4. Persiste o resultado completo no Supabase.
  5. Confirma (ack) o job na fila, ou marca falha para retry automático.
"""
from __future__ import annotations

import time

from newssearch.ai.sentiment_classifier import classificar_sentimento
from newssearch.config import get_settings
from newssearch.logger import get_logger
from newssearch.queue.local_queue import LocalQueue, QueueJob
from newssearch.scraper.article_scraper import scrape
from newssearch.storage.supabase_repository import salvar_noticia

logger = get_logger(__name__)


def processar_job(fila: LocalQueue, job: QueueJob) -> None:
    try:
        dados = scrape(job.payload)

        empresa = dados.get("empresa_alvo") or get_settings().empresa_alvo
        sentimento = classificar_sentimento(empresa=empresa, titulo=dados["titulo"], corpo=dados["corpo"])

        salvar_noticia(dados, sentimento)
        fila.ack(job.id)

        logger.info(
            "✓ Processado [%s] %s | %s",
            sentimento["sentimento"],
            dados["titulo"][:60],
            dados["url"][:60],
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("✗ Erro ao processar job %s: %s", job.id, exc)
        fila.fail(job.id, str(exc))


def run_worker(poll_interval: float | None = None) -> None:
    settings = get_settings()
    poll_interval = poll_interval or settings.worker_poll_interval

    fila = LocalQueue(settings.queue_db_path)
    recuperados = fila.requeue_stuck_jobs()
    if recuperados:
        logger.info("Recuperados %d jobs presos de uma execução anterior.", recuperados)

    logger.info("NewsSearch worker iniciado. Aguardando jobs na fila local...")

    try:
        while True:
            job = fila.dequeue()
            if job is None:
                time.sleep(poll_interval)
                continue
            processar_job(fila, job)
    except KeyboardInterrupt:
        logger.info("Worker encerrado pelo usuário (Ctrl+C).")


if __name__ == "__main__":
    run_worker()
