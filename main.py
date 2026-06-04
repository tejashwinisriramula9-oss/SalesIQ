"""
SalesIQ FastAPI backend.

Changes vs original:
  - startup event calls init_database() so tables are created before
    the first request arrives.
  - /health endpoint now reports db_online status.
  - All route handlers are unchanged.
"""

import logging

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.openapi.utils import get_openapi

import services
from data_store import store

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SalesIQ – AI Sales Intelligence Platform",
    version="1.0.0",
    description=(
        "Backend API for sales analytics, customer insights, profit analysis, "
        "forecasting, and CSV management."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup ───────────────────────────────────────────────────────────────────

@app.on_event("startup")
def on_startup() -> None:
    """
    Initialise the SQLite database on server start.
    Creates tables if they don't exist; safe to run on every restart.
    """
    try:
        from database.connection import init_database
        init_database()
        logger.info("Database initialised on startup.")
    except Exception as exc:
        logger.error("Database startup initialisation failed: %s", exc)
        # We do NOT crash here — the app still works in RAM-only mode.


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_comma_list(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


# ── Endpoints (all unchanged from original) ───────────────────────────────────

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(..., description="Sales data CSV file")):
    """
    Upload a sales CSV file.

    The file must be a valid CSV with columns such as:
    Order Date, Product, Category, Region, Customer ID, Quantity, Unit Price, Revenue, Cost, Profit.
    Column names are normalised automatically.
    """
    try:
        result = services.load_csv_content(file)
        return JSONResponse({"success": True, "message": result["message"], "metadata": result})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to upload CSV: {exc}")


@app.get("/sales-summary")
def sales_summary(
    start_date: str | None = Query(None, description="Start date filter YYYY-MM-DD"),
    end_date:   str | None = Query(None, description="End date filter YYYY-MM-DD"),
    product:    str | None = Query(None, description="Comma-separated products"),
    region:     str | None = Query(None, description="Comma-separated regions"),
):
    try:
        data = services.sales_summary(
            start_date=parse_comma_list(start_date),
            end_date=parse_comma_list(end_date),
            product=parse_comma_list(product),
            region=parse_comma_list(region),
        )
        return JSONResponse(data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Sales summary failed: {exc}")


@app.get("/top-products")
def top_products(
    start_date: str | None = Query(None),
    end_date:   str | None = Query(None),
    product:    str | None = Query(None),
    region:     str | None = Query(None),
    top_n: int = Query(10, ge=1, le=50),
):
    try:
        data = services.top_products(
            start_date=parse_comma_list(start_date),
            end_date=parse_comma_list(end_date),
            product=parse_comma_list(product),
            region=parse_comma_list(region),
            top_n=top_n,
        )
        return JSONResponse({"success": True, "data": data})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Top products failed: {exc}")


@app.get("/customer-analysis")
def customer_analysis(
    start_date: str | None = Query(None),
    end_date:   str | None = Query(None),
    product:    str | None = Query(None),
    region:     str | None = Query(None),
):
    try:
        data = services.customer_analysis(
            start_date=parse_comma_list(start_date),
            end_date=parse_comma_list(end_date),
            product=parse_comma_list(product),
            region=parse_comma_list(region),
        )
        return JSONResponse({"success": True, "data": data})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Customer analysis failed: {exc}")


@app.get("/profit-analysis")
def profit_analysis(
    start_date: str | None = Query(None),
    end_date:   str | None = Query(None),
    product:    str | None = Query(None),
    region:     str | None = Query(None),
):
    try:
        data = services.profit_analysis(
            start_date=parse_comma_list(start_date),
            end_date=parse_comma_list(end_date),
            product=parse_comma_list(product),
            region=parse_comma_list(region),
        )
        return JSONResponse({"success": True, "data": data})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Profit analysis failed: {exc}")


@app.get("/forecast")
def forecast(
    start_date: str | None = Query(None),
    end_date:   str | None = Query(None),
    product:    str | None = Query(None),
    region:     str | None = Query(None),
    days: int = Query(30, ge=1, le=90),
):
    try:
        data = services.forecast_sales(
            start_date=parse_comma_list(start_date),
            end_date=parse_comma_list(end_date),
            product=parse_comma_list(product),
            region=parse_comma_list(region),
            days=days,
        )
        return JSONResponse({"success": True, "data": data})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Forecast failed: {exc}")


@app.get("/filter-data")
def filter_data(
    start_date: str | None = Query(None),
    end_date:   str | None = Query(None),
    product:    str | None = Query(None),
    region:     str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    try:
        data = services.filter_data(
            start_date=parse_comma_list(start_date),
            end_date=parse_comma_list(end_date),
            product=parse_comma_list(product),
            region=parse_comma_list(region),
            limit=limit,
        )
        return JSONResponse({"success": True, "data": data})
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Filter request failed: {exc}")


@app.get("/download-report")
def download_report(
    start_date: str | None = Query(None),
    end_date:   str | None = Query(None),
    product:    str | None = Query(None),
    region:     str | None = Query(None),
):
    try:
        csv_bytes = services.export_report(
            start_date=parse_comma_list(start_date),
            end_date=parse_comma_list(end_date),
            product=parse_comma_list(product),
            region=parse_comma_list(region),
        )
        if not csv_bytes:
            raise HTTPException(status_code=404, detail="No report available to download.")

        response = StreamingResponse(iter([csv_bytes]), media_type="text/csv")
        response.headers["Content-Disposition"] = (
            "attachment; filename=SalesIQ_report.csv"
        )
        return response
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}")


@app.get("/")
def root():
    return JSONResponse({
        "success": True,
        "message": (
            "SalesIQ backend is running. "
            "Use /upload-csv to import data and the analytics endpoints to retrieve results."
        ),
    })


@app.get("/health")
def health_check():
    """
    Returns liveness + data status.
    Now includes db_online flag so the frontend can show DB status.
    """
    from database.connection import db_ping

    return JSONResponse({
        "success":    True,
        "status":     "healthy",
        "data_loaded": store.has_data(),
        "db_online":  db_ping(),
        "record_count": store.record_count(),
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


# ── Custom OpenAPI: force format=binary for Swagger file picker ───────────────
def _custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Patch the upload-csv body schema so ALL Swagger versions show the file button
    schemas = schema.get("components", {}).get("schemas", {})
    for schema_name, schema_body in schemas.items():
        if "upload_csv" in schema_name.lower() or "upload-csv" in schema_name.lower():
            props = schema_body.get("properties", {})
            if "file" in props:
                props["file"] = {
                    "type":        "string",
                    "format":      "binary",
                    "title":       "CSV File",
                    "description": "Sales data CSV file",
                }

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = _custom_openapi
