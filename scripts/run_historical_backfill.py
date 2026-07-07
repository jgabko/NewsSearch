"""
Entrypoint da Carga Histórica do NewsSearch.

Regra de negócio: coleta dados retroativos de N anos atrás (padrão: 2) até
o momento atual. Consulte `src/newssearch/collector/historical_loader.py`
para a implementação e `README.md` para exemplos de uso.

Uso:
    python scripts/run_historical_backfill.py
    python scripts/run_historical_backfill.py --anos 3
    python scripts/run_historical_backfill.py --data-inicio 2023-01-01 --data-fim 2024-01-01
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from newssearch.collector.historical_loader import main  # noqa: E402

if __name__ == "__main__":
    main()
