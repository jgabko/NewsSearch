"""
Módulo de Carga Histórica do NewsSearch.

Regra de negócio: coleta notícias retroativas de "N anos atrás até hoje"
(padrão: 2 anos). O intervalo NUNCA é hardcoded — pode ser configurado por:

  1. Variáveis de ambiente no .env: HISTORICO_ANOS, ou
  2. Argumentos de linha de comando (têm prioridade sobre o .env):
     --anos, --data-inicio, --data-fim

Uso (via scripts/run_historical_backfill.py):
    python scripts/run_historical_backfill.py
    python scripts/run_historical_backfill.py --anos 3
    python scripts/run_historical_backfill.py --data-inicio 2023-01-01 --data-fim 2024-01-01
    python scripts/run_historical_backfill.py --empresa "Go Coffee"
"""
from __future__ import annotations

import argparse
import time
from datetime import date

from dateutil.relativedelta import relativedelta

from newssearch.collector.google_news_client import buscar_noticias
from newssearch.config import get_settings
from newssearch.logger import get_logger
from newssearch.pipeline.producer import enfileirar_noticias
from newssearch.queue.local_queue import LocalQueue

logger = get_logger(__name__)


def _gerar_janelas_mensais(data_inicio: date, data_fim: date):
    """
    Gera janelas mensais [inicio, fim) entre data_inicio e data_fim.

    O Google News RSS retorna poucos itens por consulta; buscar mês a mês
    (em vez de um único range de 2 anos de uma vez) aumenta muito a
    cobertura de notícias coletadas ao longo do período.
    """
    cursor = data_inicio
    while cursor < data_fim:
        proxima = min(cursor + relativedelta(months=1), data_fim)
        yield cursor, proxima
        cursor = proxima


def parse_args() -> argparse.Namespace:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Carga histórica de notícias do NewsSearch")
    parser.add_argument(
        "--anos",
        type=int,
        default=None,
        help="Anos retroativos a partir de hoje (padrão: HISTORICO_ANOS do .env, ou 2)",
    )
    parser.add_argument(
        "--data-inicio", type=str, default=None, help="Data inicial YYYY-MM-DD (sobrepõe --anos)"
    )
    parser.add_argument(
        "--data-fim", type=str, default=None, help="Data final YYYY-MM-DD (padrão: hoje)"
    )
    parser.add_argument(
        "--empresa", type=str, default=settings.empresa_alvo, help="Empresa/termo a pesquisar"
    )
    parser.add_argument(
        "--max-por-janela",
        type=int,
        default=settings.max_items_por_busca,
        help="Máximo de notícias buscadas por janela mensal",
    )
    parser.add_argument(
        "--intervalo-segundos",
        type=float,
        default=1.5,
        help="Pausa entre requisições, para não sobrecarregar o Google News",
    )
    return parser.parse_args()


def resolver_intervalo(args: argparse.Namespace) -> tuple[date, date]:
    """Resolve o range de datas: CLI > .env > padrão (2 anos)."""
    settings = get_settings()

    data_fim = date.fromisoformat(args.data_fim) if args.data_fim else date.today()

    if args.data_inicio:
        data_inicio = date.fromisoformat(args.data_inicio)
    else:
        anos = args.anos if args.anos is not None else settings.historico_anos
        data_inicio = data_fim - relativedelta(years=anos)

    return data_inicio, data_fim


def main() -> None:
    args = parse_args()
    data_inicio, data_fim = resolver_intervalo(args)

    logger.info(
        "Iniciando carga histórica do NewsSearch | empresa=%s | período=%s a %s",
        args.empresa,
        data_inicio,
        data_fim,
    )

    fila = LocalQueue(get_settings().queue_db_path)
    total_enfileirado = 0

    for inicio_janela, fim_janela in _gerar_janelas_mensais(data_inicio, data_fim):
        logger.info("Buscando janela %s -> %s", inicio_janela, fim_janela)
        try:
            noticias = buscar_noticias(
                empresa=args.empresa,
                max_items=args.max_por_janela,
                data_inicio=inicio_janela.isoformat(),
                data_fim=fim_janela.isoformat(),
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Falha ao buscar janela %s-%s: %s", inicio_janela, fim_janela, exc)
            continue

        total_enfileirado += enfileirar_noticias(fila, noticias)
        time.sleep(args.intervalo_segundos)

    logger.info("Carga histórica concluída. Total de itens novos enfileirados: %d", total_enfileirado)


if __name__ == "__main__":
    main()
