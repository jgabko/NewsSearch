"""
Fila local persistente do NewsSearch, baseada em SQLite.

SUBSTITUI COMPLETAMENTE o AWS SQS (sem boto3, sem credenciais AWS, sem custo
de cloud). Funciona com um único arquivo em disco, mantendo a pipeline 100%
local e portátil — basta rodar `python scripts/run_worker.py`.

Características:
- Persistente: sobrevive a reinícios do processo (diferente de uma fila em
  memória pura), o que é importante para a carga histórica, que pode
  enfileirar milhares de itens ao longo de vários minutos.
- Segura para múltiplos processos: producer (coleta) e worker (consumo)
  podem rodar em processos separados, graças ao modo WAL do SQLite e a
  transações atômicas no dequeue.
- Idempotente: o mesmo item (mesma URL) nunca é enfileirado duas vezes.
- Com retry: falhas de processamento voltam para a fila até um limite de
  tentativas, e depois vão para status 'error' (equivalente a uma DLQ).
"""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_DONE = "done"
STATUS_ERROR = "error"


@dataclass
class QueueJob:
    id: str
    payload: dict
    attempts: int


class LocalQueue:
    """Fila local (SQLite) que substitui o AWS SQS na pipeline do NewsSearch."""

    def __init__(self, db_path: str = "data/newssearch_queue.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS newssearch_jobs (
                    id TEXT PRIMARY KEY,
                    dedup_key TEXT UNIQUE,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_newssearch_jobs_status "
                "ON newssearch_jobs(status)"
            )

    def enqueue(self, payload: dict, dedup_key: Optional[str] = None) -> Optional[str]:
        """
        Adiciona um item à fila (equivalente ao `send_message` do SQS).

        Se `dedup_key` já existir (ex: a URL da notícia), o item é ignorado
        silenciosamente para evitar duplicatas — importante porque tanto a
        coleta diária quanto a carga histórica podem encontrar a mesma notícia.

        Retorna o id do job criado, ou None se era duplicado.
        """
        job_id = str(uuid.uuid4())
        now = time.time()
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO newssearch_jobs
                        (id, dedup_key, payload, status, attempts, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 0, ?, ?)
                    """,
                    (
                        job_id,
                        dedup_key,
                        json.dumps(payload, ensure_ascii=False),
                        STATUS_PENDING,
                        now,
                        now,
                    ),
                )
            return job_id
        except sqlite3.IntegrityError:
            # dedup_key já existe -> item já está (ou já esteve) na fila
            return None

    def dequeue(self) -> Optional[QueueJob]:
        """
        Reserva atomicamente o próximo job pendente e marca como 'processing'
        (equivalente ao `receive_message` do SQS, sem visibility timeout
        porque a reserva é imediata e exclusiva via transação SQLite).

        Retorna None se a fila estiver vazia.
        """
        with self._connect() as conn:
            conn.isolation_level = None
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """
                SELECT id, payload, attempts FROM newssearch_jobs
                WHERE status = ?
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (STATUS_PENDING,),
            ).fetchone()

            if row is None:
                conn.execute("COMMIT")
                return None

            job_id, payload_raw, attempts = row
            conn.execute(
                "UPDATE newssearch_jobs SET status = ?, updated_at = ? WHERE id = ?",
                (STATUS_PROCESSING, time.time(), job_id),
            )
            conn.execute("COMMIT")

        return QueueJob(id=job_id, payload=json.loads(payload_raw), attempts=attempts)

    def ack(self, job_id: str) -> None:
        """Confirma o processamento com sucesso (equivalente ao `delete_message` do SQS)."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE newssearch_jobs SET status = ?, updated_at = ? WHERE id = ?",
                (STATUS_DONE, time.time(), job_id),
            )

    def fail(self, job_id: str, error: str, max_attempts: int = 3) -> None:
        """
        Marca falha no processamento. Se ainda não atingiu `max_attempts`,
        o job volta para 'pending' (retry automático). Caso contrário, vai
        para 'error' (equivalente a uma Dead Letter Queue).
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT attempts FROM newssearch_jobs WHERE id = ?", (job_id,)
            ).fetchone()
            attempts = (row[0] if row else 0) + 1
            novo_status = STATUS_PENDING if attempts < max_attempts else STATUS_ERROR
            conn.execute(
                """
                UPDATE newssearch_jobs
                SET status = ?, attempts = ?, error_message = ?, updated_at = ?
                WHERE id = ?
                """,
                (novo_status, attempts, error[:2000], time.time(), job_id),
            )

    def pending_count(self) -> int:
        """Quantidade de jobs aguardando processamento."""
        with self._connect() as conn:
            (count,) = conn.execute(
                "SELECT COUNT(*) FROM newssearch_jobs WHERE status = ?", (STATUS_PENDING,)
            ).fetchone()
        return count

    def requeue_stuck_jobs(self, older_than_seconds: int = 600) -> int:
        """
        Recoloca em 'pending' jobs presos em 'processing' há muito tempo
        (ex: o worker foi encerrado no meio do processamento). Chamado
        automaticamente ao iniciar o worker, para autorrecuperação.
        """
        cutoff = time.time() - older_than_seconds
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE newssearch_jobs SET status = ? WHERE status = ? AND updated_at < ?",
                (STATUS_PENDING, STATUS_PROCESSING, cutoff),
            )
            return cur.rowcount
