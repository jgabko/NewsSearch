"""
Logger centralizado do NewsSearch.

Todas as mensagens de log do sistema saem prefixadas como "newssearch.<módulo>",
facilitando filtrar/grepar logs de toda a pipeline local.
"""
from __future__ import annotations

import logging
import os


def get_logger(name: str) -> logging.Logger:
    logger_name = f"newssearch.{name.replace('newssearch.', '')}"
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(os.environ.get("NEWSSEARCH_LOG_LEVEL", "INFO"))
        logger.propagate = False

    return logger
