"""
SalesIQ Service Layer

What changed vs the original:
  - get_active_dataframe()    → still calls store.load() (unchanged API)
  - get_filtered_dataframe()  → unchanged
  - load_csv_content()        → unchanged (store.save() now writes to DB too)
  - All analytics functions   → completely unchanged

The dual-layer data_store.py handles the DB/RAM logic transparently.
services.py never touches SQLAlchemy directly.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from data_store import store
from backend_utils import (
    apply_filters,
    clean_sales_dataframe,
    dataframe_to_csv_bytes,
    parse_csv_filter,
    read_csv_file,
    validate_csv_filename,
)


# ── CSV ingestion ─────────────────────────────────────────────────────────────

def load_csv_content(file) -> Dict[str, object]:
    """
    Validate → read → clean → save.
    store.save() now persists to both RAM and SQLite automatically.
    """
    valid, error_message = validate_csv_filename(file.filename)
    if not valid:
        raise ValueError(error_message)

    df = read_csv_file(file.file)
    if df.empty:
        raise ValueError("CSV file is empty or contains no valid rows.")

    cleaned_df = clean_sales_dataframe(df)
    if cleaned_df.empty:
        raise ValueError("Uploaded CSV does not contain valid sales data.")

    store.save(cleaned_df)   # ← writes RAM + SQLite
    return {
        "message": "CSV uploaded and processed successfully.",
        "row_count": len(cleaned_df),
        "columns": list(cleaned_df.columns),
    }


# ── Data access helpers ───────────────────────────────────────────────────────

def get_active_dataframe() -> pd.DataFrame:
    """
    Load the full dataset.
    On first call after a server restart, store.load() silently rehydrates
    from SQLite so callers never need to know about the DB.
    """
    df = store.load()
    if df is None:
        raise ValueError("No sales data is available. Upload a CSV file first.")
    return df


def get_filtered_dataframe(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    product:    Optional[str] = None,
    region:     Optional[str] = None,
) -> pd.DataFrame:
    df = get_active_dataframe()
    return apply_filters(
        df,
        start_date=start_date,
        end_date=end_date,
        product=parse_csv_filter(product),
        region=parse_csv_filter(region),
    )


# ── Analytics endpoints ───────────────────────────────────────────────────────

def sales_summary(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    product:    Optional[str] = None,
    region:     Optional[str] = None,
) -> Dict[str, object]:
    df = get_filtered_dataframe(start_date, end_date, product, region)

    if df.empty:
        return {
            "total_revenue":   0.0,
            "avg_order_value": 0.0,
            "total_orders":    0,
            "monthly_growth":  {},
            "best_region":     "N/A",
        }

    total_revenue = float(df["Revenue"].sum())
    total_orders  = int(len(df))
    avg_order_value = float(round(total_revenue / total_orders, 2)) if total_orders else 0.0

    region_summary = (
        df.groupby("Region", observed=True)["Revenue"]
        .sum().sort_values(ascending=False)
    )
    best_region = str(region_summary.index[0]) if not region_summary.empty else "N/A"

    monthly = df.set_index("Date").resample("ME")["Revenue"].sum().sort_index()
    monthly_growth = monthly.pct_change().fillna(0.0) * 100
    monthly_growth_map = {
        period.strftime("%Y-%m"): float(round(value, 2))
        for period, value in zip(monthly.index, monthly_growth.values)
    }

    return {
        "total_revenue":   float(round(total_revenue, 2)),
        "avg_order_value": avg_order_value,
        "total_orders":    total_orders,
        "monthly_growth":  monthly_growth_map,
        "best_region":     best_region,
    }


def top_products(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    product:    Optional[str] = None,
    region:     Optional[str] = None,
    top_n: int = 10,
) -> Dict[str, object]:
    df = get_filtered_dataframe(start_date, end_date, product, region)
    summary = (
        df.groupby("Product", observed=True)["Revenue"]
        .sum().sort_values(ascending=False)
    )
    return {
        "top_products": [
            {"product": prod, "revenue": float(round(rev, 2))}
            for prod, rev in summary.head(top_n).items()
        ],
        "count": len(summary),
    }


def customer_analysis(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    product:    Optional[str] = None,
    region:     Optional[str] = None,
) -> Dict[str, object]:
    df = get_filtered_dataframe(start_date, end_date, product, region)
    if df.empty:
        return {
            "message":            "No customer data found for the selected filters.",
            "total_customers":    0,
            "new_customers":      0,
            "returning_customers": 0,
            "segments":           [],
            "top_customers":      [],
        }

    revenue_by_customer = df.groupby("Customer ID", observed=True)["Revenue"].sum()
    first_order_date    = df.groupby("Customer ID", observed=True)["Date"].min()
    max_date  = df["Date"].max()
    threshold = max_date - timedelta(days=30)

    new_customers      = int((first_order_date >= threshold).sum())
    total_customers    = int(revenue_by_customer.size)
    returning_customers = total_customers - new_customers

    q1 = float(revenue_by_customer.quantile(0.33))
    q2 = float(revenue_by_customer.quantile(0.66))

    segments = {
        "high_value":   int((revenue_by_customer >= q2).sum()),
        "medium_value": int((revenue_by_customer >= q1).sum()) - int((revenue_by_customer >= q2).sum()),
        "low_value":    int((revenue_by_customer < q1).sum()),
    }

    top_customers = [
        {"customer_id": cid, "clv": float(round(spend, 2))}
        for cid, spend in revenue_by_customer.sort_values(ascending=False).head(10).items()
    ]

    return {
        "total_customers":      total_customers,
        "new_customers":        new_customers,
        "returning_customers":  returning_customers,
        "segments":             segments,
        "top_customers":        top_customers,
        "average_customer_value": float(round(revenue_by_customer.mean(), 2)),
    }


def profit_analysis(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    product:    Optional[str] = None,
    region:     Optional[str] = None,
) -> Dict[str, object]:
    df = get_filtered_dataframe(start_date, end_date, product, region)
    if df.empty:
        return {
            "message":              "No profit data available for the selected filters.",
            "profitable_products":  [],
            "loss_making_products": [],
            "product_margins":      [],
            "total_profit":         0.0,
        }

    grouped = df.groupby("Product", observed=True).agg(
        total_revenue=("Revenue", "sum"),
        total_cost=("Cost",    "sum"),
        total_profit=("Profit",  "sum"),
    )
    grouped["profit_margin"] = np.where(
        grouped["total_revenue"] > 0,
        (grouped["total_profit"] / grouped["total_revenue"]) * 100,
        0.0,
    )
    grouped = grouped.sort_values(by="total_profit", ascending=False)

    profitable_products = [
        {
            "product":      prod,
            "total_profit": float(round(row.total_profit, 2)),
            "margin_pct":   float(round(row.profit_margin, 2)),
        }
        for prod, row in grouped.head(5).iterrows()
    ]

    losses = grouped[grouped["total_profit"] < 0]
    loss_products = [
        {
            "product":      prod,
            "total_profit": float(round(row.total_profit, 2)),
            "margin_pct":   float(round(row.profit_margin, 2)),
        }
        for prod, row in losses.iterrows()
    ]

    product_margins = [
        {
            "product":           prod,
            "profit_margin_pct": float(round(row.profit_margin, 2)),
        }
        for prod, row in grouped.sort_values(
            by="profit_margin", ascending=False
        ).head(10).iterrows()
    ]

    return {
        "profitable_products":  profitable_products,
        "loss_making_products": loss_products,
        "product_margins":      product_margins,
        "total_profit":         float(round(grouped["total_profit"].sum(), 2)),
    }


def forecast_sales(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    product:    Optional[str] = None,
    region:     Optional[str] = None,
    days: int = 30,
) -> Dict[str, object]:
    df = get_filtered_dataframe(start_date, end_date, product, region)
    if df.empty:
        return {"message": "No data available for forecasting.", "forecast": []}

    if df.shape[0] < 2:
        raise ValueError(
            "Not enough historical sales data. Upload at least 2 valid sales rows."
        )

    daily_sales = (
        df.groupby("Date", observed=True)["Revenue"]
        .sum().asfreq("D", fill_value=0).sort_index()
    )
    if daily_sales.shape[0] < 2:
        raise ValueError(
            "At least 2 distinct dates are required for forecasting."
        )

    X = np.array(
        (daily_sales.index - daily_sales.index.min()).days
    ).reshape(-1, 1)
    y = daily_sales.values

    model = LinearRegression()
    model.fit(X, y)

    last_day     = daily_sales.index.max()
    future_dates = [last_day + timedelta(days=i) for i in range(1, days + 1)]
    X_future     = np.array(
        [(d - daily_sales.index.min()).days for d in future_dates]
    ).reshape(-1, 1)
    predicted = np.maximum(model.predict(X_future), 0.0)

    return {
        "model": "linear_regression",
        "forecast": [
            {
                "date":              d.strftime("%Y-%m-%d"),
                "predicted_revenue": float(round(float(v), 2)),
            }
            for d, v in zip(future_dates, predicted)
        ],
    }


def filter_data(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    product:    Optional[str] = None,
    region:     Optional[str] = None,
    limit: int = 100,
) -> Dict[str, object]:
    df      = get_filtered_dataframe(start_date, end_date, product, region)
    preview = df.head(limit).copy()

    # Serialise Timestamps to strings
    for col in preview.select_dtypes(
        include=["datetime64[ns]", "datetime64[ns, UTC]", "datetimetz"]
    ).columns:
        preview[col] = preview[col].dt.strftime("%Y-%m-%d")

    return {
        "row_count":    len(df),
        "preview_rows": preview.to_dict(orient="records"),
        "columns":      list(df.columns),
    }


def export_report(
    start_date: Optional[str] = None,
    end_date:   Optional[str] = None,
    product:    Optional[str] = None,
    region:     Optional[str] = None,
) -> bytes:
    df = get_filtered_dataframe(start_date, end_date, product, region)
    return dataframe_to_csv_bytes(df)
