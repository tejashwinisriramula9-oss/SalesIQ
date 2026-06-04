import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

EXPECTED_COLUMNS = [
    "Date",
    "Product",
    "Region",
    "Customer ID",
    "Quantity",
    "Price",
    "Revenue",
    "Cost",
    "Profit",
]

COLUMN_ALIASES = {
    "order date": "Date",
    "order_date": "Date",
    "date": "Date",
    "product_name": "Product",
    "product": "Product",
    "item": "Product",
    "region": "Region",
    "customer": "Customer ID",
    "customer_id": "Customer ID",
    "client_id": "Customer ID",
    "qty": "Quantity",
    "quantity": "Quantity",
    # both space and underscore variants
    "unit price": "Price",
    "unit_price": "Price",
    "price": "Price",
    "revenue": "Revenue",
    "sales": "Revenue",
    "cost": "Cost",
    "profit": "Profit",
}

RNG = np.random.default_rng(42)


def normalize_columns(columns: List[str]) -> List[str]:
    normalized = []
    for value in columns:
        key = value.strip().lower()
        if key in COLUMN_ALIASES:
            normalized.append(COLUMN_ALIASES[key])
        else:
            normalized.append(value.strip())
    return normalized


def validate_csv_filename(filename: str) -> Tuple[bool, Optional[str]]:
    if not filename:
        return False, "No filename provided."

    normalized = filename.strip().lower()
    if not normalized.endswith(".csv"):
        return False, "Uploaded file must be a .csv file."
    return True, None


def read_csv_file(file_stream: io.BufferedReader) -> pd.DataFrame:
    file_stream.seek(0)
    try:
        df = pd.read_csv(file_stream)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    except Exception as exc:
        raise ValueError(f"Unable to read CSV content: {exc}")

    if df.empty:
        return pd.DataFrame()

    df.columns = normalize_columns(list(df.columns))
    return df


def clean_sales_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    df = df.copy(deep=True)
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    for col in missing_columns:
        df[col] = np.nan

    df = df[EXPECTED_COLUMNS]

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Product"] = df["Product"].fillna("Unknown").astype(str)
    df["Region"] = df["Region"].fillna("Unknown").astype(str)
    df["Customer ID"] = df["Customer ID"].fillna("Unknown").astype(str)

    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0).astype(float)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0.0).astype(float)
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce")

    computed_revenue = df["Quantity"] * df["Price"]
    df["Revenue"] = df["Revenue"].fillna(computed_revenue)
    df["Revenue"] = df["Revenue"].fillna(0.0).astype(float)

    df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")
    missing_cost = df["Cost"].isna() | (df["Cost"] < 0)
    df.loc[missing_cost, "Cost"] = (
        df.loc[missing_cost, "Revenue"]
        * RNG.uniform(0.7, 0.9, size=int(missing_cost.sum()))
    )
    df["Cost"] = df["Cost"].fillna(0.0).astype(float)

    # Recalculate Profit (or use supplied value if already present and valid)
    profit = pd.to_numeric(df.get("Profit", pd.Series(dtype=float)), errors="coerce")
    computed_profit = df["Revenue"] - df["Cost"]
    profit = profit.fillna(computed_profit)
    df["Profit"] = profit.astype(float)

    # Remove rows with invalid dates or missing essential date information
    df = df[df["Date"].notna()]
    df = df.reset_index(drop=True)
    return df


def apply_filters(
    df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    product: Optional[List[str]] = None,
    region: Optional[List[str]] = None,
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    filtered = df.copy(deep=True)

    if start_date:
        start = parse_iso_date(start_date)
        if start is not None:
            filtered = filtered[filtered["Date"] >= start]

    if end_date:
        end = parse_iso_date(end_date)
        if end is not None:
            filtered = filtered[filtered["Date"] <= end]

    if product:
        normalized = [value.strip().lower() for value in product if value.strip()]
        filtered = filtered[filtered["Product"].str.lower().isin(normalized)]

    if region:
        normalized = [value.strip().lower() for value in region if value.strip()]
        filtered = filtered[filtered["Region"].str.lower().isin(normalized)]

    return filtered.reset_index(drop=True)


def parse_iso_date(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return pd.to_datetime(value, utc=False, errors="coerce")
    except Exception:
        return None


def parse_csv_filter(value: Optional[str]) -> Optional[List[str]]:
    if not value:
        return None
    tokens = [token.strip() for token in value.split(",") if token.strip()]
    return tokens if tokens else None


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue().encode("utf-8")
