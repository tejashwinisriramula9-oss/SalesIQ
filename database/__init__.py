"""
SalesIQ Database package.

Exports everything consumers need so they can write:
    from database import SalesRecord, get_db, init_database
"""

from .models import (
    Base,
    SalesRecord,
    Customer,
    Product,
    ForecastResult,
    BusinessInsight,
)
from .connection import (
    engine,
    SessionLocal,
    get_db,
    get_session,
    init_database,
    db_ping,
)

__all__ = [
    # Models
    "Base",
    "SalesRecord",
    "Customer",
    "Product",
    "ForecastResult",
    "BusinessInsight",
    # Connection helpers
    "engine",
    "SessionLocal",
    "get_db",
    "get_session",
    "init_database",
    "db_ping",
]
