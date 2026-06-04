"""
SalesIQ Data Store — dual-layer persistence.

Architecture
────────────
  ┌──────────────────────────────────────────────┐
  │               SalesDataStore                 │
  │                                              │
  │  RAM cache (pd.DataFrame)  ◄──────────────── │◄── write
  │       fast reads                             │
  │                                              │
  │  SQLite via db_ops  ◄──────────────────────  │◄── write
  │       survives restart                       │
  └──────────────────────────────────────────────┘

On save()   → writes to BOTH RAM and SQLite
On load()   → returns RAM cache if populated,
              otherwise reloads from SQLite
On restart  → RAM is empty; first load() hydrates
              the cache from SQLite automatically
"""

import logging
import threading
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class SalesDataStore:
    """
    Thread-safe, dual-layer data store.

    Public API (unchanged from original in-memory version):
        store.save(df)          → persist
        store.load()            → retrieve as DataFrame | None
        store.clear()           → wipe RAM + DB
        store.has_data()        → bool
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cache: Optional[pd.DataFrame] = None
        self._db_available: bool = True   # flipped to False if DB init fails

        # Attempt to connect to the database at construction time.
        # If the DB isn't ready yet (first import before init_database()),
        # we log the warning and fall back to pure RAM mode.
        try:
            from database.connection import init_database
            init_database()
        except Exception as exc:
            logger.warning(
                "SalesDataStore: DB initialisation skipped at import (%s). "
                "Will retry on first save().",
                exc,
            )
            self._db_available = False

    # ── Write ─────────────────────────────────────────────────────────────────

    def save(self, df: pd.DataFrame) -> None:
        """
        Persist df to both RAM cache and SQLite.
        Replaces the entire dataset (re-upload clears old data first).
        """
        with self._lock:
            # 1. Update RAM cache immediately
            self._cache = df.copy(deep=True)

            # 2. Persist to SQLite
            try:
                from database.connection import get_session
                from database.db_ops import clear_all_records, save_dataframe
                from database.connection import init_database

                # Make sure tables exist (idempotent)
                if not self._db_available:
                    init_database()
                    self._db_available = True

                with get_session() as db:
                    clear_all_records(db)       # replace, don't append
                    batch = save_dataframe(db, df)
                    logger.info(
                        "SalesDataStore.save: %d rows written to DB (batch=%s)",
                        len(df), batch,
                    )
            except Exception as exc:
                logger.error(
                    "SalesDataStore.save: DB write failed — running RAM-only. "
                    "Error: %s", exc,
                )
                self._db_available = False

    # ── Read ──────────────────────────────────────────────────────────────────

    def load(self) -> Optional[pd.DataFrame]:
        """
        Return the current dataset as a DataFrame.

        1. Serves from RAM cache when available (fast path).
        2. Loads from SQLite when RAM cache is empty (e.g. after restart).
        3. Returns None when no data has ever been uploaded.
        """
        with self._lock:
            # Fast path — RAM hit
            if self._cache is not None and not self._cache.empty:
                return self._cache.copy(deep=True)

            # Slow path — hydrate from DB
            if self._db_available:
                try:
                    from database.connection import get_session
                    from database.db_ops import load_all_as_dataframe

                    with get_session() as db:
                        df = load_all_as_dataframe(db)

                    if not df.empty:
                        self._cache = df   # warm the cache
                        logger.info(
                            "SalesDataStore.load: hydrated %d rows from DB into RAM cache",
                            len(df),
                        )
                        return self._cache.copy(deep=True)
                except Exception as exc:
                    logger.error(
                        "SalesDataStore.load: DB read failed — returning None. "
                        "Error: %s", exc,
                    )

            return None

    # ── Utilities ─────────────────────────────────────────────────────────────

    def clear(self) -> None:
        """Wipe both the RAM cache and all SQLite rows."""
        with self._lock:
            self._cache = None
            if self._db_available:
                try:
                    from database.connection import get_session
                    from database.db_ops import clear_all_records

                    with get_session() as db:
                        n = clear_all_records(db)
                        logger.info("SalesDataStore.clear: deleted %d DB rows", n)
                except Exception as exc:
                    logger.error("SalesDataStore.clear: DB clear failed: %s", exc)

    def has_data(self) -> bool:
        """
        True when data is available (RAM cache OR database).
        Does NOT load the full dataset — just checks existence.
        """
        with self._lock:
            # Check RAM first
            if self._cache is not None and not self._cache.empty:
                return True

            # Fall back to a lightweight DB count
            if self._db_available:
                try:
                    from database.connection import get_session
                    from database.db_ops import has_data as db_has_data

                    with get_session() as db:
                        return db_has_data(db)
                except Exception:
                    pass

            return False

    def record_count(self) -> int:
        """Return total number of records (RAM cache if available, else DB)."""
        with self._lock:
            if self._cache is not None and not self._cache.empty:
                return len(self._cache)
            if self._db_available:
                try:
                    from database.connection import get_session
                    from database.db_ops import count_records

                    with get_session() as db:
                        return count_records(db)
                except Exception:
                    pass
            return 0


# Module-level singleton — imported everywhere as `from data_store import store`
store = SalesDataStore()
