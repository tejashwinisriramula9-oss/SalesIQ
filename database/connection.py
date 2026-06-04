"""
SalesIQ Database Connection — SQLAlchemy 2.x + SQLite compatible.

Fixes vs original scaffolding:
  - SQLite does not support pool_size / max_overflow → removed
  - Uses check_same_thread=False for SQLite multi-thread safety
  - Proper FastAPI dependency (yields session, commits on success)
  - init_database() creates all tables on first run
"""

import logging
import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

logger = logging.getLogger(__name__)

# ── Database file lives in the project root ──────────────────────────────────
_DEFAULT_DB_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'salesiq.db')}",
)


def _make_engine(db_url: str = _DEFAULT_DB_URL) -> Engine:
    """
    Build a SQLAlchemy engine.
    SQLite-specific args (check_same_thread=False) are added automatically
    when the URL starts with sqlite:///.
    """
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        db_url,
        connect_args=connect_args,
        echo=False,           # set True to log every SQL statement
        pool_pre_ping=True,   # recycles stale connections
    )

    # Enable WAL mode on SQLite for better concurrent read performance
    if db_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _set_wal(dbapi_conn, _record):
            dbapi_conn.execute("PRAGMA journal_mode=WAL")
            dbapi_conn.execute("PRAGMA foreign_keys=ON")

    return engine


# Module-level singletons created once at import time
engine: Engine = _make_engine()
SessionLocal: sessionmaker = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ── Table initialisation ─────────────────────────────────────────────────────
def init_database() -> None:
    """
    Create all tables defined in models.py if they do not already exist.
    Safe to call on every server start (CREATE TABLE IF NOT EXISTS).
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialised (salesiq.db)")


# ── FastAPI dependency ────────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    Yield a SQLAlchemy Session for use as a FastAPI dependency.

        @app.get("/example")
        def handler(db: Session = Depends(get_db)):
            ...

    The session is committed on success and rolled back on any exception.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Convenience context manager (for use outside FastAPI) ────────────────────
@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for one-off database operations outside a request context.

        with get_session() as db:
            db.add(record)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Health helper ─────────────────────────────────────────────────────────────
def db_ping() -> bool:
    """Return True if the database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
