# UI_BACKUP.md — SalesIQ Pre-Redesign Documentation

## Current UI Structure (as-is before redesign)

### Layout
- Single dark CSS block injected via `st.markdown`
- Streamlit default sidebar navigation via `st.sidebar.radio`
- `st.title()` for page header
- No top navigation bar
- No theme toggle

### Pages
1. 📊 Dashboard — st.header + 4 st.metric cols + 2 plotly charts
2. 📈 Sales Analytics — bar + pie charts + st.dataframe
3. 👥 Customer Intelligence — 4 metrics + pie + dataframe
4. 💰 Profit Analysis — 1 metric + 2 bar charts + bar chart
5. 🔮 Forecasting — slider + line chart + 2 metrics + dataframe
6. 🔍 Filter & Explore — slider + dataframe + pie chart
7. 📄 Reports — button + download_button
8. 📚 API Docs — markdown table + dataframe

### Components
- KPI Cards: bare `st.metric()` — no icons, no trend, no hover
- Charts: basic plotly with manual dark bg (#1c1e26)
- Tables: bare `st.dataframe()`
- Sidebar: text_input + form with date/multiselect
- System Health: markdown text in sidebar
- Dev Status: `st.expander` with 5 metrics + progress bar
- Build Log: `st.expander` with reversed log entries

### CSS (minimal)
```css
body, .stApp { background-color: #0e1117; color: #fafafa; }
.metric-card { background: #1c1e26; border-radius: 10px; ... }
.status-ok / .status-err / .status-warn — color classes
.log-line — monospace small text
```

### Known Design Gaps
- No light/dark theme toggle
- No professional top navbar
- No branded logo/wordmark
- KPI cards have no trend indicators or icons
- Charts lack consistent color palette
- No empty-state illustrations
- No hover effects on cards
- No responsive grid improvements
- Mojibake in title was present (now fixed)
- No premium spacing or typography

---

## Planned UI Changes (redesign targets)

### 1. Theme System
- Light theme: white bg, #f8fafc surfaces, #2563eb blue accent
- Dark theme: #0f1117 bg, #1e2130 surfaces, #4f8ef7 accent
- Toggle button in top navbar persisted to session_state

### 2. Top Navigation Bar (HTML/CSS overlay)
- SalesIQ logo + wordmark left-aligned
- Page title center
- Theme toggle + Refresh + Status dot right-aligned

### 3. Sidebar Redesign
- Section headers with dividers
- Navigation with active highlight
- Filter section with card styling
- System health badges

### 4. Premium KPI Cards
- Icon + label + value + trend badge + sparkline-style delta
- Hover lift shadow effect
- Color-coded borders by metric type

### 5. Chart Improvements
- Consistent color palette per theme
- Better titles, legends, tooltips
- Responsive height

### 6. Professional Tables
- Alternating row shading via CSS
- Column header styling

### 7. Empty States
- Friendly icon + headline + instruction text

### 8. Page Headers
- Section hero with gradient background
- Subtitle + breadcrumb

### Files to modify
- `app.py` — complete redesign (frontend only)
- `UI_BACKUP.md` — this file

### Files NOT to modify
- main.py, services.py, backend_utils.py, data_store.py
- analytics/*, forecasting/*, utils/*
- data/sample_sales.csv
