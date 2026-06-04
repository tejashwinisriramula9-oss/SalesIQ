"""
SalesIQ Database Models — SQLAlchemy 2.x compatible
Stores individual sales records. Other models (Customer, Product,
Forecast, Insight) are kept for future use but are not actively
written by the current upload pipeline.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float, Integer, String, Text
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 2.x declarative base."""
    pass


# ---------------------------------------------------------------------------
# Core table — written on every CSV upload
# ---------------------------------------------------------------------------

class SalesRecord(Base):
    """
    One row per sales transaction.
    Column names mirror the cleaned DataFrame produced by backend_utils.
    """
    __tablename__ = "sales_records"

    id          = Column(Integer, primary_key=True, autoincrement=True)

    # ── Identifiers ──────────────────────────────────────────────────────────
    order_id    = Column(String(60),  nullable=True,  index=True)
    customer_id = Column(String(60),  nullable=False, index=True)

    # ── Date ─────────────────────────────────────────────────────────────────
    order_date  = Column(DateTime,    nullable=False, index=True)

    # ── Dimensions ───────────────────────────────────────────────────────────
    product     = Column(String(200), nullable=False, index=True)
    category    = Column(String(100), nullable=True,  index=True)
    region      = Column(String(100), nullable=False, index=True)

    # ── Measures ─────────────────────────────────────────────────────────────
    quantity    = Column(Float,       nullable=False, default=0.0)
    price       = Column(Float,       nullable=False, default=0.0)
    revenue     = Column(Float,       nullable=False, default=0.0)
    cost        = Column(Float,       nullable=False, default=0.0)
    profit      = Column(Float,       nullable=False, default=0.0)

    # ── Upload tracking ───────────────────────────────────────────────────────
    upload_batch = Column(String(40), nullable=True, index=True)
    created_at   = Column(DateTime,   default=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<SalesRecord id={self.id} order_id={self.order_id!r} "
            f"revenue={self.revenue}>"
        )


# ---------------------------------------------------------------------------
# Scaffolded tables — reserved for future features
# ---------------------------------------------------------------------------

class Customer(Base):
    """Customer-level aggregated profile (populated by future analytics job)."""
    __tablename__ = "customers"

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    customer_id             = Column(String(60),  unique=True, nullable=False, index=True)
    customer_name           = Column(String(200), nullable=True)
    region                  = Column(String(100), nullable=True)
    total_orders            = Column(Integer, default=0)
    total_revenue           = Column(Float,   default=0.0)
    total_profit            = Column(Float,   default=0.0)
    avg_order_value         = Column(Float,   default=0.0)
    customer_lifetime_value = Column(Float,   default=0.0)
    rfm_segment             = Column(String(50),  nullable=True)
    first_purchase_date     = Column(DateTime,    nullable=True)
    last_purchase_date      = Column(DateTime,    nullable=True)
    created_at              = Column(DateTime,    default=datetime.utcnow)
    updated_at              = Column(DateTime,    default=datetime.utcnow,
                                     onupdate=datetime.utcnow)


class Product(Base):
    """Product-level aggregated performance (populated by future analytics job)."""
    __tablename__ = "products"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    product_name         = Column(String(200), unique=True, nullable=False, index=True)
    category             = Column(String(100), nullable=True,  index=True)
    total_quantity_sold  = Column(Integer, default=0)
    total_revenue        = Column(Float,   default=0.0)
    total_cost           = Column(Float,   default=0.0)
    total_profit         = Column(Float,   default=0.0)
    profit_margin        = Column(Float,   default=0.0)
    avg_unit_price       = Column(Float,   default=0.0)
    total_orders         = Column(Integer, default=0)
    is_profitable        = Column(Boolean, default=True)
    created_at           = Column(DateTime, default=datetime.utcnow)
    updated_at           = Column(DateTime, default=datetime.utcnow,
                                  onupdate=datetime.utcnow)


class ForecastResult(Base):
    """Persisted forecast results (populated by future scheduled job)."""
    __tablename__ = "forecast_results"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    forecast_type    = Column(String(50),  nullable=False)
    forecast_date    = Column(DateTime,    nullable=False)
    forecast_value   = Column(Float,       nullable=False)
    confidence_lower = Column(Float,       nullable=True)
    confidence_upper = Column(Float,       nullable=True)
    model_used       = Column(String(100), nullable=True)
    model_accuracy   = Column(Float,       nullable=True)
    forecast_period  = Column(String(50),  nullable=True)
    extra_json       = Column(Text,        nullable=True)   # renamed from 'metadata'
    created_at       = Column(DateTime,    default=datetime.utcnow)


class BusinessInsight(Base):
    """Auto-generated business insights (populated by InsightsEngine)."""
    __tablename__ = "business_insights"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    insight_type     = Column(String(50),  nullable=False)
    insight_text     = Column(Text,        nullable=False)
    impact_level     = Column(String(20),  nullable=True)
    confidence_score = Column(Float,       nullable=True)
    is_actionable    = Column(Boolean,     default=True)   # renamed from 'actionable'
    category         = Column(String(50),  nullable=True)
    created_at       = Column(DateTime,    default=datetime.utcnow)
