"""
SalesIQ — AI Sales Intelligence Platform
Premium SaaS-grade analytics dashboard.
Backend logic is untouched; only UI/UX is redesigned.
"""

import io
import datetime as dt
from typing import List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SalesIQ — AI Sales Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session defaults ──────────────────────────────────────────────────────────
_DEFAULTS = {
    "theme": "dark",          # "light" | "dark"
    "build_log": [],
    "data_loaded": False,
    "total_records": 0,
    "active_errors": 0,
    "completed_fixes": 0,
    "last_fix": "—",
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Theme tokens ──────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "app_bg":        "#0f1117",
        "surface":       "#1e2130",
        "surface2":      "#252840",
        "border":        "#2d3154",
        "text":          "#f0f2f8",
        "text_sub":      "#8b92b8",
        "accent":        "#4f8ef7",
        "accent2":       "#7c6eff",
        "green":         "#22c55e",
        "red":           "#ef4444",
        "amber":         "#f59e0b",
        "chart_bg":      "#1e2130",
        "chart_paper":   "#1e2130",
        "chart_font":    "#f0f2f8",
        "chart_grid":    "#2d3154",
        "row_alt":       "rgba(79,142,247,0.05)",
        "card_shadow":   "0 4px 24px rgba(0,0,0,0.4)",
        "nav_bg":        "#13162b",
    },
    "light": {
        "app_bg":        "#f8fafc",
        "surface":       "#ffffff",
        "surface2":      "#f1f5f9",
        "border":        "#e2e8f0",
        "text":          "#0f172a",
        "text_sub":      "#64748b",
        "accent":        "#2563eb",
        "accent2":       "#7c3aed",
        "green":         "#16a34a",
        "red":           "#dc2626",
        "amber":         "#d97706",
        "chart_bg":      "#ffffff",
        "chart_paper":   "#ffffff",
        "chart_font":    "#0f172a",
        "chart_grid":    "#e2e8f0",
        "row_alt":       "rgba(37,99,235,0.04)",
        "card_shadow":   "0 2px 12px rgba(0,0,0,0.08)",
        "nav_bg":        "#1e40af",
    },
}

def T() -> dict:
    return THEMES[st.session_state["theme"]]

# ── CSS injection ─────────────────────────────────────────────────────────────
def inject_css():
    t = T()
    st.markdown(f"""
<style>
/* ── Reset & base ── */
*, *::before, *::after {{ box-sizing: border-box; }}

.stApp, body {{
    background-color: {t['app_bg']} !important;
    color: {t['text']} !important;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
}}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, .stDeployButton {{ display: none !important; }}
header[data-testid="stHeader"] {{ background: transparent !important; }}
.block-container {{ padding: 0 2rem 2rem 2rem !important; max-width: 1400px !important; }}

/* ── Top navbar ── */
.siq-navbar {{
    background: linear-gradient(135deg, {t['nav_bg']} 0%, {t['accent2']} 100%);
    padding: 0.75rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    margin: 0 -2rem 1.5rem -2rem;
    box-shadow: 0 2px 20px rgba(0,0,0,0.3);
    position: sticky; top: 0; z-index: 999;
}}
.siq-logo {{ display: flex; align-items: center; gap: 0.6rem; }}
.siq-logo-icon {{ font-size: 1.6rem; }}
.siq-logo-text {{ font-size: 1.25rem; font-weight: 700; color: #fff;
    letter-spacing: -0.02em; }}
.siq-logo-badge {{ background: rgba(255,255,255,0.2); color: #fff;
    font-size: 0.65rem; font-weight: 600; padding: 2px 7px;
    border-radius: 99px; letter-spacing: 0.05em; }}
.siq-nav-right {{ display: flex; align-items: center; gap: 1rem; }}
.siq-status-dot {{ width: 8px; height: 8px; border-radius: 50%;
    display: inline-block; margin-right: 4px; }}
.siq-status-online  {{ background: #22c55e; box-shadow: 0 0 6px #22c55e; }}
.siq-status-offline {{ background: #ef4444; box-shadow: 0 0 6px #ef4444; }}
.siq-nav-pill {{
    background: rgba(255,255,255,0.12); color: #fff;
    padding: 4px 14px; border-radius: 99px; font-size: 0.82rem;
    font-weight: 500; cursor: pointer; border: 1px solid rgba(255,255,255,0.2);
}}
.siq-datetime {{ color: rgba(255,255,255,0.75); font-size: 0.8rem; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {t['surface']} !important;
    border-right: 1px solid {t['border']} !important;
}}
[data-testid="stSidebar"] * {{ color: {t['text']} !important; }}
.siq-sidebar-logo {{
    background: linear-gradient(135deg, {t['accent']} 0%, {t['accent2']} 100%);
    color: #fff !important; font-weight: 700; font-size: 1.1rem;
    padding: 12px 16px; border-radius: 10px; margin-bottom: 1rem;
    text-align: center; letter-spacing: -0.01em;
}}
.siq-nav-item {{
    padding: 8px 12px; border-radius: 8px; margin-bottom: 3px;
    font-size: 0.88rem; font-weight: 500; cursor: pointer;
    transition: all 0.15s;
}}
.siq-nav-item:hover {{ background: {t['surface2']}; }}
.siq-section-label {{
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: {t['text_sub']} !important;
    padding: 8px 0 4px 4px; margin-top: 8px;
}}
.siq-divider {{ border: none; border-top: 1px solid {t['border']}; margin: 12px 0; }}

/* ── Health badges ── */
.siq-badge {{
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 10px; border-radius: 99px; font-size: 0.75rem;
    font-weight: 600; margin: 3px 0;
}}
.siq-badge-green {{ background: rgba(34,197,94,0.15); color: {t['green']}; }}
.siq-badge-red   {{ background: rgba(239,68,68,0.15);  color: {t['red']};   }}
.siq-badge-amber {{ background: rgba(245,158,11,0.15); color: {t['amber']}; }}
.siq-badge-blue  {{ background: rgba(79,142,247,0.15); color: {t['accent']}; }}

/* ── KPI cards ── */
.kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }}
.kpi-card {{
    background: {t['surface']}; border: 1px solid {t['border']};
    border-radius: 14px; padding: 1.25rem 1.5rem;
    box-shadow: {t['card_shadow']};
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative; overflow: hidden;
}}
.kpi-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 32px rgba(0,0,0,0.25); }}
.kpi-card::before {{
    content: ''; position: absolute; top: 0; left: 0;
    width: 4px; height: 100%; border-radius: 14px 0 0 14px;
}}
.kpi-card.blue::before   {{ background: {t['accent']}; }}
.kpi-card.green::before  {{ background: {t['green']}; }}
.kpi-card.purple::before {{ background: {t['accent2']}; }}
.kpi-card.amber::before  {{ background: {t['amber']}; }}
.kpi-icon {{ font-size: 1.6rem; margin-bottom: 0.4rem; }}
.kpi-label {{ font-size: 0.75rem; font-weight: 600; letter-spacing: 0.06em;
    text-transform: uppercase; color: {t['text_sub']}; margin-bottom: 0.25rem; }}
.kpi-value {{ font-size: 1.75rem; font-weight: 700; color: {t['text']};
    letter-spacing: -0.03em; line-height: 1; }}
.kpi-trend {{ display: flex; align-items: center; gap: 4px; margin-top: 6px;
    font-size: 0.78rem; font-weight: 600; }}
.kpi-trend.up   {{ color: {t['green']}; }}
.kpi-trend.down {{ color: {t['red']}; }}
.kpi-trend.flat {{ color: {t['text_sub']}; }}

/* ── Section headers ── */
.siq-section {{
    background: linear-gradient(90deg, {t['surface']} 0%, {t['surface2']} 100%);
    border: 1px solid {t['border']}; border-radius: 12px;
    padding: 1rem 1.5rem; margin-bottom: 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
}}
.siq-section-title {{ font-size: 1.1rem; font-weight: 700; color: {t['text']}; }}
.siq-section-sub   {{ font-size: 0.82rem; color: {t['text_sub']}; margin-top: 2px; }}

/* ── Chart containers ── */
.chart-card {{
    background: {t['surface']}; border: 1px solid {t['border']};
    border-radius: 14px; padding: 1rem;
    box-shadow: {t['card_shadow']}; margin-bottom: 1rem;
}}

/* ── Data tables ── */
.siq-table-wrap {{ border-radius: 12px; overflow: hidden;
    border: 1px solid {t['border']}; background: {t['surface']}; }}
[data-testid="stDataFrame"] {{ border: none !important; }}
[data-testid="stDataFrame"] th {{
    background: {t['surface2']} !important; color: {t['text_sub']} !important;
    font-weight: 700 !important; font-size: 0.78rem !important;
    text-transform: uppercase !important; letter-spacing: 0.05em !important;
    padding: 10px 14px !important;
}}

/* ── Buttons ── */
.stButton > button {{
    background: linear-gradient(135deg, {t['accent']} 0%, {t['accent2']} 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important; font-size: 0.88rem !important;
    box-shadow: 0 2px 12px rgba(79,142,247,0.35) !important;
    transition: all 0.2s !important;
}}
.stButton > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(79,142,247,0.5) !important;
}}

/* ── Inputs / selects ── */
.stTextInput input, .stSelectbox select, .stMultiSelect div,
[data-testid="stDateInput"] input {{
    background: {t['surface2']} !important; color: {t['text']} !important;
    border: 1px solid {t['border']} !important; border-radius: 8px !important;
}}
.stSlider [data-testid="stSlider"] {{ accent-color: {t['accent']}; }}

/* ── Alerts ── */
.stAlert {{ border-radius: 10px !important; }}

/* ── Expanders ── */
[data-testid="stExpander"] {{
    background: {t['surface']} !important; border: 1px solid {t['border']} !important;
    border-radius: 12px !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {t['surface2']} !important; border-radius: 10px !important;
    padding: 4px !important;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 7px !important; font-weight: 600 !important;
    font-size: 0.85rem !important;
}}
.stTabs [aria-selected="true"] {{
    background: {t['accent']} !important; color: #fff !important;
}}

/* ── st.metric override ── */
[data-testid="metric-container"] {{
    background: {t['surface']}; border: 1px solid {t['border']};
    border-radius: 12px; padding: 1rem !important;
    box-shadow: {t['card_shadow']};
}}
[data-testid="stMetricLabel"] {{ color: {t['text_sub']} !important; font-size: 0.8rem !important; }}
[data-testid="stMetricValue"] {{ color: {t['text']} !important; font-size: 1.5rem !important; }}

/* ── Empty state ── */
.siq-empty {{
    text-align: center; padding: 3rem 2rem;
    background: {t['surface']}; border: 2px dashed {t['border']};
    border-radius: 16px; color: {t['text_sub']};
}}
.siq-empty-icon {{ font-size: 3rem; margin-bottom: 0.75rem; }}
.siq-empty-title {{ font-size: 1.1rem; font-weight: 700; color: {t['text']}; margin-bottom: 0.4rem; }}
.siq-empty-body  {{ font-size: 0.88rem; line-height: 1.6; }}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {{
    background: {t['surface2']} !important; border: 2px dashed {t['border']} !important;
    border-radius: 12px !important;
}}

/* ── Progress bar ── */
.stProgress > div > div {{ background: {t['accent']} !important; border-radius: 99px; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {t['surface']}; }}
::-webkit-scrollbar-thumb {{ background: {t['border']}; border-radius: 99px; }}
</style>
""", unsafe_allow_html=True)

# ── Utility functions (unchanged logic) ──────────────────────────────────────
def log_event(action: str, result: str, status: str = "OK"):
    ts = dt.datetime.now().strftime("%H:%M:%S")
    st.session_state["build_log"].append(
        {"ts": ts, "action": action, "result": result, "status": status}
    )

def safe_get(url: str, params: dict = None, timeout: int = 10) -> Tuple[dict, Optional[str]]:
    try:
        r = requests.get(url, params=params or {}, timeout=timeout)
        if r.status_code != 200:
            return {}, f"HTTP {r.status_code}: {r.text[:120]}"
        return r.json(), None
    except requests.ConnectionError:
        return {}, "Connection refused — is the backend running?"
    except requests.Timeout:
        return {}, "Request timed out"
    except Exception as exc:
        return {}, str(exc)

def safe_post_file(url: str, file_bytes: bytes, filename: str) -> Tuple[dict, Optional[str]]:
    try:
        files = {"file": (filename, io.BytesIO(file_bytes), "text/csv")}
        r = requests.post(url, files=files, timeout=30)
        if r.status_code != 200:
            return {}, f"HTTP {r.status_code}: {r.text[:120]}"
        return r.json(), None
    except Exception as exc:
        return {}, str(exc)

def safe_get_bytes(url: str, params: dict = None, timeout: int = 30) -> Tuple[bytes, Optional[str]]:
    try:
        r = requests.get(url, params=params or {}, timeout=timeout)
        if r.status_code != 200:
            return b"", f"HTTP {r.status_code}: {r.text[:120]}"
        return r.content, None
    except Exception as exc:
        return b"", str(exc)

def to_comma(values: Optional[List[str]]) -> Optional[str]:
    return ",".join(values) if values else None

def check_health(api_url: str) -> dict:
    result = {"backend_online": False, "data_loaded": False, "total_records": 0}
    try:
        r = requests.get(f"{api_url}/health", timeout=4)
        if r.status_code == 200:
            d = r.json()
            result["backend_online"]  = True
            result["data_loaded"]     = d.get("data_loaded", False)
            # /health now returns record_count directly — no extra HTTP call needed
            result["total_records"]   = d.get("record_count", 0)
    except Exception:
        pass
    return result

def chart_cfg(height: int = 340) -> dict:
    t = T()
    return dict(
        plot_bgcolor=t["chart_bg"], paper_bgcolor=t["chart_paper"],
        font=dict(color=t["chart_font"], family="Inter, Segoe UI, sans-serif", size=12),
        margin=dict(l=16, r=16, t=40, b=16),
        height=height,
        xaxis=dict(gridcolor=t["chart_grid"], showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=t["chart_grid"], showgrid=True, zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        hoverlabel=dict(bgcolor=t["surface2"], font_size=12),
    )

ACCENT_PALETTE = ["#4f8ef7","#7c6eff","#22c55e","#f59e0b","#ef4444","#06b6d4","#ec4899"]

# ── UI components ─────────────────────────────────────────────────────────────
def navbar(health: dict, page: str):
    be_dot   = "siq-status-online" if health["backend_online"] else "siq-status-offline"
    be_label = "API Online" if health["backend_online"] else "API Offline"
    now      = dt.datetime.now().strftime("%b %d, %Y  %H:%M")

    st.markdown(f"""
<div class="siq-navbar">
  <div class="siq-logo">
    <span class="siq-logo-icon">📊</span>
    <span class="siq-logo-text">SalesIQ</span>
    <span class="siq-logo-badge">BETA</span>
  </div>
  <div style="color:rgba(255,255,255,0.85);font-size:0.9rem;font-weight:600;">
    {page}
  </div>
  <div class="siq-nav-right">
    <span class="siq-datetime">{now}</span>
    <span class="siq-nav-pill">
      <span class="siq-status-dot {be_dot}"></span>{be_label}
    </span>
  </div>
</div>
""", unsafe_allow_html=True)
    # NOTE: Theme toggle is in the sidebar — NOT here.
    # Putting st.button + st.rerun() inside st.columns() inside navbar()
    # causes Streamlit to restart mid-render and blank the entire page.


def section_header(icon: str, title: str, subtitle: str = ""):
    t = T()
    sub_html = f'<div class="siq-section-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
<div class="siq-section">
  <div>
    <div class="siq-section-title">{icon}&nbsp; {title}</div>
    {sub_html}
  </div>
</div>
""", unsafe_allow_html=True)


def kpi_card(icon: str, label: str, value: str, trend: str = "",
             trend_dir: str = "flat", color: str = "blue"):
    trend_html = ""
    if trend:
        arrow = "▲" if trend_dir == "up" else ("▼" if trend_dir == "down" else "—")
        trend_html = f'<div class="kpi-trend {trend_dir}">{arrow} {trend}</div>'
    st.markdown(f"""
<div class="kpi-card {color}">
  <div class="kpi-icon">{icon}</div>
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
  {trend_html}
</div>
""", unsafe_allow_html=True)


def empty_state(icon: str, title: str, body: str):
    st.markdown(f"""
<div class="siq-empty">
  <div class="siq-empty-icon">{icon}</div>
  <div class="siq-empty-title">{title}</div>
  <div class="siq-empty-body">{body}</div>
</div>
""", unsafe_allow_html=True)


def badge(text: str, kind: str = "blue") -> str:
    return f'<span class="siq-badge siq-badge-{kind}">{text}</span>'

# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar(api_url: str, health: dict) -> Tuple[dict, str]:
    t = T()

    st.sidebar.markdown(
        '<div class="siq-sidebar-logo">📊 SalesIQ Analytics</div>',
        unsafe_allow_html=True,
    )

    # Navigation
    st.sidebar.markdown('<div class="siq-section-label">Navigation</div>', unsafe_allow_html=True)
    pages = [
        ("📊", "Dashboard"),
        ("📈", "Sales Analytics"),
        ("👥", "Customer Intelligence"),
        ("💰", "Profit Analysis"),
        ("🔮", "Forecasting"),
        ("🔍", "Filter & Explore"),
        ("📄", "Reports"),
        ("📚", "API Docs"),
    ]
    page_labels = [f"{ico}  {name}" for ico, name in pages]
    selected = st.sidebar.radio(
        "nav", page_labels, label_visibility="collapsed",
        key="nav_radio"
    )

    st.sidebar.markdown('<hr class="siq-divider">', unsafe_allow_html=True)

    # Filters
    st.sidebar.markdown('<div class="siq-section-label">Filters</div>', unsafe_allow_html=True)

    # ── Cache product/region lists — only reload when data status changes ──────
    # This prevents a blocking HTTP call on EVERY Streamlit rerun (including the
    # rerun triggered right after CSV upload).
    cache_key_products = "sidebar_products"
    cache_key_regions  = "sidebar_regions"
    cache_key_loaded   = "sidebar_data_loaded_snapshot"

    data_status_changed = (
        st.session_state.get(cache_key_loaded) != health["data_loaded"]
    )
    if data_status_changed or cache_key_products not in st.session_state:
        products, regions = [], []
        if health["backend_online"] and health["data_loaded"]:
            fd, _ = safe_get(f"{api_url}/filter-data", {"limit": 500})
            if fd:
                inner = fd.get("data", fd)
                rows  = inner.get("preview_rows", [])
                if rows:
                    df_p = pd.DataFrame(rows)
                    if "Product" in df_p.columns:
                        products = sorted(df_p["Product"].dropna().unique().tolist())
                    if "Region" in df_p.columns:
                        regions  = sorted(df_p["Region"].dropna().unique().tolist())
        st.session_state[cache_key_products] = products
        st.session_state[cache_key_regions]  = regions
        st.session_state[cache_key_loaded]   = health["data_loaded"]

    products = st.session_state.get(cache_key_products, [])
    regions  = st.session_state.get(cache_key_regions,  [])

    with st.sidebar.form("filter_form"):
        start_date   = st.date_input("Start date", value=None)
        end_date     = st.date_input("End date",   value=None)
        sel_products = st.multiselect("Products",  options=products, placeholder="All products")
        sel_regions  = st.multiselect("Regions",   options=regions,  placeholder="All regions")
        st.form_submit_button("🔍  Apply Filters", use_container_width=True)

    params: dict = {}
    if start_date:  params["start_date"] = start_date.isoformat()
    if end_date:    params["end_date"]   = end_date.isoformat()
    if sel_products: params["product"]  = to_comma(sel_products)
    if sel_regions:  params["region"]   = to_comma(sel_regions)

    # System health
    st.sidebar.markdown('<hr class="siq-divider">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="siq-section-label">System Health</div>', unsafe_allow_html=True)

    be_kind  = "green" if health["backend_online"] else "red"
    be_label = "🟢 Backend Online" if health["backend_online"] else "🔴 Backend Offline"
    dl_kind  = "green" if health["data_loaded"] else "amber"
    dl_label = "🟢 Data Loaded" if health["data_loaded"] else "🟡 No Data"

    st.sidebar.markdown(
        f'{badge(be_label, be_kind)}<br>{badge(dl_label, dl_kind)}',
        unsafe_allow_html=True,
    )
    if health["data_loaded"]:
        st.sidebar.markdown(
            badge(f"📦 {health['total_records']:,} records", "blue"),
            unsafe_allow_html=True,
        )

    st.sidebar.markdown('<hr class="siq-divider">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="siq-section-label">Quick Links</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        f"[🔗 Swagger UI]({api_url}/docs)  &nbsp;|&nbsp;  [❤️ Health]({api_url}/health)",
        unsafe_allow_html=True,
    )
    st.sidebar.caption(f"Refreshed {dt.datetime.now().strftime('%H:%M:%S')}")

    # ── Theme toggle (safe in sidebar — no column context) ──
    st.sidebar.markdown('<hr class="siq-divider">', unsafe_allow_html=True)
    theme_lbl = "☀️  Switch to Light Mode" if st.session_state["theme"] == "dark" else "🌙  Switch to Dark Mode"
    if st.sidebar.button(theme_lbl, key="theme_toggle", use_container_width=True):
        st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"
        st.rerun()

    return params, selected

# ── CSV Upload panel ──────────────────────────────────────────────────────────
def section_upload(api_url: str):
    """
    CSV upload panel.

    BUG FIX — Infinite rerun prevention:
    st.file_uploader keeps the file in widget state across reruns.
    Without a guard, every st.rerun() re-triggers the upload POST call.
    Fix: track the last uploaded filename + size in session_state.
    Only call the backend when the file is NEW (different from last upload).
    Never call st.rerun() after a successful upload — just let Streamlit
    naturally re-render on the next interaction. The session_state flags
    (data_loaded, total_records) are already set, so the UI updates correctly.
    """
    with st.expander(
        "📤  Upload Sales Data" + ("  ✅" if st.session_state["data_loaded"] else "  ← Start here"),
        expanded=not st.session_state["data_loaded"],
    ):
        st.markdown("""
<small style="opacity:0.7">
Accepted columns: <code>Order Date · Product · Category · Region · Customer ID ·
Quantity · Unit Price · Revenue · Cost · Profit</code>
</small>
""", unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Choose a CSV file", type=["csv"], label_visibility="collapsed",
            key="csv_uploader",
        )

        if uploaded is not None:
            # ── Guard: only process when file is genuinely new ──────────────
            file_sig = f"{uploaded.name}_{uploaded.size}"
            already_processed = (
                st.session_state.get("last_uploaded_sig") == file_sig
            )

            if already_processed:
                # File was already uploaded this session — just show confirmation
                rows = st.session_state.get("total_records", "?")
                st.success(
                    f"✅ Data loaded  •  {rows} records available  •  "
                    f"Navigate using the sidebar to explore analytics."
                )
            else:
                # New file — send to backend exactly once
                file_bytes = uploaded.read()
                with st.spinner("Uploading & processing…"):
                    result, err = safe_post_file(
                        f"{api_url}/upload-csv", file_bytes, uploaded.name
                    )

                if err:
                    st.error(f"Upload failed: {err}")
                    log_event("POST /upload-csv", err, "ERR")
                    st.session_state["active_errors"] += 1
                else:
                    msg  = result.get("message", "Upload successful")
                    meta = result.get("metadata", result)
                    rows = meta.get("row_count", "?")
                    cols = meta.get("columns", [])

                    # Persist all state BEFORE any rerun
                    st.session_state["last_uploaded_sig"]  = file_sig
                    st.session_state["data_loaded"]        = True
                    st.session_state["total_records"]      = rows
                    st.session_state["last_fix"]           = "CSV Upload"
                    st.session_state["completed_fixes"]   += 1
                    # Invalidate the sidebar filter cache so it reloads
                    st.session_state.pop("sidebar_data_loaded_snapshot", None)

                    log_event("POST /upload-csv", f"{rows} rows", "OK")

                    st.success(
                        f"✅ {msg}  •  {rows} rows  •  {len(cols)} columns  •  "
                        f"Use the sidebar to navigate."
                    )
                    # No st.rerun() here — session_state is already updated.
                    # Streamlit will rerender naturally on the next interaction.
                    # Calling st.rerun() here caused the infinite upload loop.

# ── Dashboard page ────────────────────────────────────────────────────────────
def page_dashboard(api_url: str, params: dict):
    section_header("📊", "Executive Dashboard",
                   f"Business overview  •  {dt.date.today().strftime('%B %d, %Y')}")

    # ── KPIs ──
    summary, err = safe_get(f"{api_url}/sales-summary", params)
    if err:
        st.error(f"Sales summary error: {err}")
        log_event("GET /sales-summary", err, "ERR")
        summary = {}
    else:
        log_event("GET /sales-summary", "200 OK")

    rev    = summary.get("total_revenue", 0)
    orders = summary.get("total_orders", 0)
    aov    = summary.get("avg_order_value", 0)
    region = summary.get("best_region", "N/A")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("💰", "Total Revenue",    f"${rev:,.0f}",   trend="All time",  color="blue")
    with c2:
        kpi_card("🛒", "Total Orders",     f"{orders:,}",    trend="All time",  color="green")
    with c3:
        kpi_card("📦", "Avg Order Value",  f"${aov:,.2f}",   trend="Per order", color="purple")
    with c4:
        kpi_card("🌍", "Best Region",      region,           color="amber")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row ──
    growth = summary.get("monthly_growth", {})
    fd, _  = safe_get(f"{api_url}/filter-data", {**params, "limit": 500})
    inner  = (fd.get("data", fd) if fd else {})
    rows   = inner.get("preview_rows", []) if inner else []

    c_left, c_right = st.columns([3, 2])

    with c_left:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if rows:
            df_raw = pd.DataFrame(rows)
            df_raw["Date"] = pd.to_datetime(df_raw["Date"], errors="coerce")
            df_raw = df_raw.dropna(subset=["Date"])
            monthly = df_raw.set_index("Date").resample("ME")["Revenue"].sum().reset_index()
            fig = px.area(monthly, x="Date", y="Revenue",
                          title="Revenue Trend — Monthly",
                          color_discrete_sequence=[T()["accent"]])
            fig.update_traces(fill="tozeroy", line_width=2.5)
            fig.update_layout(**chart_cfg(300))
            st.plotly_chart(fig, use_container_width=True)
        else:
            empty_state("📈", "No Revenue Data", "Upload a CSV file to see revenue trends.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if growth:
            df_g = pd.DataFrame({"Month": list(growth.keys()), "Growth": list(growth.values())})
            colors = [T()["green"] if v >= 0 else T()["red"] for v in df_g["Growth"]]
            fig2 = go.Figure(go.Bar(
                x=df_g["Month"], y=df_g["Growth"],
                marker_color=colors,
                text=df_g["Growth"].round(1),
                textposition="outside",
                textfont_size=10,
            ))
            fig2.update_layout(title="MoM Growth %", **chart_cfg(300))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            empty_state("📊", "No Growth Data", "Upload data to see monthly growth.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Regional breakdown ──
    if rows:
        df_r = pd.DataFrame(rows)
        if "Region" in df_r.columns and "Revenue" in df_r.columns:
            rr = df_r.groupby("Region", observed=True)["Revenue"].sum().reset_index()
            c_a, c_b = st.columns(2)
            with c_a:
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                fig3 = px.pie(rr, names="Region", values="Revenue",
                              title="Revenue by Region",
                              color_discrete_sequence=ACCENT_PALETTE)
                fig3.update_traces(textposition="inside", textinfo="percent+label")
                fig3.update_layout(**chart_cfg(280))
                st.plotly_chart(fig3, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with c_b:
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                fig4 = px.bar(rr.sort_values("Revenue"), x="Revenue", y="Region",
                              orientation="h", title="Regional Revenue Comparison",
                              color="Revenue", color_continuous_scale="Blues")
                fig4.update_layout(**chart_cfg(280))
                st.plotly_chart(fig4, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

# ── Sales Analytics page ──────────────────────────────────────────────────────
def page_sales(api_url: str, params: dict):
    section_header("📈", "Sales Analytics", "Top products, revenue distribution & performance")

    data, err = safe_get(f"{api_url}/top-products", {**params, "top_n": 15})
    if err:
        st.error(f"Top products error: {err}");  log_event("GET /top-products", err, "ERR"); return
    log_event("GET /top-products", "200 OK")

    inner    = data.get("data", data)
    products = inner.get("top_products", [])
    if not products:
        empty_state("🏪", "No Products Found",
                    "No product data matches your current filters. Try broadening the date range.")
        return

    df_top = pd.DataFrame(products)

    # Tab layout for charts vs table
    tab1, tab2 = st.tabs(["📊  Charts", "📋  Data Table"])

    with tab1:
        ca, cb = st.columns(2)
        with ca:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = px.bar(df_top.head(10), x="revenue", y="product",
                         orientation="h", title="Top 10 Products by Revenue",
                         color="revenue", color_continuous_scale="Blues",
                         text_auto=".2s")
            fig.update_layout(**chart_cfg(350))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with cb:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig2 = px.pie(df_top.head(10), names="product", values="revenue",
                          title="Revenue Share — Top 10",
                          color_discrete_sequence=ACCENT_PALETTE,
                          hole=0.42)
            fig2.update_traces(textposition="inside", textinfo="percent+label")
            fig2.update_layout(**chart_cfg(350))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="siq-table-wrap">', unsafe_allow_html=True)
        df_display = df_top.copy()
        df_display.columns = [c.title() for c in df_display.columns]
        df_display["Revenue"] = df_display["Revenue"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Customer Intelligence page ────────────────────────────────────────────────
def page_customers(api_url: str, params: dict):
    section_header("👥", "Customer Intelligence", "Segmentation, retention & lifetime value")

    data, err = safe_get(f"{api_url}/customer-analysis", params)
    if err:
        st.error(f"Customer analysis error: {err}"); log_event("GET /customer-analysis", err, "ERR"); return
    log_event("GET /customer-analysis", "200 OK")

    inner = data.get("data", data)
    if inner.get("total_customers", 0) == 0:
        empty_state("👥", "No Customer Data",
                    "No customers found for the selected filters. Try adjusting date or region.")
        return

    total  = inner.get("total_customers", 0)
    new_c  = inner.get("new_customers", 0)
    ret_c  = inner.get("returning_customers", 0)
    avg_cv = inner.get("average_customer_value", 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("👥", "Total Customers",     f"{total:,}",       color="blue")
    with c2: kpi_card("🆕", "New Customers",       f"{new_c:,}",       color="green")
    with c3: kpi_card("🔁", "Returning Customers", f"{ret_c:,}",       color="purple")
    with c4: kpi_card("💵", "Avg Customer Value",  f"${avg_cv:,.2f}",  color="amber")

    st.markdown("<br>", unsafe_allow_html=True)
    segs = inner.get("segments", {})
    top  = inner.get("top_customers", [])

    ca, cb = st.columns(2)
    with ca:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if segs:
            df_seg = pd.DataFrame([
                {"Segment": "High Value",   "Count": segs.get("high_value", 0)},
                {"Segment": "Medium Value", "Count": segs.get("medium_value", 0)},
                {"Segment": "Low Value",    "Count": segs.get("low_value", 0)},
            ])
            fig = px.pie(df_seg, names="Segment", values="Count",
                         title="Customer Value Segments",
                         color_discrete_sequence=[T()["accent"], T()["accent2"], T()["amber"]],
                         hole=0.4)
            fig.update_layout(**chart_cfg(300))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cb:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if top:
            df_top = pd.DataFrame(top)
            fig2 = px.bar(df_top, x="clv", y="customer_id", orientation="h",
                          title="Top Customers by Revenue",
                          color="clv", color_continuous_scale="Purples",
                          text_auto=".2s")
            fig2.update_layout(**chart_cfg(300))
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if top:
        st.subheader("Top Customers")
        st.markdown('<div class="siq-table-wrap">', unsafe_allow_html=True)
        df_t = pd.DataFrame(top).rename(columns={"customer_id": "Customer ID", "clv": "Revenue ($)"})
        df_t["Revenue ($)"] = df_t["Revenue ($)"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df_t, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Profit Analysis page ──────────────────────────────────────────────────────
def page_profit(api_url: str, params: dict):
    section_header("💰", "Profit Analysis", "Margins, losses & product profitability")

    data, err = safe_get(f"{api_url}/profit-analysis", params)
    if err:
        st.error(f"Profit analysis error: {err}"); log_event("GET /profit-analysis", err, "ERR"); return
    log_event("GET /profit-analysis", "200 OK")

    inner      = data.get("data", data)
    total_prf  = inner.get("total_profit", 0)
    profitable = inner.get("profitable_products", [])
    losses     = inner.get("loss_making_products", [])
    margins    = inner.get("product_margins", [])

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("💵", "Total Profit",     f"${total_prf:,.2f}", color="green")
    with c2: kpi_card("✅", "Profitable Items", str(len(profitable)), color="blue")
    with c3: kpi_card("⚠️", "Loss-Making Items",str(len(losses)),    color="amber")

    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb = st.columns(2)

    with ca:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if profitable:
            df_p = pd.DataFrame(profitable)
            fig = px.bar(df_p, x="total_profit", y="product", orientation="h",
                         title="Top Profitable Products",
                         color="total_profit", color_continuous_scale="Greens",
                         text_auto=".2s")
            fig.update_layout(**chart_cfg(320))
            st.plotly_chart(fig, use_container_width=True)
        else:
            empty_state("✅", "All Profitable", "No loss-making products detected.")
        st.markdown('</div>', unsafe_allow_html=True)

    with cb:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if losses:
            df_l = pd.DataFrame(losses)
            fig2 = px.bar(df_l, x="total_profit", y="product", orientation="h",
                          title="Loss-Making Products",
                          color="total_profit", color_continuous_scale="Reds")
            fig2.update_layout(**chart_cfg(320))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            empty_state("🎉", "No Losses", "All products are profitable with current filters.")
        st.markdown('</div>', unsafe_allow_html=True)

    if margins:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        df_m = pd.DataFrame(margins)
        colors = [T()["green"] if v >= 20 else (T()["amber"] if v >= 0 else T()["red"])
                  for v in df_m["profit_margin_pct"]]
        fig3 = go.Figure(go.Bar(
            x=df_m["product"], y=df_m["profit_margin_pct"],
            marker_color=colors,
            text=df_m["profit_margin_pct"].round(1),
            textposition="outside",
        ))
        fig3.update_layout(title="Profit Margin % by Product", **chart_cfg(300))
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Forecasting page ──────────────────────────────────────────────────────────
def page_forecast(api_url: str, params: dict):
    section_header("🔮", "AI Sales Forecasting", "Linear regression model — revenue projection")

    days = st.slider("Forecast horizon (days)", 7, 90, 30, key="forecast_days")

    data, err = safe_get(f"{api_url}/forecast", {**params, "days": days})
    if err:
        st.error(f"Forecast error: {err}"); log_event("GET /forecast", err, "ERR"); return
    log_event("GET /forecast", "200 OK")

    inner         = data.get("data", data)
    forecast_list = inner.get("forecast", [])

    if not forecast_list:
        empty_state("🔮", "Insufficient Data for Forecasting",
                    "Upload at least 2 rows of historical data across different dates to generate a forecast.")
        return

    df_f  = pd.DataFrame(forecast_list)
    df_f["date"] = pd.to_datetime(df_f["date"])
    total_f = df_f["predicted_revenue"].sum()
    avg_d   = df_f["predicted_revenue"].mean()
    peak_d  = df_f.loc[df_f["predicted_revenue"].idxmax(), "date"].strftime("%b %d")

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("💰", f"{days}d Forecast Total", f"${total_f:,.0f}", color="blue")
    with c2: kpi_card("📅", "Avg Daily Revenue",       f"${avg_d:,.2f}",  color="green")
    with c3: kpi_card("📈", "Peak Day",                peak_d,            color="purple")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_f["date"], y=df_f["predicted_revenue"],
        mode="lines+markers", name="Forecast",
        line=dict(color=T()["accent"], width=2.5),
        marker=dict(size=5, color=T()["accent"]),
        fill="tozeroy",
        fillcolor=f"rgba(79,142,247,0.1)",
    ))
    # Confidence band (±15% visual)
    fig.add_trace(go.Scatter(
        x=pd.concat([df_f["date"], df_f["date"][::-1]]),
        y=pd.concat([df_f["predicted_revenue"] * 1.15,
                     df_f["predicted_revenue"][::-1] * 0.85]),
        fill="toself", fillcolor="rgba(79,142,247,0.06)",
        line=dict(width=0), showlegend=False, name="Confidence band",
    ))
    fig.update_layout(title=f"{days}-Day Revenue Forecast (Linear Regression)", **chart_cfg(360))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋  Forecast Table", "📊  Distribution"])
    with tab1:
        st.markdown('<div class="siq-table-wrap">', unsafe_allow_html=True)
        df_show = df_f.copy()
        df_show["Date"] = df_show["date"].dt.strftime("%Y-%m-%d")
        df_show["Predicted Revenue"] = df_show["predicted_revenue"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df_show[["Date","Predicted Revenue"]], use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab2:
        fig_hist = px.histogram(df_f, x="predicted_revenue", nbins=15,
                                title="Forecast Revenue Distribution",
                                color_discrete_sequence=[T()["accent2"]])
        fig_hist.update_layout(**chart_cfg(260))
        st.plotly_chart(fig_hist, use_container_width=True)

# ── Filter & Explore page ─────────────────────────────────────────────────────
def page_filter_data(api_url: str, params: dict):
    section_header("🔍", "Filter & Explore", "Browse, search and analyse raw sales records")

    limit = st.slider("Row limit", 10, 500, 100, key="explore_limit")
    data, err = safe_get(f"{api_url}/filter-data", {**params, "limit": limit})
    if err:
        st.error(f"Filter error: {err}"); log_event("GET /filter-data", err, "ERR"); return
    log_event("GET /filter-data", "200 OK")

    inner = data.get("data", data)
    rows  = inner.get("preview_rows", [])
    total = inner.get("row_count", 0)

    c1, c2 = st.columns([3, 1])
    c1.info(f"Showing **{len(rows)}** of **{total:,}** total records")
    if total == 0:
        empty_state("🔍", "No Records Found",
                    "No data matches the selected filters. Try clearing the date or product filters.")
        return

    df = pd.DataFrame(rows)

    # ── Quick visual ──
    if "Revenue" in df.columns and "Region" in df.columns:
        ca, cb = st.columns(2)
        with ca:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            rr = df.groupby("Region", observed=True)["Revenue"].sum().reset_index()
            fig = px.pie(rr, names="Region", values="Revenue",
                         title="Revenue by Region (filtered)",
                         color_discrete_sequence=ACCENT_PALETTE, hole=0.38)
            fig.update_layout(**chart_cfg(260))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with cb:
            if "Product" in df.columns:
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                pp = df.groupby("Product", observed=True)["Revenue"].sum().nlargest(8).reset_index()
                fig2 = px.bar(pp, x="Revenue", y="Product", orientation="h",
                              title="Top Products (filtered)",
                              color="Revenue", color_continuous_scale="Blues",
                              text_auto=".2s")
                fig2.update_layout(**chart_cfg(260))
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # ── Data table ──
    st.markdown('<div class="siq-table-wrap">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── Reports page ──────────────────────────────────────────────────────────────
def page_reports(api_url: str, params: dict):
    section_header("📄", "Reports & Export", "Download filtered data as CSV")

    t = T()
    st.markdown(f"""
<div style="background:{t['surface']};border:1px solid {t['border']};border-radius:14px;
     padding:2rem;text-align:center;margin-bottom:1.5rem;">
  <div style="font-size:2.5rem;margin-bottom:0.5rem;">📥</div>
  <div style="font-size:1.1rem;font-weight:700;color:{t['text']};">Export Sales Report</div>
  <div style="color:{t['text_sub']};font-size:0.88rem;margin-top:4px;margin-bottom:1rem;">
    Download the currently filtered dataset as a CSV file
  </div>
</div>
""", unsafe_allow_html=True)

    col, _ = st.columns([2, 3])
    with col:
        if st.button("📥  Generate CSV Report", use_container_width=True):
            with st.spinner("Generating report…"):
                csv_bytes, err = safe_get_bytes(f"{api_url}/download-report", params)
            if err:
                st.error(f"Download failed: {err}")
                log_event("GET /download-report", err, "ERR")
            else:
                log_event("GET /download-report", "CSV ready")
                st.download_button(
                    label="💾  Save CSV",
                    data=csv_bytes,
                    file_name=f"SalesIQ_report_{dt.date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
                st.success("✅ Report ready — click Save CSV above to download.")


# ── API Docs page ─────────────────────────────────────────────────────────────
def page_api_docs(api_url: str):
    section_header("📚", "API Documentation", f"Interactive docs at {api_url}/docs")

    t = T()
    st.markdown(f"""
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload-csv` | Upload sales data CSV |
| `GET`  | `/sales-summary` | KPI totals + monthly growth |
| `GET`  | `/top-products` | Top N products by revenue |
| `GET`  | `/customer-analysis` | Segments & customer value |
| `GET`  | `/profit-analysis` | Profit margins & losses |
| `GET`  | `/forecast` | ML revenue forecast |
| `GET`  | `/filter-data` | Paginated filtered records |
| `GET`  | `/download-report` | Export as CSV |
| `GET`  | `/health` | Backend health status |

**🔗 [Swagger UI — {api_url}/docs]({api_url}/docs)** &nbsp;|&nbsp;
**📖 [ReDoc — {api_url}/redoc]({api_url}/redoc)**
""")

    st.subheader("Live Endpoint Status")
    endpoints = ["/health", "/", "/sales-summary", "/top-products",
                 "/customer-analysis", "/profit-analysis", "/forecast", "/filter-data"]
    rows = []
    for ep in endpoints:
        try:
            r = requests.get(f"{api_url}{ep}", timeout=5)
            rows.append({"Endpoint": ep, "Code": r.status_code,
                         "Status": "✅ OK" if r.status_code == 200 else "⚠️ Error"})
        except Exception as exc:
            rows.append({"Endpoint": ep, "Code": "—", "Status": f"❌ {str(exc)[:40]}"})

    st.markdown('<div class="siq-table-wrap">', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── Build Progress Log panel ──────────────────────────────────────────────────
def panel_build_log():
    t = T()
    with st.expander("📋  Activity Log", expanded=False):
        logs = st.session_state["build_log"]
        if not logs:
            st.caption("No API activity yet this session.")
            return
        for entry in reversed(logs[-60:]):
            icon = "✅" if entry["status"] == "OK" else "❌"
            st.markdown(
                f"`{entry['ts']}` {icon} **{entry['action']}** — {entry['result']}",
                unsafe_allow_html=True,
            )


# ── Developer / Status footer ─────────────────────────────────────────────────
def panel_dev_status(page: str, health: dict):
    t = T()
    done  = st.session_state["completed_fixes"]
    errs  = st.session_state["active_errors"]
    total = 11
    pct   = min(int(done / total * 100), 100)

    with st.expander("🛠️  System Status", expanded=False):
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Current Page",  page.split("  ")[-1] if "  " in page else page[:15])
        c2.metric("Last Action",   st.session_state["last_fix"])
        c3.metric("Active Errors", errs)
        c4.metric("Tasks Done",    done)
        c5.metric("Completion",    f"{pct}%")
        st.progress(pct / 100)
        be = "✅ Online" if health["backend_online"] else "❌ Offline"
        dl = "✅ Loaded" if health["data_loaded"]    else "⚠️ None"
        st.markdown(
            f"**Backend:** {be} &nbsp;|&nbsp; "
            f"**Data:** {dl} &nbsp;|&nbsp; "
            f"**Records:** {health.get('total_records', 0):,} &nbsp;|&nbsp; "
            f"**Theme:** {st.session_state['theme'].title()}",
            unsafe_allow_html=True,
        )


# ── Main entrypoint ───────────────────────────────────────────────────────────
def main():
    # ── Inject CSS first (theme-aware) ──
    inject_css()

    # ── Sidebar: API URL (above everything else) ──
    api_url = st.sidebar.text_input(
        "Backend URL", value="http://127.0.0.1:8000", key="api_url_input"
    ).rstrip("/")

    # ── Health check ──
    health = check_health(api_url)

    # Sync data_loaded from backend health
    if health["data_loaded"] and not st.session_state["data_loaded"]:
        st.session_state["data_loaded"]   = True
        st.session_state["total_records"] = health["total_records"]

    # ── Sidebar (nav + filters + health) ──
    params, selected_page = render_sidebar(api_url, health)

    # ── Top navbar ──
    navbar(health, selected_page.replace("📊  ", "").replace("📈  ", "")
           .replace("👥  ", "").replace("💰  ", "").replace("🔮  ", "")
           .replace("🔍  ", "").replace("📄  ", "").replace("📚  ", ""))

    # ── Backend offline guard ──
    if not health["backend_online"]:
        st.error(
            "❌  **Backend is offline.**  "
            "Start it with:  `python -m uvicorn main:app --host 127.0.0.1 --port 8000`"
        )
        st.info("Once the backend is running, refresh this page.")
        panel_dev_status(selected_page, health)
        panel_build_log()
        return

    # ── No data warning ──
    if not health["data_loaded"]:
        st.warning("⚠️  No sales data loaded. Upload a CSV file to begin analysis.")

    # ── CSV upload (always visible) ──
    section_upload(api_url)

    # ── If no data yet, don't render page content — avoids blank/error states ──
    if not health["data_loaded"] and not st.session_state.get("data_loaded"):
        st.markdown("""
<div style="text-align:center;padding:3rem 1rem;">
  <div style="font-size:3.5rem;margin-bottom:1rem;">📂</div>
  <div style="font-size:1.2rem;font-weight:700;margin-bottom:0.5rem;">
    No Sales Data Loaded
  </div>
  <div style="opacity:0.6;font-size:0.9rem;max-width:400px;margin:0 auto;">
    Upload a CSV file using the panel above, then use the sidebar
    navigation to explore your analytics dashboard.
  </div>
</div>
""", unsafe_allow_html=True)
        panel_dev_status(selected_page, health)
        panel_build_log()
        return

    # ── Route to selected page ──
    page_map = {
        "📊  Dashboard":                page_dashboard,
        "📈  Sales Analytics":          page_sales,
        "👥  Customer Intelligence":    page_customers,
        "💰  Profit Analysis":          page_profit,
        "🔮  Forecasting":              page_forecast,
        "🔍  Filter & Explore":         page_filter_data,
        "📄  Reports":                  page_reports,
    }

    if selected_page in page_map:
        page_map[selected_page](api_url, params)
    elif "API Docs" in selected_page:
        page_api_docs(api_url)
    else:
        # Exact match failed — default to Dashboard (safe fallback)
        page_dashboard(api_url, params)

    # ── Status footer ──
    st.markdown("<br>", unsafe_allow_html=True)
    panel_dev_status(selected_page, health)
    panel_build_log()


if __name__ == "__main__":
    main()
