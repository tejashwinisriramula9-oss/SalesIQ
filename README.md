# 📊 SalesIQ — AI Sales Intelligence Platform

A full-stack business intelligence web application that transforms raw CSV sales data into interactive analytics, AI-powered forecasts, and executive-level dashboards.

## 🚀 Live Demo

| Service | URL |
|---|---|
| Frontend Dashboard | https://tejashwinisriramula9-oss-salesiq-app-axccm8.streamlit.app/ |
| Backend API | https://salesiq-backend-3yr9.onrender.com |
| Swagger Docs | https://salesiq-backend-3yr9.onrender.com/docs |

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit 1.58 + Plotly 6.7 |
| Backend | FastAPI 0.136 + Uvicorn |
| Database | SQLite (SQLAlchemy 2.0 ORM) |
| ML / Analytics | scikit-learn, pandas, numpy |
| Language | Python 3.11 |

---

## ✨ Features

- **CSV Upload** — drag-and-drop sales data with auto column normalization
- **Executive Dashboard** — KPI cards, revenue trends, regional breakdown
- **Sales Analytics** — top products, revenue share, tabbed charts
- **Customer Intelligence** — segments (High/Medium/Low value), top customers
- **Profit Analysis** — margin analysis, loss-making product detection
- **AI Forecasting** — 7–90 day linear regression revenue forecast with confidence bands
- **Filter & Explore** — date/product/region filters across all pages
- **Export Reports** — download filtered data as CSV
- **Persistent Storage** — SQLite database survives server restarts
- **Light/Dark Theme** — toggle in sidebar
- **API Documentation** — live Swagger UI at `/docs`

---

## 📁 Project Structure

```
SalesIQ/
├── app.py                  # Streamlit frontend (8 pages)
├── main.py                 # FastAPI backend (13 endpoints)
├── services.py             # Business logic layer
├── backend_utils.py        # CSV parsing & cleaning
├── data_store.py           # Dual RAM + SQLite storage
│
├── database/
│   ├── models.py           # SQLAlchemy ORM models
│   ├── connection.py       # DB engine + session management
│   └── db_ops.py           # SQL read/write operations
│
├── analytics/
│   ├── sales_analytics.py
│   ├── customer_analytics.py
│   └── profitability_analytics.py
│
├── forecasting/
│   └── forecasting_models.py  # Linear Regression + Random Forest
│
├── utils/
│   ├── insights_engine.py
│   └── data_processor.py
│
├── data/
│   └── sample_sales.csv    # 45-row demo dataset
│
└── requirements.txt
```

---

## ⚡ Quick Start (Local)

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/SalesIQ.git
cd SalesIQ
```

### 2. Create virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the backend
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

### 5. Start the frontend (new terminal)
```bash
streamlit run app.py
```

### 6. Open in browser
- **Dashboard:** http://localhost:8501
- **API Docs:** http://127.0.0.1:8000/docs

### 7. Upload sample data
Upload `data/sample_sales.csv` from the dashboard to get started.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload-csv` | Upload sales data CSV |
| `GET` | `/sales-summary` | KPI totals + monthly growth |
| `GET` | `/top-products` | Top N products by revenue |
| `GET` | `/customer-analysis` | Customer segments & CLV |
| `GET` | `/profit-analysis` | Profit margins & losses |
| `GET` | `/forecast` | ML revenue forecast (1–90 days) |
| `GET` | `/filter-data` | Paginated filtered records |
| `GET` | `/download-report` | Export filtered data as CSV |
| `GET` | `/health` | Backend health + DB status |

All filter endpoints accept: `start_date`, `end_date`, `product`, `region`

---

## 📊 Sample CSV Format

```csv
Order ID,Order Date,Customer ID,Customer Name,Product,Category,Region,Quantity,Unit Price,Revenue,Cost,Profit
ORD-001,2024-01-05,CUST-101,Acme Corp,Laptop,Electronics,North,1,1200.00,1200.00,720.00,480.00
```

---


## 📸 Screenshots

### 🏠 Dashboard
![Dashboard](screenshots/dashboard1.png)
![Dashboard](screenshots/dashboard2.png)

---

### 📊 Sales Analytics
![Sales Analytics](screenshots/sales_analytics.png)

---

### 👥 Customer Intelligence
![Customer Intelligence](screenshots/customer_intelligence.png)

---

### 💰 Profit Analysis
![Profit Analysis](screenshots/profit__analysis.png)

---

### 🔮 Forecasting
![Forecasting](screenshots/forecasting.png)

---

### 🔍 Filter & Explore Reports
![Filter Explore](screenshots/filter_explore.png)

---

### 📡 API Docs
![API Docs](screenshots/api.docs.png)

---

## ⚙️ Setup Instructions

```bash
# Clone repository
git clone https://github.com/your-username/salesiq.git

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn backend.main:app --reload

# Run frontend
streamlit run app.py


## 📄 License

MIT License — free to use for portfolio, learning, and commercial projects.
