"""
Worker (consumer) da pipeline NewsSearch.

Loop contínuo 100% local que substitui o antigo worker baseado em AWS SQS:

  1. Consome um job da fila local (SQLite).
  2. Faz o scraping do conteúdo completo do artigo.
  3. Verifica se o artigo REALMENTE menciona a empresa (título + corpo
     completo) — filtro rigoroso que evita gastar tokens do OpenRouter
     classificando notícias que só casaram por uma palavra solta do nome
     da empresa (ex: "coffee" sozinho para "Go Coffee"). Se não menciona,
     descarta o job sem chamar a IA e sem salvar no Supabase.
  4. Classifica o sentimento da notícia via OpenRouter.
  5. Persiste o resultado completo no Supabase.
  6. Confirma (ack) o job na fila, ou marca falha para retry automático.
"""
from __future__ import annotations

import time

from newssearch.ai.sentiment_classifier import classificar_sentimento
from newssearch.config import get_settings
from newssearch.logger import get_logger
from newssearch.matching.empresa_matcher import mencao_real
from newssearch.queue.local_queue import LocalQueue, QueueJob
from newssearch.scraper.article_scraper import scrape
from newssearch.storage.supabase_repository import salvar_noticia

logger = get_logger(__name__)


def processar_job(fila: LocalQueue, job: QueueJob) -> None:
    try:
        dados = scrape(job.payload)
        empresa = dados.get("empresa_alvo") or get_settings().empresa_alvo

        texto_completo = f"{dados.get('titulo', '')}\n{dados.get('corpo', '')}"
        if not mencao_real(texto_completo, empresa):
            fila.ack(job.id)
            logger.info(
                '✗ Descartado (sem menção real a "%s" no artigo): %s | %s',
                empresa,
                dados["titulo"][:60],
                dados["url"][:60],
            )
            return

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


def run_worker(
    poll_interval: float | None = None,
    drain: bool = False,
    max_runtime_seconds: float | None = None,
) -> None:
    """
    Executa o worker.

    Args:
        poll_interval: intervalo (segundos) entre tentativas quando a fila
            está vazia, no modo contínuo. Ignorado no modo drain.
        drain: se True, processa jobs até a fila esvaziar e ENCERRA (em vez
            de ficar em loop infinito). Modo usado em execuções via
            GitHub Actions / CI, onde não há um processo de longa duração.
        max_runtime_seconds: teto de segurança de tempo total de execução
            (em qualquer modo). Útil em CI para nunca estourar o limite do
            job, mesmo que a fila tenha muitos itens.
    """
    settings = get_settings()
    poll_interval = poll_interval or settings.worker_poll_interval

    fila = LocalQueue(settings.queue_db_path)
    recuperados = fila.requeue_stuck_jobs()
    if recuperados:
        logger.info("Recuperados %d jobs presos de uma execução anterior.", recuperados)

    modo = "drenagem (encerra ao esvaziar a fila)" if drain else "contínuo (loop infinito)"
    logger.info("NewsSearch worker iniciado em modo %s...", modo)

    inicio = time.monotonic()
    processados = 0

    try:
        while True:
            if max_runtime_seconds is not None and (time.monotonic() - inicio) > max_runtime_seconds:
                logger.info(
                    "Tempo máximo de execução atingido (%.0fs). %d job(s) processado(s). Encerrando.",
                    max_runtime_seconds,
                    processados,
                )
                break

            job = fila.dequeue()
            if job is None:
                if drain:
                    logger.info(
                        "Fila vazia. %d job(s) processado(s). Encerrando (modo drenagem).",
                        processados,
                    )
                    break
                time.sleep(poll_interval)
                continue

            processar_job(fila, job)
            processados += 1
    except KeyboardInterrupt:
        logger.info("Worker encerrado pelo usuário (Ctrl+C).")

if __name__ == "__main__":
    run_worker()