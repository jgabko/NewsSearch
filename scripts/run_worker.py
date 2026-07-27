"""
Entrypoint do worker (consumer) local do NewsSearch.

Roda em loop contínuo: consome jobs da fila local -> scraping -> classificação
de sentimento (OpenRouter) -> persistência (Supabase).

Uso:
    python scripts/run_worker.py
    python scripts/run_worker.py --drain --max-runtime-seconds 18000
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from newssearch.pipeline.consumer_worker import run_worker  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Worker (consumer) do NewsSearch.")
    parser.add_argument(
        "--drain",
        action="store_true",
        help="Processa a fila até esvaziar e encerra (uso em CI/GitHub Actions). "
        "Sem essa flag, roda em loop contínuo (uso local).",
    )
    parser.add_argument(
        "--max-runtime-seconds",
        type=float,
        default=None,
        help="Teto de segurança de tempo total de execução, em segundos.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_worker(drain=args.drain, max_runtime_seconds=args.max_runtime_seconds)