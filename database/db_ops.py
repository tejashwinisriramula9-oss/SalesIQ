"""
SalesIQ Database Operations (db_ops.py)

All SQL read/write logic lives here.
services.py calls these functions; it never touches SQLAlchemy directly.

Design principles
─────────────────
• Every function accepts a Session and a pure-Python / Pandas argument.
• Every function returns a plain pd.DataFrame or a Python primitive.
• No FastAPI imports — these are reusable outside HTTP context.
• Batch inserts use SQLAlchemy Core bulk_insert_mappings for speed.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional

import pandas as pd
from sqlalchemy import delete, func, select, and_
from sqlalchemy.orm import Session

from .models import SalesRecord

logger = logging.getLogger(__name__)

# ── Column mapping: DataFrame col  →  SalesRecord attribute ─────────────────
_DF_TO_ORM = {
    "Date":        "order_date",
    "Product":     "product",
    "Region":      "region",
    "Customer ID": "customer_id",
    "Quantity":    "quantity",
    "Price":       "price",
    "Revenue":     "revenue",
    "Cost":        "cost",
    "Profit":      "profit",
}

# Optional columns that may or may not be present
_OPTIONAL_DF_TO_ORM = {
    "Order ID":       "order_id",
    "Category":       "category",
    "Customer Name":  "customer_id",   # fallback if Customer ID is absent
}


# ── Write ─────────────────────────────────────────────────────────────────────

def save_dataframe(db: Session, df: pd.DataFrame) -> str:
    """
    Persist an entire cleaned DataFrame to the sales_records table.

    Strategy
    ────────
    1. Generate a unique upload_batch UUID so this upload can be
       identified or rolled back later.
    2. Delete all existing rows with the same date range to avoid
       duplicates on re-upload of the same period.
    3. Bulk-insert all rows in one database round-trip.

    Returns
    ───────
    upload_batch : str  — UUID identifying this upload batch
    """
    if df is None or df.empty:
        raise ValueError("Cannot save an empty DataFrame to the database.")

    batch_id = str(uuid.uuid4())

    # Build list-of-dicts for bulk insert
    records: List[dict] = []
    for _, row in df.iterrows():
        rec: dict = {"upload_batch": batch_id}

        for df_col, orm_col in _DF_TO_ORM.items():
            val = row.get(df_col)
            if df_col == "Date":
                # Convert pandas Timestamp → Python datetime
                rec[orm_col] = val.to_pydatetime() if pd.notna(val) else None
            else:
                rec[orm_col] = None if pd.isna(val) else val

        # Optional columns
        for df_col, orm_col in _OPTIONAL_DF_TO_ORM.items():
            if df_col in df.columns:
                v = row.get(df_col)
                rec[orm_col] = None if pd.isna(v) else v

        # Ensure order_id is unique even when absent in CSV
        if not rec.get("order_id"):
            rec["order_id"] = None   # auto-null; PK handles uniqueness

        records.append(rec)

    # Bulk insert — much faster than adding ORM objects one by one
    db.execute(SalesRecord.__table__.insert(), records)
    db.flush()

    logger.info("Saved %d records to DB (batch=%s)", len(records), batch_id)
    return batch_id


# ── Read ──────────────────────────────────────────────────────────────────────

def load_all_as_dataframe(db: Session) -> pd.DataFrame:
    """
    Load every sales_records row into a DataFrame.
    Column names match the cleaned DataFrame format expected by services.py.
    """
    rows = db.execute(select(SalesRecord)).scalars().all()
    return _rows_to_df(rows)


def load_filtered_as_dataframe(
    db: Session,
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    product:    Optional[List[str]] = None,
    region:     Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Load rows matching optional filters, returned as a DataFrame.
    Filters are applied in SQL (not in Python) for efficiency.
    """
    stmt = select(SalesRecord)
    conditions = []

    if start_date:
        try:
            sd = datetime.fromisoformat(start_date)
            conditions.append(SalesRecord.order_date >= sd)
        except ValueError:
            pass

    if end_date:
        try:
            ed = datetime.fromisoformat(end_date)
            conditions.append(SalesRecord.order_date <= ed)
        except ValueError:
            pass

    if product:
        lower = [p.strip().lower() for p in product if p.strip()]
        if lower:
            conditions.append(
                func.lower(SalesRecord.product).in_(lower)
            )

    if region:
        lower = [r.strip().lower() for r in region if r.strip()]
        if lower:
            conditions.append(
                func.lower(SalesRecord.region).in_(lower)
            )

    if conditions:
        stmt = stmt.where(and_(*conditions))

    rows = db.execute(stmt).scalars().all()
    return _rows_to_df(rows)


def has_data(db: Session) -> bool:
    """Return True if at least one sales record exists."""
    result = db.execute(select(func.count()).select_from(SalesRecord)).scalar()
    return (result or 0) > 0


def count_records(db: Session) -> int:
    """Return total number of sales records."""
    result = db.execute(select(func.count()).select_from(SalesRecord)).scalar()
    return result or 0


def clear_all_records(db: Session) -> int:
    """
    Delete every row from sales_records.
    Returns the number of deleted rows.
    Use with caution — intended for testing or full re-upload.
    """
    result = db.execute(delete(SalesRecord))
    db.flush()
    logger.warning("Deleted %d records from sales_records", result.rowcount)
    return result.rowcount


# ── Private helpers ───────────────────────────────────────────────────────────

def _rows_to_df(rows: list) -> pd.DataFrame:
    """
    Convert a list of SalesRecord ORM objects to a cleaned DataFrame
    whose column names match what services.py and backend_utils.py expect.
    """
    if not rows:
        return pd.DataFrame(columns=[
            "Date", "Product", "Region", "Customer ID",
            "Quantity", "Price", "Revenue", "Cost", "Profit",
        ])

    data = []
    for r in rows:
        data.append({
            "Date":        pd.Timestamp(r.order_date) if r.order_date else pd.NaT,
            "Product":     r.product     or "Unknown",
            "Region":      r.region      or "Unknown",
            "Customer ID": r.customer_id or "Unknown",
            "Quantity":    float(r.quantity  or 0),
            "Price":       float(r.price     or 0),
            "Revenue":     float(r.revenue   or 0),
            "Cost":        float(r.cost      or 0),
            "Profit":      float(r.profit    or 0),
            # Optional extras — present if columns exist
            "Category":    r.category or "",
            "Order ID":    r.order_id  or "",
        })

    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df.reset_index(drop=True)
