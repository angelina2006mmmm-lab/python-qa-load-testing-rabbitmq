"""SQLite test storage shared between the API and its worker."""

from contextlib import contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
from typing import Iterator


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    db_path = Path(os.getenv("SQLITE_PATH", "/tmp/premium-jobs.db"))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with connection() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                message TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


def create_job(job_id: str, message: str) -> None:
    timestamp = _now()
    with connection() as conn:
        conn.execute(
            "INSERT INTO jobs (id, message, status, result, created_at, updated_at) "
            "VALUES (?, ?, 'queued', NULL, ?, ?)",
            (job_id, message, timestamp, timestamp),
        )


def get_job(job_id: str) -> dict | None:
    with connection() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return dict(row) if row is not None else None


def update_job(job_id: str, status: str, result: str | None = None) -> None:
    if status not in {"queued", "processing", "done", "failed"}:
        raise ValueError("Unsupported job status")
    with connection() as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, result = ?, updated_at = ? WHERE id = ?",
            (status, result, _now(), job_id),
        )
