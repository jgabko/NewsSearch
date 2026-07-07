"""
Coleta pontual (não histórica) de notícias recentes sobre a empresa alvo,
enfileirando-as na fila local do NewsSearch para o worker processar.

Uso:
    python scripts/run_collect.py
    python scripts/run_collect.py --empresa "Go Coffee" --max-items 15
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from newssearch.collector.google_news_client import buscar_noticias  # noqa: E402
from newssearch.config import get_settings  # noqa: E402
from newssearch.logger import get_logger  # noqa: E402
from newssearch.pipeline.producer import enfileirar_noticias  # noqa: E402
from newssearch.queue.local_queue import LocalQueue  # noqa: E402

logger = get_logger(__name__)


def main() -> None:
    settings = get_settings()

    parser = argparse.ArgumentParser(description="Coleta pontual de notícias do NewsSearch")
    parser.add_argument("--empresa", type=str, default=settings.empresa_alvo)
    parser.add_argument("--max-items", type=int, default=settings.max_items_por_busca)
    args = parser.parse_args()

    logger.info('Buscando notícias recentes sobre "%s"...', args.empresa)
    noticias = buscar_noticias(empresa=args.empresa, max_items=args.max_items)

    fila = LocalQueue(settings.queue_db_path)
    total = enfileirar_noticias(fila, noticias)

    logger.info("%d notícias novas enfileiradas (de %d encontradas).", total, len(noticias))


if __name__ == "__main__":
    main()
