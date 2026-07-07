"""
Entrypoint do worker (consumer) local do NewsSearch.

Roda em loop contínuo: consome jobs da fila local -> scraping -> classificação
de sentimento (OpenRouter) -> persistência (Supabase).

Uso:
    python scripts/run_worker.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from newssearch.pipeline.consumer_worker import run_worker  # noqa: E402

if __name__ == "__main__":
    run_worker()
