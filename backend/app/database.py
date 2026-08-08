"""Database setup and session creation for SQLAlchemy."""

from __future__ import annotations

import logging
import os
from pathlib import Path
import time
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL = settings.DATABASE_URL

# Ensure parent directory exists for SQLite database files
connect_args: dict[str, Any] = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 10}
    raw_path = DATABASE_URL.replace("sqlite:///", "", 1)
    if raw_path and raw_path != ":memory:":
        try:
            db_file_path = Path(raw_path).resolve()
            db_file_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            logger.warning(f"Could not create SQLite parent directory for {raw_path}: {err}")

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SQLITE_LOCK_RETRY_METRICS = {
    "commit_retries": 0,
    "flush_retries": 0,
}


def _is_sqlite_lock_error(exc: BaseException) -> bool:
    return "database is locked" in str(exc).lower()


class RetrySQLiteSession(SQLAlchemySession):
    """Session with bounded retry/backoff for SQLite write-lock contention."""

    max_lock_retries = 3
    base_backoff_seconds = 0.12

    def _run_with_sqlite_lock_retry(self, operation: str, fn: Any) -> Any:
        for attempt in range(self.max_lock_retries + 1):
            try:
                return fn()
            except OperationalError as exc:
                if not _is_sqlite_lock_error(exc) or attempt >= self.max_lock_retries:
                    raise

                SQLITE_LOCK_RETRY_METRICS[f"{operation}_retries"] += 1
                delay = self.base_backoff_seconds * (2 ** attempt)
                logger.warning(
                    "SQLite write lock during %s; retrying in %.2fs "
                    "(attempt %s/%s, total_%s_retries=%s)",
                    operation,
                    delay,
                    attempt + 1,
                    self.max_lock_retries,
                    operation,
                    SQLITE_LOCK_RETRY_METRICS[f"{operation}_retries"],
                )
                time.sleep(delay)

        return fn()

    def flush(self, objects: Any = None) -> None:
        return self._run_with_sqlite_lock_retry(
            "flush",
            lambda: super(RetrySQLiteSession, self).flush(objects),
        )

    def commit(self) -> None:
        return self._run_with_sqlite_lock_retry(
            "commit",
            lambda: super(RetrySQLiteSession, self).commit(),
        )


@event.listens_for(engine, "connect")
def _set_sqlite_busy_timeout(dbapi_connection: Any, connection_record: Any) -> None:
    """Ask SQLite to wait briefly before surfacing lock contention."""
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA busy_timeout = 10000")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=RetrySQLiteSession)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database session generation."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
