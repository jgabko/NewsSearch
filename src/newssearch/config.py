"""
Configuração centralizada do NewsSearch.

Todas as variáveis vêm do ambiente (.env), nunca hardcoded — inclusive o
intervalo de tempo usado na carga histórica (requisito de negócio: o range
de datas tem que ser configurável, nunca fixo no código).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Supabase
    supabase_url: str
    supabase_key: str

    # OpenRouter (IA de classificação de sentimento)
    openrouter_api_key: str
    openrouter_model: str

    # Domínio / negócio
    empresa_alvo: str
    historico_anos: int
    max_items_por_busca: int

    # Fila local (substitui o AWS SQS)
    queue_db_path: str
    worker_poll_interval: float

    # Observabilidade
    log_level: str


def _obrigatoria(nome: str) -> str:
    valor = os.environ.get(nome)
    if not valor:
        raise RuntimeError(
            f"Variável de ambiente obrigatória ausente: {nome}. "
            f"Verifique seu arquivo .env (veja .env.example)."
        )
    return valor


@lru_cache
def get_settings() -> Settings:
    """Carrega e cacheia as configurações do NewsSearch a partir do ambiente."""
    return Settings(
        supabase_url=_obrigatoria("SUPABASE_URL"),
        supabase_key=_obrigatoria("SUPABASE_KEY"),
        openrouter_api_key=_obrigatoria("OPENROUTER_API_KEY"),
        openrouter_model=os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        empresa_alvo=os.environ.get("EMPRESA_ALVO", "Go Coffee"),
        historico_anos=int(os.environ.get("HISTORICO_ANOS", "2")),
        max_items_por_busca=int(os.environ.get("NEWSSEARCH_MAX_ITEMS_POR_BUSCA", "20")),
        queue_db_path=os.environ.get("NEWSSEARCH_QUEUE_DB_PATH", "data/newssearch_queue.db"),
        worker_poll_interval=float(os.environ.get("NEWSSEARCH_WORKER_POLL_INTERVAL", "2")),
        log_level=os.environ.get("NEWSSEARCH_LOG_LEVEL", "INFO"),
    )
