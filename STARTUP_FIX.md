# ✅ SalesIQ - Connection Refused Error FIXED

## Problem You Were Facing
❌ **Error:** `http://127.0.0.1:8000/` returned "Connection Refused"

## Root Cause
The FastAPI backend was **NOT RUNNING**. The `main.py` file didn't have startup code to launch the server.

---

## ✅ SOLUTION IMPLEMENTED

### What I Fixed
1. **Added startup code to `main.py`** - Added `if __name__ == "__main__"` block with uvicorn server startup
2. **Fixed dependency conflict** - Updated Streamlit and Starlette versions for compatibility
3. **Verified the fix** - Backend now responds with HTTP 200 OK on port 8000

### The Fix Applied
```python
# Added at end of main.py:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
```

---

## 🚀 HOW TO RUN THE APPLICATION

### Option 1: TWO TERMINAL APPROACH (Recommended)

**Terminal 1 - Start Backend API (Port 8000)**
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Output should show:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 - Start Streamlit Frontend (Port 8501)**
```bash
python -m streamlit run app.py
```
Output should show:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Option 2: DIRECT PYTHON RUN

**Terminal 1 - Run Backend**
```bash
python main.py
```

**Terminal 2 - Run Frontend**
```bash
python -m streamlit run app.py
```

---

## 🌐 VERIFY IT'S WORKING

### Backend Health Check (Port 8000)
```bash
powershell -Command "Invoke-WebRequest -Uri http://127.0.0.1:8000/health | Select-Object -ExpandProperty Content"
```
Expected response:
```json
{"success":true,"status":"healthy","data_loaded":false}
```

### Access Points
- **Backend API**: http://127.0.0.1:8000
- **Backend Docs**: http://127.0.0.1:8000/docs (Swagger UI)
- **Frontend Dashboard**: http://localhost:8501

---

## 📊 PROJECT ARCHITECTURE

This is a **Two-Tier Application**:

### Tier 1: Backend (FastAPI on Port 8000)
- **File**: `main.py`
- **Purpose**: REST API for data processing and analytics
- **Key Endpoints**:
  - `GET /` - Root info
  - `GET /health` - Health check
  - `POST /upload-csv` - Upload sales data
  - `GET /sales-summary` - Sales analytics
  - `GET /customer-analysis` - Customer insights
  - `GET /profit-analysis` - Profitability metrics
  - `GET /forecast` - Sales forecasting
  - `GET /filter-data` - Data filtering

### Tier 2: Frontend (Streamlit on Port 8501)
- **File**: `app.py`
- **Purpose**: Interactive web dashboard
- **Features**:
  - Executive Dashboard with 6 KPI metrics
  - CSV file upload
  - Real-time analytics
  - Data visualization with Plotly
  - Professional UI with glassmorphism design

### Data Flow
```
CSV File → Streamlit Upload → Backend Processing → JSON Response → Dashboard Display
```

---

## 📁 KEY PROJECT FILES

| File | Purpose |
|------|---------|
| `main.py` | FastAPI backend server (Port 8000) |
| `app.py` | Streamlit frontend dashboard (Port 8501) |
| `services.py` | Business logic and data processing |
| `data_store.py` | In-memory data storage |
| `backend_utils.py` | Utility functions |
| `analytics/` | Analytics modules (sales, customer, profitability) |
| `forecasting/` | ML forecasting models |
| `config/settings.py` | Application configuration |
| `data/sample_sales.csv` | Sample data for testing |

---

## 🎯 WHAT THIS APPLICATION DOES

**SalesIQ** is an AI-powered Sales Intelligence Platform that:

1. **Analyzes Sales Data** - Process CSV files with sales records
2. **Generates Insights** - Calculate KPIs (revenue, profit, orders, margins)
3. **Forecasts Trends** - ML-based sales predictions
4. **Interactive Dashboard** - Real-time visualization and filtering
5. **Exports Reports** - Generate PDF/Excel reports

### Sample Use Cases:
- Track monthly/quarterly revenue trends
- Identify top-performing products and regions
- Analyze customer purchase patterns
- Forecast future sales
- Monitor profit margins by category

---

## ⚡ TROUBLESHOOTING

### Problem: Port 8000 still shows "Connection Refused"
**Solution**: Make sure you ran one of the startup commands in a terminal first

### Problem: Streamlit shows import errors
**Solution**: Dependencies may be outdated. Run:
```bash
pip install --upgrade streamlit starlette fastapi uvicorn
```

### Problem: Cannot find modules (services, data_store, etc.)
**Solution**: Make sure you're in the SalesIQ project directory:
```bash
cd C:\Users\CHARAN\OneDrive\Desktop\SalesIQ
```

### Problem: "Address already in use"
**Solution**: Another process is using port 8000 or 8501. Either:
- Kill the existing process
- Use different ports with `--port` flag

---

## 📈 NEXT STEPS

1. ✅ Start Backend (Port 8000) - See **HOW TO RUN** section above
2. ✅ Start Frontend (Port 8501) - Open browser to http://localhost:8501
3. ✅ Upload Sample Data - Use the CSV upload button
4. ✅ View Analytics - Check KPI cards and charts
5. ✅ Export Reports - Generate PDF/Excel exports

---

## ✨ THE FIX SUMMARY

| Before | After |
|--------|-------|
| ❌ Port 8000 refused connection | ✅ Port 8000 responds with HTTP 200 |
| ❌ No startup code in main.py | ✅ Added uvicorn startup block |
| ❌ Dependency conflicts | ✅ Updated to compatible versions |
| ❌ No way to run backend | ✅ Multiple startup options available |

---

**Status**: ✅ **READY TO USE**  
**Backend**: ✅ Confirmed working on http://127.0.0.1:8000  
**Frontend**: ✅ Ready to launch with Streamlit
