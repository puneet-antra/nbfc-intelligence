"""
NBFC Intelligence — Streamlit app
Run: streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import yfinance as yf
import numpy as np
import json
from datetime import datetime
from PIL import Image, ImageDraw

def _make_favicon():
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, 63, 63], radius=12, fill=(20, 72, 53, 255))
    light = (215, 244, 233, 255)   # #D7F4E9
    white = (255, 255, 255, 255)
    draw.rectangle([11, 40, 21, 50], fill=light)   # short bar
    draw.rectangle([26, 30, 36, 50], fill=light)   # medium bar
    draw.rectangle([41, 16, 51, 50], fill=white)   # tall bar (accent)
    return img

st.set_page_config(
    page_title="NBFC Intelligence",
    page_icon=_make_favicon(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Authentication ────────────────────────────────────────────────────────────
_ALLOWED_DOMAIN = "@moneyview.in"
_AUTH_ENABLED = hasattr(st, "user") and hasattr(st.user, "is_logged_in")

if _AUTH_ENABLED:
    if not st.user.is_logged_in:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    min-height:70vh;gap:1.2rem;font-family:'Inter',sans-serif;">
            <div style="font-size:2rem;font-weight:800;color:#144835;letter-spacing:-0.03em;">
                NBFC Intelligence
            </div>
            <div style="font-size:0.95rem;color:#73757A;">
                Restricted to MoneyView employees
            </div>
        </div>
        """, unsafe_allow_html=True)
        col = st.columns([1, 0.4, 1])[1]
        with col:
            if st.button("🔐  Sign in with Google", use_container_width=True, type="primary"):
                st.login("google")
        st.stop()

    _user_email = (st.user.email or "").lower()
    if not _user_email.endswith(_ALLOWED_DOMAIN):
        st.error(f"Access denied — only **{_ALLOWED_DOMAIN}** accounts are permitted.")
        if st.button("Sign out"):
            st.logout()
        st.stop()
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #F6F6F6 !important;
}

/* ── Remove default Streamlit padding ── */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    max-width: 1360px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* ── Page title (h1 fallback) ── */
h1 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 2.0rem !important;
    letter-spacing: -0.03em !important;
    color: #28292D !important;
    line-height: 1.1 !important;
    margin-bottom: 0 !important;
}

/* ── Metric values ── */
[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    color: #28292D !important;
    opacity: 1 !important;
    font-weight: 700 !important;
    font-size: 1.4rem !important;
    letter-spacing: -0.02em !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    color: #73757A !important;
    opacity: 1 !important;
    font-weight: 500 !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    white-space: normal !important;
    overflow: visible !important;
    line-height: 1.5 !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    opacity: 1 !important;
}

/* ── Metric card animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #ffffff !important;
    border: 1px solid #EAEAEA !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.4rem 1.1rem !important;
    box-shadow: 0px 2px 8px 0px rgba(16, 16, 18, 0.08) !important;
    transition: box-shadow 0.25s ease, transform 0.25s ease !important;
    position: relative !important;
    overflow: hidden !important;
    animation: fadeInUp 0.4s ease both !important;
}
[data-testid="metric-container"]::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important; left: 0 !important; right: 0 !important;
    height: 3px !important;
    background: #144835 !important;
    border-radius: 16px 16px 0 0 !important;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0px 4px 16px 0px rgba(16, 16, 18, 0.12) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stColumns"] > div:nth-child(1) [data-testid="metric-container"] { animation-delay: 0.05s !important; }
[data-testid="stColumns"] > div:nth-child(2) [data-testid="metric-container"] { animation-delay: 0.10s !important; }
[data-testid="stColumns"] > div:nth-child(3) [data-testid="metric-container"] { animation-delay: 0.15s !important; }
[data-testid="stColumns"] > div:nth-child(4) [data-testid="metric-container"] { animation-delay: 0.20s !important; }
[data-testid="stColumns"] > div:nth-child(5) [data-testid="metric-container"] { animation-delay: 0.25s !important; }

/* ── Section headers ── */
.section-header {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    color: #28292D;
    margin: 2.6rem 0 1.2rem 0;
    padding: 0.45rem 0.9rem 0.45rem 0.9rem;
    background: #D7F4E9;
    border-left: 3px solid #144835;
    border-radius: 0 4px 4px 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    line-height: 1.2;
}

/* ── Chart card wrapper ── */
[data-testid="stPlotlyChart"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin-bottom: 1.2rem !important;
}

/* ── Caption ── */
[data-testid="stCaptionContainer"] {
    margin-top: -0.6rem !important;
    margin-bottom: 0.8rem !important;
    padding-left: 0.4rem !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #101012 !important;
    border-right: 1px solid #1e1e20 !important;
}
/* Collapse button (‹) inside open sidebar */
[data-testid="stSidebarCollapseButton"] {
    background: #2CA076 !important;
    border-radius: 8px !important;
    border: 1px solid #3dbb8d !important;
    opacity: 1 !important;
    visibility: visible !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    color: #ffffff !important;
    fill: #ffffff !important;
    opacity: 1 !important;
}
[data-testid="stSidebarCollapseButton"]:hover {
    background: #34c98a !important;
    border-color: #5de8a8 !important;
}
/* Expand button (›) on main page when sidebar is collapsed */
[data-testid="stSidebarCollapsedControl"] {
    opacity: 1 !important;
    visibility: visible !important;
    background: #f0f0f0 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebarCollapsedControl"] svg {
    color: #144835 !important;
    fill: #144835 !important;
}
[data-testid="stSidebarCollapsedControl"]:hover {
    background: #D7F4E9 !important;
}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] label {
    font-family: 'Inter', sans-serif !important;
    color: #73757A !important;
    font-size: 0.70rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.70rem !important;
    color: #73757A !important;
}
[data-testid="stSidebar"] hr {
    border-color: #1e1e20 !important;
    margin: 1rem 0 !important;
}
/* ── Selectbox + Multiselect: consistent container ── */
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #1a1a1c !important;
    border-color: #2e3a33 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important;
}
/* Universal catch-all: force all text inside any select to be readable */
[data-testid="stSidebar"] [data-baseweb="select"] *,
[data-testid="stSidebar"] [data-testid="stSelectbox"] * {
    color: #e8eaef !important;
    opacity: 1 !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}
/* Multiselect chips — same style for both RBI Layer and Sector */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: #1e3028 !important;
    border: 1px solid #2e7d54 !important;
    border-radius: 4px !important;
    padding: 2px 8px !important;
    margin: 2px 2px !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] *,
[data-testid="stSidebar"] [data-baseweb="tag"] span {
    color: #e8eaef !important;
    opacity: 1 !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    background: transparent !important;
}
/* Radio — all options */
[data-testid="stSidebar"] [data-baseweb="radio"] label span,
[data-testid="stSidebar"] [data-baseweb="checkbox"] label span {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important;
    color: #8a8c91 !important;
}
/* Radio — selected option: bright white + bold */
[data-testid="stSidebar"] [data-baseweb="radio"] label:has(input:checked) span:last-child {
    color: #ffffff !important;
    font-weight: 700 !important;
}
/* Radio circle fill for selected */
[data-testid="stSidebar"] [data-baseweb="radio"] label:has(input:checked) [data-testid="stRadioCircle"],
[data-testid="stSidebar"] [data-baseweb="radio"] label:has(input:checked) div[class*="radioInner"] {
    background: #217858 !important;
    border-color: #4ade80 !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBar"] {
    color: #73757A !important;
    font-size: 0.70rem !important;
}
[data-testid="stSidebar"] [role="slider"] {
    background: #144835 !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] {
    border-bottom: none !important;
    margin-bottom: 1.5rem !important;
}
[data-baseweb="tab-list"] {
    background: #EDEDEE !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 0 !important;
    border: 1px solid #DCDCDE !important;
    display: flex !important;
    width: 100% !important;
    justify-content: space-evenly !important;
}
[data-baseweb="tab-border"] { display: none !important; }
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.80rem !important;
    color: #73757A !important;
    padding: 0.42rem 1.0rem !important;
    border-radius: 6px !important;
    background: transparent !important;
    border: none !important;
    transition: color 0.15s ease, background 0.15s ease !important;
    letter-spacing: 0.005em !important;
    white-space: nowrap !important;
    justify-content: center !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: #28292D !important;
    background: #D7F4E9 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #ffffff !important;
    font-weight: 600 !important;
    background: #144835 !important;
    box-shadow: 0px 2px 8px rgba(20, 72, 53, 0.3) !important;
    border-bottom: none !important;
}

/* ── Dataframes ── */
[data-testid="stDataFrame"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.80rem !important;
    border-radius: 16px !important;
    border: 1px solid #EAEAEA !important;
    overflow: hidden !important;
    box-shadow: 0px 2px 8px 0px rgba(16, 16, 18, 0.06) !important;
}

/* ── Chart containers ── */
[data-testid="stPlotlyChart"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}
[data-testid="stPlotlyChart"] > div {
    border-radius: 16px !important;
    border: 1px solid #EAEAEA !important;
    overflow: hidden !important;
    box-shadow: 0px 2px 8px 0px rgba(16, 16, 18, 0.08) !important;
    background: #ffffff !important;
    transition: box-shadow 0.2s ease !important;
    width: 100% !important;
}
[data-testid="stPlotlyChart"] > div:hover {
    box-shadow: 0px 4px 16px 0px rgba(16, 16, 18, 0.12) !important;
}

/* ── Badges ── */
.unverified-badge {
    background: #fff5ed; color: #9a3412;
    padding: 2px 9px; border-radius: 4px;
    font-size: 10px; font-weight: 600;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.03em;
    border: 1px solid #fed7aa;
}
.estimated-badge {
    background: #D7F4E9; color: #144835;
    padding: 2px 9px; border-radius: 4px;
    font-size: 10px; font-weight: 600;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.03em;
    border: 1px solid #AFE9D4;
}

/* ── Alerts — hide native Streamlit ones (replaced by note() helper) ── */
[data-testid="stAlert"] { display: none !important; }

/* ── Captions ── */
.stCaption, [data-testid="stCaptionContainer"] {
    font-size: 0.70rem !important;
    font-weight: 400 !important;
    color: #B9BABD !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Selectbox / inputs ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] input {
    border-radius: 4px !important;
    border: 1px solid #DCDCDE !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important;
}
/* Move chevron to left side of selectbox */
[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child {
    flex-direction: row-reverse !important;
    padding-left: 8px !important;
    padding-right: 14px !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child > div:last-child {
    padding-left: 0 !important;
    padding-right: 8px !important;
}


/* ── Tab panel fade-in ── */
@keyframes tabFadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
[data-testid="stTabsContent"] > div[role="tabpanel"] {
    animation: tabFadeIn 0.3s cubic-bezier(0.22, 1, 0.36, 1) both !important;
}

/* ── Deep Dive: filter popover icon button ── */
[data-testid="stPopover"] button,
[data-testid="stPopoverButton"] {
    min-height: 2.45rem !important;
    width: 100% !important;
    padding: 0 !important;
    background: #ffffff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='none' stroke='%2328292D' stroke-width='1.7' stroke-linecap='round'%3E%3Cline x1='3' y1='5' x2='17' y2='5'/%3E%3Cline x1='5.5' y1='10' x2='14.5' y2='10'/%3E%3Cline x1='8' y1='15' x2='12' y2='15'/%3E%3C/svg%3E") no-repeat center / 18px !important;
    border: 1px solid #DCDCDE !important;
    border-radius: 8px !important;
    color: transparent !important;
    font-size: 0 !important;
    cursor: pointer !important;
    transition: background-color 0.18s ease, border-color 0.18s ease !important;
}
[data-testid="stPopover"] button:hover,
[data-testid="stPopoverButton"]:hover {
    background-color: #f0faf4 !important;
    border-color: #217858 !important;
}

/* ── Deep Dive: "pick a company" animated hint ── */
@keyframes hintFloat {
    0%, 100% { transform: translateY(0px); opacity: 0.75; }
    50%       { transform: translateY(-5px); opacity: 1; }
}
.nbfc-select-hint {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #217858;
    font-size: 0.82rem;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    padding: 0.55rem 0 0.1rem;
    animation: hintFloat 2.2s ease-in-out infinite;
    user-select: none;
}

/* ── Deep Dive: quick-select chip anchors ── */
.qs-chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.25rem 1.1rem;
    border-radius: 999px;
    border: 1.5px solid #D0D2D8;
    background: #FFFFFF;
    color: #28292D;
    font-size: 0.78rem;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
    text-decoration: none !important;
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.15s, border-color 0.15s, color 0.15s, box-shadow 0.15s;
    line-height: 1.5;
}
.qs-chip:hover {
    background: #F0FBF5;
    border-color: #2CA076;
    color: #144835;
    box-shadow: 0 1px 4px rgba(20,72,53,0.10);
    text-decoration: none !important;
}
.qs-chip.qs-active {
    background: #E8F5EE;
    border-color: #2CA076;
    color: #144835;
    font-weight: 600;
    box-shadow: 0 0 0 2px rgba(44,160,118,0.20);
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #DCDCDE; border-radius: 10px; }

/* ── Mobile ── */
@media (max-width: 640px) {
    /* Tighter container padding */
    .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-top: 0.8rem !important;
    }
    /* Smaller page title */
    .page-title { font-size: 1.35rem !important; }
    .page-subtitle { font-size: 0.72rem !important; }
    /* Stack ALL multi-column layouts vertically */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }
    [data-testid="stColumn"] {
        flex: 1 1 100% !important;
        min-width: 100% !important;
        width: 100% !important;
    }
    /* Tabs: smaller text + horizontal scroll instead of overflow */
    [data-baseweb="tab-list"] {
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
        padding-bottom: 4px !important;
    }
    [data-baseweb="tab"] {
        font-size: 0.72rem !important;
        padding: 0.3rem 0.65rem !important;
        white-space: nowrap !important;
    }
    /* Metric cards: tighter padding */
    [data-testid="metric-container"] {
        padding: 0.75rem 0.9rem 0.9rem !important;
        border-radius: 10px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
    /* Charts full width, centred */
    [data-testid="stPlotlyChart"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    [data-testid="stPlotlyChart"] > div {
        border-radius: 10px !important;
        width: 100% !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Re-trigger tab animation on each tab click via JS
st.markdown("""
<script>
(function() {
    function hookTabs() {
        const tabs = document.querySelectorAll('[data-baseweb="tab"]');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                setTimeout(() => {
                    const panels = document.querySelectorAll('[role="tabpanel"]');
                    panels.forEach(p => {
                        p.style.animation = 'none';
                        p.offsetHeight; // reflow
                        p.style.animation = '';
                    });
                }, 20);
            });
        });
    }
    // Wait for Streamlit to render
    const observer = new MutationObserver(() => { hookTabs(); });
    observer.observe(document.body, { childList: true, subtree: true });
    hookTabs();
})();
</script>
""", unsafe_allow_html=True)

COLOR = {
    "primary":        "#144835",   # MoneyView primary green
    "success":        "#217858",   # MoneyView mid green
    "teal":           "#2CA076",   # MoneyView teal accent
    "accent":         "#2CA076",   # MoneyView teal (replaces amber)
    "danger":         "#E7554A",   # MoneyView red
    "warning":        "#DE5E2B",   # MoneyView rust orange
    "blue":           "#2562BD",   # MoneyView blue
    "yellow":         "#FCC945",   # MoneyView yellow
    "purple":         "#9769B2",   # MoneyView purple
    "text":           "#28292D",   # MoneyView primary text
    "text_secondary": "#73757A",   # MoneyView secondary text
    "card_bg":        "#ffffff",
    "border":         "#EAEAEA",
    "chart_bg":       "#ffffff",
}

# Ordered palette for multi-series charts — MoneyView brand sequence
MV_PALETTE = [
    "#144835",  # deep forest green
    "#2CA076",  # teal
    "#DE5E2B",  # rust orange
    "#2562BD",  # blue
    "#FCC945",  # yellow
    "#9769B2",  # purple
    "#37C893",  # bright green
    "#E7554A",  # red
    "#505259",  # charcoal
    "#73757A",  # grey
]

PERIOD_ORDER = ["FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "9MFY26"]
PERIOD_ORDER_ANN = ["FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "9MFY26 (Ann.)"]
PERIOD_SHORT = {
    "FY2021": "FY21", "FY2022": "FY22", "FY2023": "FY23",
    "FY2024": "FY24", "FY2025": "FY25", "9MFY26": "9MFY26",
    "9MFY26 (Ann.)": "9MFY26 (Ann.)",
}
# Same as PERIOD_SHORT but flags 9MFY26 as annualised — use for hover on ROA/ROE/PAT/NII charts
PERIOD_SHORT_ANN = {**PERIOD_SHORT, "9MFY26": "9MFY26 (Ann.)"}

# ── Ensure DB exists ─────────────────────────────────────────────────────────
import os as _os
_DB_PATH    = "data/nbfc_full.db"
_BUILD_PATH = "build_db.py"
_db_stale = (
    not _os.path.exists(_DB_PATH) or
    _os.path.getmtime(_BUILD_PATH) > _os.path.getmtime(_DB_PATH)
)
if _db_stale:
    import build_db as _build_db
    _build_db.build()
    st.cache_resource.clear()
    st.cache_data.clear()

# ── Data loaders ─────────────────────────────────────────────────────────────

def load_nbfc_table():
    conn = sqlite3.connect("data/nbfc_full.db")
    df = pd.read_sql("SELECT * FROM nbfc", conn)
    conn.close()
    return df

def load_financials():
    conn = sqlite3.connect("data/nbfc_full.db")
    df = pd.read_sql("""
        SELECT f.*, n.name, n.rbi_layer, n.sector, n.listed,
               n.data_quality AS company_dq, n.has_financials
        FROM financials f
        JOIN nbfc n ON f.nbfc_id = n.id
    """, conn)
    conn.close()
    # ── Recompute credit_loss_rate_pct consistently for all annual periods ──────
    # Formula: gross credit losses (impairment on financial instruments, P&L) ÷ ending loan book.
    # - Annual rows: credit_losses_cr / ending loan_book_cr × 100
    # - Q3 rows: excluded here — annualise_9m() handles them using (credit_losses_cr × 4/3) / avg loan book
    # Moneyview credit_losses_cr now stores total managed portfolio losses (not on-book only),
    # and loan_book_cr = managed AUM, so this formula is consistent across all companies.
    annual_mask = (
        ~df["period"].str.contains("Q3", na=False)  # Q3 rows handled by annualise_9m
        & df["credit_losses_cr"].notna()
        & df["loan_book_cr"].notna()
        & (df["loan_book_cr"] > 0)
    )
    df.loc[annual_mask, "credit_loss_rate_pct"] = (
        df.loc[annual_mask, "credit_losses_cr"] / df.loc[annual_mask, "loan_book_cr"] * 100
    ).round(2)
    return df

# ── Helper functions ──────────────────────────────────────────────────────────

def annual_only(df):
    """Return only annual period rows (excludes Q1/Q2/Q3)."""
    return df[~df["period"].str.contains("Q")]


def truncate_name(name, n=15):
    return name[:n] + "…" if len(name) > n else name


# Post-tax one-time exceptional items excluded from ROA/ROE calculations (₹ Crore).
# These inflate reported PAT but do not reflect recurring earnings power.
EXCEPTIONAL_ITEMS_ADJ = {
    ("KreditBee", "9MFY26"): 152,  # GST provision reversal ₹104 Cr + DTA recognition ₹48 Cr
    # Moneyview DB stores ₹245 Cr (PAT before exceptional charges per DRHP) — no further
    # adjustment needed; annualise_9m() uses this directly for ROA/ROE calculations.
}

# Companies whose ROA (and optionally ROE) use a non-standard denominator stored in the DB.
# For these, annualise_9m preserves the pre-stored Q3 roa_pct/roe_pct rather than
# recalculating from loan_book_cr.
# Note: Moneyview loan_book_cr = managed AUM, so the generic annualise_9m formula is correct.
USE_STORED_ROA_ROE: set = set()



def annualise_9m(df):
    """
    Build 9MFY26 rows from FY2026-Q3 data.
    - NII: annualised (×4/3) so it is comparable to full-year figures on charts.
    - PAT: annualised (×4/3) after exceptional items adjustment.
    - credit_losses_cr: raw 9-month value (rate is annualised separately).
    - ROA: annualised PAT ÷ avg loan book (pat_cr already annualised — used directly).
    - ROE: annualised PAT ÷ avg equity (pat_cr already annualised — used directly).
    - credit_loss_rate_pct: annualised credit losses (×4/3) ÷ avg loan book
      (avg of FY2025 closing and Q3 closing).
    - EXCEPTIONAL_ITEMS_ADJ: company-specific post-tax one-time items subtracted
      from 9M PAT before annualising.
    """
    q3 = df[df["period"] == "FY2026-Q3"].copy()
    if q3.empty:
        return pd.DataFrame()
    ann = q3.copy()
    ann["period"] = "9MFY26"

    fy25 = df[df["period"] == "FY2025"]

    def _adj_9m_pat(base_9m_pat):
        """Subtract 9M exceptional items from 9M PAT *before* annualising (×4/3 applied after)."""
        adj = base_9m_pat.copy()
        for (comp_name, _period_lbl), adj_cr in EXCEPTIONAL_ITEMS_ADJ.items():
            mask = ann["name"] == comp_name
            adj = adj.where(~mask, adj - adj_cr)
        return adj

    # Adjust and annualise pat_cr: subtract exceptional items then multiply by 4/3
    if "pat_cr" in ann.columns:
        ann["pat_cr"] = _adj_9m_pat(ann["pat_cr"]) * (4 / 3)

    # Annualise NII so it is comparable to full-year figures on trend charts
    if "net_interest_income_cr" in ann.columns:
        ann["net_interest_income_cr"] = ann["net_interest_income_cr"] * (4 / 3)

    # ROA: annualised adjusted PAT ÷ avg loan book (FY25 + Q3) / 2
    # pat_cr is already annualised (×4/3) — use directly
    if "pat_cr" in ann.columns and "loan_book_cr" in ann.columns and not fy25.empty:
        ann_pat = ann["pat_cr"]
        fy25_lb = fy25.set_index("nbfc_id")["loan_book_cr"]
        avg_lb = ann.apply(
            lambda r: (fy25_lb.get(r["nbfc_id"], r["loan_book_cr"]) + r["loan_book_cr"]) / 2,
            axis=1,
        )
        ann["roa_pct"] = (ann_pat.values / avg_lb.values * 100)

    # ROE: annualised adjusted PAT ÷ avg equity (FY25 + Q3) / 2
    # pat_cr is already annualised (×4/3) — use directly
    if "pat_cr" in ann.columns and "equity_cr" in ann.columns and not fy25.empty:
        ann_pat = ann["pat_cr"]
        fy25_equity = fy25.set_index("nbfc_id")["equity_cr"]
        avg_equity = ann.apply(
            lambda r: (fy25_equity.get(r["nbfc_id"], r["equity_cr"]) + r["equity_cr"]) / 2,
            axis=1,
        )
        ann["roe_pct"] = (ann_pat.values / avg_equity.values * 100)

    # Annualized loss rate: annualised credit losses (×4/3) ÷ avg loan book (FY25 + Q3) / 2
    if "credit_losses_cr" in ann.columns and "loan_book_cr" in ann.columns and not fy25.empty:
        ann_cl = ann["credit_losses_cr"] * (4 / 3)
        fy25_lb = fy25.set_index("nbfc_id")["loan_book_cr"]
        avg_lb = ann.apply(
            lambda r: (fy25_lb.get(r["nbfc_id"], r["loan_book_cr"]) + r["loan_book_cr"]) / 2,
            axis=1,
        )
        ann["credit_loss_rate_pct"] = (ann_cl.values / avg_lb.values * 100)

    # For companies with non-standard ROA/ROE denominators, restore the pre-stored Q3 values
    # instead of the generic loan_book_cr-based recalculation above.
    for comp_name in USE_STORED_ROA_ROE:
        mask = ann["name"] == comp_name
        q3_mask = q3["name"] == comp_name
        if mask.any() and q3_mask.any():
            ann.loc[mask, "roa_pct"] = q3.loc[q3_mask, "roa_pct"].values[0]
            ann.loc[mask, "roe_pct"] = q3.loc[q3_mask, "roe_pct"].values[0]

    return ann



def get_chart_periods(df):
    """Annual FY2021–FY2025 plus annualised 9MFY26, sorted."""
    annual = annual_only(df)
    ann_9m = annualise_9m(df)
    combined = pd.concat([annual, ann_9m], ignore_index=True)
    combined["period"] = pd.Categorical(combined["period"], categories=PERIOD_ORDER, ordered=True)
    return combined.sort_values(["name", "period"])



def get_latest_period_data(df):
    """
    Per company: use 9MFY26 if FY2026-Q3 exists, else FY2025.
    """
    ann_9m = annualise_9m(df)
    annual = annual_only(df)
    fy25 = annual[annual["period"] == "FY2025"]
    if ann_9m.empty:
        return fy25
    companies_with_q3 = set(ann_9m["name"].unique())
    fy25_only = fy25[~fy25["name"].isin(companies_with_q3)]
    return pd.concat([fy25_only, ann_9m], ignore_index=True)


def latest_period_label(df):
    return "FY25 / 9MFY26" if "FY2026-Q3" in df["period"].values else "FY25"

def period_label_for(df):
    """Return a period label based only on the periods actually present in df."""
    periods = df["period"].dropna().unique() if "period" in df.columns else []
    has_9m  = any("9M" in str(p) or "FY2026" in str(p) for p in periods)
    has_fy25 = any("FY2025" in str(p) for p in periods)
    if has_9m and has_fy25:
        return "FY25 / 9MFY26"
    elif has_9m:
        return "9MFY26"
    else:
        return "FY25"


def compute_cagr(df, metric_col, start_year="FY2021", end_year="FY2025"):
    """CAGR between two annual periods. Never uses quarterly rows."""
    annual = annual_only(df)
    start = annual[annual["period"] == start_year][["nbfc_id", "name", metric_col]].rename(
        columns={metric_col: "start_val"})
    end = annual[annual["period"] == end_year][["nbfc_id", metric_col]].rename(
        columns={metric_col: "end_val"})
    merged = start.merge(end, on="nbfc_id")
    merged = merged[(merged["start_val"] > 0) & (merged["end_val"] > 0)]
    years = int(end_year[-4:]) - int(start_year[-4:])
    merged["cagr_pct"] = ((merged["end_val"] / merged["start_val"]) ** (1 / years) - 1) * 100
    return merged[["name", "cagr_pct"]].sort_values("cagr_pct", ascending=False)


def compute_latest_growth(df, metric_col):
    """
    Per-company 1-year AUM growth using the most recent pair available:
      - If 9MFY26 exists → annualised growth: ((9MFY26/FY2025)^(12/9) − 1)
      - Otherwise             → (FY2025 − FY2024) / FY2024
    Returns DataFrame with columns: name, growth_pct, period_label
    """
    ann_9m = annualise_9m(df)
    annual = annual_only(df)
    fy25 = annual[annual["period"] == "FY2025"][["nbfc_id", "name", metric_col]].rename(
        columns={metric_col: "fy25"})
    fy24 = annual[annual["period"] == "FY2024"][["nbfc_id", metric_col]].rename(
        columns={metric_col: "fy24"})

    rows = []
    if not ann_9m.empty:
        ann = ann_9m[["nbfc_id", "name", metric_col]].rename(columns={metric_col: "recent"})
        merged = ann.merge(fy25, on=["nbfc_id", "name"], how="inner")
        merged = merged[merged["fy25"] != 0]  # only exclude zero FY25 (avoid division by zero)
        # Annualise: 9MFY26 covers 9 months vs FY25's 12 months
        merged["growth_pct"] = (merged["recent"] * (4 / 3) / merged["fy25"] - 1) * 100
        merged["period_label"] = "9MFY26 (Ann.) vs FY25"
        rows.append(merged[["name", "growth_pct", "period_label"]])

    # Companies without Q3 data use FY25 vs FY24
    companies_with_9m = set(ann_9m["name"].unique()) if not ann_9m.empty else set()
    fy25_no9m = fy25[~fy25["name"].isin(companies_with_9m)]
    merged2 = fy25_no9m.merge(fy24, on="nbfc_id", how="inner")
    merged2 = merged2[(merged2["fy25"] > 0) & (merged2["fy24"] > 0)]
    merged2["growth_pct"] = (merged2["fy25"] / merged2["fy24"] - 1) * 100
    merged2["period_label"] = "FY25 vs FY24"
    rows.append(merged2[["name", "growth_pct", "period_label"]])

    if not rows:
        return pd.DataFrame(columns=["name", "growth_pct", "period_label"])
    result = pd.concat(rows, ignore_index=True)
    return result.sort_values("growth_pct", ascending=False)


def bar_chart_height(n, min_h=360, max_h=1000, px_per_row=34):
    return max(min_h, min(max_h, n * px_per_row))


CHART_FONT  = "Inter"
CHART_TITLE_FONT = "Inter"
CHART_MONO  = "Inter"
CHART_BG    = "#ffffff"
CHART_PAPER = "#ffffff"
CHART_GRID  = "#EAEAEA"
HOVER_LABEL = dict(
    bgcolor="#101012", bordercolor="#144835",
    font=dict(family=CHART_FONT, size=11, color="#e8e8e8"),
    align="left",
    namelength=0,
)


def split_title(title, max_len=32):
    """Split a chart title into (main, subtitle_or_None).

    Uses Plotly's native subtitle support (>=5.18) so no HTML tag hacks needed.
    """
    if not title:
        return "", None
    # Any parenthetical always becomes the subtitle
    paren_idx = title.find(" (")
    if paren_idx > 0:
        return title[:paren_idx].strip(), title[paren_idx:].strip()
    # Short titles with no parenthetical: no split
    if len(title) <= max_len:
        return title, None
    # Long titles: split at natural separator
    for sep in [" — ", ": ", " - ", " vs "]:
        idx = title.find(sep)
        if 0 < idx <= max_len:
            return title[:idx].strip(), title[idx:].strip()
    idx = title.rfind(" ", 0, max_len)
    if idx > 0:
        return title[:idx].strip(), title[idx + 1:].strip()
    return title, None


def _title_dict(raw_title, pad_t=10, pad_b=14):
    """Build a Plotly title dict compatible with all Plotly versions.
    Uses <b> for main title and <br> + smaller text for subtitle.
    """
    main, sub = split_title(raw_title)
    main_nbsp = main.replace(" ", "\u00a0")
    if sub:
        sub_nbsp = sub.replace(" ", "\u00a0")
        text = f"<b>{main_nbsp}</b><br><sub>{sub_nbsp}</sub>"
    else:
        text = f"<b>{main_nbsp}</b>"
    return dict(
        text=text,
        font=dict(color=COLOR["text"], size=15, family=CHART_TITLE_FONT),
        x=0.5, xanchor="center", xref="paper",
        pad=dict(t=pad_t, b=pad_b),
    )


# Keep wrap_title as a thin shim so any callers that still use it keep working
def wrap_title(title, max_len=32):
    main, sub = split_title(title, max_len)
    return f"{main}<br>{sub}" if sub else main


def note(text, kind="info"):
    """Render a minimal, elegant disclosure note with a left-border accent."""
    palette = {
        "info":    {"border": "#144835", "color": "#217858"},
        "warning": {"border": "#d97706", "color": "#7c4a00"},
        "error":   {"border": "#c0392b", "color": "#7f1d1d"},
    }
    p = palette.get(kind, palette["info"])
    st.markdown(
        f'<div style="border-left:2px solid {p["border"]};padding:0.28rem 0.85rem;'
        f'margin:0.6rem 0;font-family:\'Inter\',sans-serif;font-size:0.7rem;'
        f'color:{p["color"]};line-height:1.55;opacity:0.85;">{text}</div>',
        unsafe_allow_html=True,
    )


MONEYVIEW_GREEN = "#1B5E20"   # Moneyview brand dark green

def make_hbar(df, x_col, y_col, color, title, height=None, hover_text=None, text_suffix="", text_labels=None, label_position="bar_end"):
    """Standard horizontal bar chart — pass data sorted DESCENDING (chart reverses y-axis).
    Moneyview is automatically highlighted: dark-green bar + bold dark-green label.
    label_position: 'bar_end' = text right after each bar (default);
                    'right_edge' = fixed annotations at paper right edge (for charts with negatives)."""
    df = df.copy()
    df[y_col] = df[y_col].apply(lambda n: truncate_name(str(n)))
    h = height or bar_chart_height(len(df))
    vals = df[x_col].dropna()
    x_max = vals.abs().max() if not vals.empty else 1
    x_left = vals.min() * 1.55 if vals.min() < 0 else 0
    if text_labels is None:
        text_labels = df[x_col].round(1).astype(str) + text_suffix

    names = df[y_col].tolist()
    bar_colors = [MONEYVIEW_GREEN if n == "Moneyview" else color for n in names]
    tick_text = [
        f"<b><span style='color:{MONEYVIEW_GREEN}'>{n}</span></b>"
        if n == "Moneyview" else n
        for n in names
    ]

    fig = px.bar(df, x=x_col, y=y_col, orientation="h", height=h)

    if label_position == "bar_end":
        # Labels anchored to each bar's end — explicit annotations so label tracks
        # the bar, not the paper edge (avoids all labels clustering at the right).
        x_range = [x_left, x_max * 1.55]
        fig.update_traces(
            marker_color=bar_colors, marker_line_width=0, marker_opacity=0.85,
        )
        bar_vals = df[x_col].tolist()
        for name, label, val in zip(names, list(text_labels), bar_vals):
            fig.add_annotation(
                x=max(val, 0) if x_left == 0 else val,
                y=name,
                text=label, showarrow=False,
                xanchor="left", yanchor="middle", xshift=5,
                font=dict(family=CHART_MONO, size=11.5, color=COLOR["text_secondary"]),
            )
        r_margin = 16
    else:
        # Fixed annotations at the far right edge (safe for charts with negative values)
        x_range = [x_left, x_max * 1.05]
        fig.update_traces(marker_color=bar_colors, marker_line_width=0, marker_opacity=0.85)
        for name, label in zip(names, text_labels):
            fig.add_annotation(
                x=1.0, xref="paper", y=name, yref="y",
                text=label, showarrow=False,
                xanchor="left", yanchor="middle", xshift=6,
                font=dict(family=CHART_MONO, size=11.5, color=COLOR["text_secondary"]),
            )
        r_margin = 70

    fig.update_layout(
        title=_title_dict(title),
        paper_bgcolor=CHART_PAPER, plot_bgcolor=CHART_BG,
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT, size=12),
        yaxis=dict(autorange="reversed",
                   tickmode="array", tickvals=names, ticktext=tick_text,
                   tickfont=dict(family=CHART_FONT, size=12.5),
                   showgrid=False, tickcolor="rgba(0,0,0,0)", title=""),
        xaxis=dict(showgrid=False, showticklabels=False,
                   range=x_range, zeroline=True, zerolinecolor=CHART_GRID,
                   zerolinewidth=1, tickcolor="rgba(0,0,0,0)", title=""),
        bargap=0.28,
        margin=dict(l=90, r=r_margin, t=90, b=24),
        hoverlabel=HOVER_LABEL,
    )
    if hover_text is not None:
        import numpy as np
        fig.update_traces(customdata=np.array(hover_text).reshape(-1, 1),
                          hovertemplate="%{customdata[0]}<extra></extra>")
    else:
        fig.update_traces(hovertemplate="<extra></extra>")
    return fig


def chart_layout(fig, title=None):
    existing = ""
    if fig.layout.title and fig.layout.title.text:
        existing = fig.layout.title.text
    raw = title or existing
    fig.update_layout(
        paper_bgcolor=CHART_PAPER, plot_bgcolor=CHART_BG,
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT, size=12),
        title=_title_dict(raw) if raw else {},
        xaxis=dict(
            showgrid=False,
            tickfont=dict(family=CHART_MONO, size=11, color="#73757A"),
            zeroline=False,
            tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)", title="",
            tickvals=list(PERIOD_SHORT.keys()),
            ticktext=list(PERIOD_SHORT.values()),
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(family=CHART_MONO, size=11, color="#73757A"),
            zeroline=True, zerolinecolor="#EAEAEA", zerolinewidth=1,
            tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)", title="",
        ),
        margin=dict(t=86, b=90, l=10, r=24),
        legend=dict(
            font=dict(family=CHART_FONT, size=11, color="#73757A"),
            bgcolor="rgba(249,251,249,0.85)",
            bordercolor="rgba(35,107,53,0.12)",
            borderwidth=1,
            orientation="h",
            yanchor="bottom", y=-0.32,
            xanchor="left", x=0,
            title_text="",
        ),
        hoverlabel=HOVER_LABEL,
    )
    fig.update_traces(hovertemplate="%{x}<extra></extra>")
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────


nbfc_df = load_nbfc_table()
fin_df = load_financials()

all_sectors = sorted(nbfc_df["sector"].dropna().unique().tolist())
_default_sectors = ["Consumer Finance"] if "Consumer Finance" in all_sectors else []
sector_filter = st.sidebar.multiselect("Sector", all_sectors, default=_default_sectors, placeholder="All sectors")
listing_filter = st.sidebar.radio("Listing Status", ["All", "Listed Only", "Unlisted Only"])
include_estimated = st.sidebar.checkbox("Include Estimated Data", value=True)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: Company annual reports, Screener.in. "
    "⚠️ = estimated from rating reports. "
    "❌ = unverified. "
    "Live valuations from Yahoo Finance."
)
st.sidebar.markdown("---")
if _AUTH_ENABLED:
    st.sidebar.caption(f"Signed in as **{st.user.email}**")
    if st.sidebar.button("Sign out", use_container_width=True):
        st.logout()

# ── Active filter badge (computed here, injected into page header below) ──────
_active_filters = []
# Sector: show first item + "+N" if multiple, skip if nothing selected
if sector_filter:
    if len(sector_filter) == 1:
        _active_filters.append(sector_filter[0])
    else:
        _active_filters.append(f"{sector_filter[0]} +{len(sector_filter)-1}")
if listing_filter != "All":
    _active_filters.append(listing_filter.replace(" Only", ""))
_badge_label = " · ".join(_active_filters) if _active_filters else "All NBFCs"


def apply_filters(df):
    d = df.copy()
    if sector_filter:  # non-empty list → filter active
        d = d[d["sector"].isin(sector_filter)]
    if listing_filter == "Listed Only":
        d = d[d["listed"] == 1]
    elif listing_filter == "Unlisted Only":
        d = d[d["listed"] == 0]
    if not include_estimated:
        dq_col = "data_quality" if "data_quality" in d.columns else "company_dq"
        d = d[d[dq_col].isin(["audited", "DRHP"])]
    return d


fin_filtered = apply_filters(fin_df)
nbfc_filtered = apply_filters(nbfc_df)

# ── Page header ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
@keyframes headerFadeIn {
    from { opacity: 0; transform: translateY(-8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.page-header-wrap {
    animation: headerFadeIn 0.4s cubic-bezier(0.22,1,0.36,1) both;
    padding-top: 0.5rem;
    margin-bottom: 1.6rem;
}
.page-title {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 2.0rem;
    letter-spacing: -0.03em;
    line-height: 1.1;
    color: #28292D;
    display: inline;
}
.page-badge {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    color: #144835;
    background: #D7F4E9;
    border: 1px solid #AFE9D4;
    padding: 3px 10px;
    border-radius: 4px;
    letter-spacing: 0.07em;
    vertical-align: middle;
    position: relative;
    top: -4px;
}
.page-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.84rem;
    color: #73757A;
    margin: 0.4rem 0 0 0;
    font-weight: 400;
    letter-spacing: 0.01em;
}
.header-rule {
    border: none;
    border-top: 1px solid #EAEAEA;
    margin: 1rem 0 1.4rem 0;
}
</style>
<div class="page-header-wrap">
  <div style="display:flex; align-items:center; gap:0.8rem; flex-wrap:wrap;">
    <span class="page-title">NBFC Intelligence</span>
    <span class="page-badge">INDIA</span>
  </div>
  <p class="page-subtitle">Non-Banking Financial Companies &mdash; Growth &middot; Profitability &middot; Asset Quality &middot; Valuation</p>
  <hr class="header-rule"/>
</div>
""", unsafe_allow_html=True)

# Filter badge — injected into parent DOM via components.html iframe (window.parent access)
# MY_TS ownership: only the most-recently-created iframe updates the badge (prevents stale iframes
# from overwriting). Uses a named <span> for text so onclick is never replaced.
components.html(f"""
<script>
(function() {{
  var LABEL  = {repr(_badge_label)};
  var MY_TS  = String(Date.now());
  var CSS    = "position:fixed;top:0.62rem;left:3.4rem;z-index:2147483647;"
             + "display:inline-flex;align-items:center;gap:0.4rem;"
             + "background:#EAF4EE;border:1.5px solid #144835;border-radius:20px;"
             + "padding:0.26rem 0.8rem 0.26rem 0.65rem;cursor:pointer;user-select:none;"
             + "font-size:0.78rem;font-weight:700;color:#144835;"
             + "box-shadow:0 2px 8px rgba(0,0,0,0.18);font-family:Inter,sans-serif;"
             + "max-width:calc(100vw - 9rem);";

  function toggleSidebar() {{
    var doc = window.parent.document;
    var btn = doc.querySelector('[data-testid="stSidebarCollapsedControl"] button')
           || doc.querySelector('[data-testid="stSidebarCollapseButton"] button')
           || doc.querySelector('[data-testid="stSidebarCollapsedControl"]')
           || doc.querySelector('[data-testid="stSidebarCollapseButton"]');
    if (btn) btn.dispatchEvent(new MouseEvent('click', {{bubbles:true, cancelable:true, view:window.parent}}));
  }}

  var INNER = '<svg width="13" height="13" viewBox="0 0 16 16" fill="none" style="flex-shrink:0">'
            + '<path d="M2 4h12M4 8h8M6 12h4" stroke="#144835" stroke-width="2.2" stroke-linecap="round"/>'
            + '</svg>'
            + '<span class="nbfc-bl" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0">' + LABEL + '</span>'
            + '<svg width="10" height="10" viewBox="0 0 16 16" fill="none" style="flex-shrink:0;margin-left:1px">'
            + '<path d="M6 3l5 5-5 5" stroke="#144835" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
            + '</svg>';
  function syncBadge() {{
    try {{
      var doc = window.parent.document;
      var b = doc.getElementById('nbfc-filter-badge');
      if (b) {{
        var owner = b.dataset.owner || '0';
        if (MY_TS < owner) return;          // A newer iframe owns this — stand down
        b.dataset.owner = MY_TS;
        b.onclick = toggleSidebar;
        var sp = b.querySelector('.nbfc-bl');
        if (!sp) {{
          // Stale badge from old code structure — rebuild inner HTML
          b.innerHTML = INNER;
        }} else if (sp.textContent !== LABEL) {{
          sp.textContent = LABEL;
        }}
      }} else {{
        b = doc.createElement('div');
        b.id = 'nbfc-filter-badge';
        b.title = 'Click to open/close filters';
        b.setAttribute('style', CSS);
        b.dataset.owner = MY_TS;
        b.onclick = toggleSidebar;
        b.innerHTML = INNER;
        doc.body.appendChild(b);
      }}
    }} catch(e) {{ console.warn('nbfc-badge:', e); }}
  }}

  syncBadge();
  setInterval(syncBadge, 1200);
}})();
</script>
""", height=0, scrolling=False)

annual_fin = annual_only(fin_filtered)
latest_annual = annual_fin[annual_fin["period"] == "FY2025"]

total_nbfcs = 9359
with_data = nbfc_filtered[nbfc_filtered["has_financials"] == 1].shape[0]
total_assets = latest_annual["total_assets_cr"].sum() / 1e5  # to Lakh Crore
avg_gnpa = latest_annual["gnpa_pct"].mean()

growth_df_header = compute_latest_growth(fin_filtered, "loan_book_cr")
avg_growth = growth_df_header["growth_pct"].mean() if not growth_df_header.empty else 0.0

_gap, c1, c2, c3, c4, c5, _gap2 = st.columns([0.3, 1, 1, 1, 1, 1, 0.3])
c1.metric("Total NBFCs", f"{total_nbfcs:,}", help="RBI Registry")
c2.metric("With Financials", f"{with_data:,}")
c3.metric("Combined Assets", f"₹{total_assets:.1f}L Cr", help="FY25")
c4.metric("Avg AUM Growth", f"{avg_growth:.1f}%", help="Latest 1Y")
c5.metric("Avg GNPA", f"{avg_gnpa:.2f}%", help="FY25")

# ── Tabs ──────────────────────────────────────────────────────────────────────

tabs = st.tabs([
    "Growth", "Profitability", "Credit Quality",
    "NBFC Specific", "Top Ranked",
    "Valuation", "Data", "Trends",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: GROWTH
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    lbl = latest_period_label(fin_filtered)
    estimated_names = set(
        fin_filtered[fin_filtered["data_quality"] == "estimated"]["name"].unique()
    )
    sectors_df = fin_filtered[["name", "sector"]].drop_duplicates()

    growth_df    = compute_latest_growth(fin_filtered, "loan_book_cr").dropna(subset=["growth_pct"])
    rev_growth_df = compute_latest_growth(fin_filtered, "net_interest_income_cr").dropna(subset=["growth_pct"])
    pat_growth_df = compute_latest_growth(fin_filtered, "pat_cr").dropna(subset=["growth_pct"])

    def _add_star(df):
        df = df.copy()
        df["display_name"] = df["name"].apply(lambda n: n + " ★" if n in estimated_names else n)
        return df

    growth_df     = _add_star(growth_df)
    rev_growth_df = _add_star(rev_growth_df)
    pat_growth_df = _add_star(pat_growth_df)

    # ── Row 1: AUM | Revenue | PAT Growth ────────────────────────────────────
    st.markdown('<div class="section-header">Growth — Latest 1 Year</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        fig = make_hbar(growth_df.sort_values("growth_pct", ascending=False),
                        "growth_pct", "display_name", COLOR["success"],
                        "AUM Growth % (Fastest → Slowest)",
                        hover_text=growth_df.sort_values("growth_pct", ascending=False)["period_label"].values,
                        text_suffix="%", label_position="right_edge")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = make_hbar(rev_growth_df.sort_values("growth_pct", ascending=False),
                        "growth_pct", "display_name", COLOR["primary"],
                        "Revenue Growth % (Fastest → Slowest)",
                        hover_text=rev_growth_df.sort_values("growth_pct", ascending=False)["period_label"].values,
                        text_suffix="%", label_position="right_edge")
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        fig = make_hbar(pat_growth_df.sort_values("growth_pct", ascending=False),
                        "growth_pct", "display_name", COLOR["accent"],
                        "PAT Growth % (Fastest → Slowest)",
                        hover_text=pat_growth_df.sort_values("growth_pct", ascending=False)["period_label"].values,
                        text_suffix="%", label_position="right_edge")
        st.plotly_chart(fig, use_container_width=True)

    st.caption("★ = estimated data. 9MFY26 growth annualised: (9M value × 4/3) / FY25 − 1. Otherwise FY25 vs FY24.")

    # ── Row 2: AUM | Revenue | PAT Growth by Sector ──────────────────────────
    # Use unfiltered fin_df so sector charts always show all sectors
    _sectors_map = fin_df[["name", "sector"]].drop_duplicates()
    _growth_all     = compute_latest_growth(fin_df, "loan_book_cr").dropna(subset=["growth_pct"]).merge(_sectors_map, on="name", how="left")
    _rev_growth_all = compute_latest_growth(fin_df, "net_interest_income_cr").dropna(subset=["growth_pct"]).merge(_sectors_map, on="name", how="left")
    _pat_growth_all = compute_latest_growth(fin_df, "pat_cr").dropna(subset=["growth_pct"]).merge(_sectors_map, on="name", how="left")

    st.markdown('<div class="section-header">Growth by Sector — Latest 1Y</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        sector_aum = (
            _growth_all.groupby("sector")["growth_pct"].mean().reset_index()
            .sort_values("growth_pct", ascending=False)
        )
        fig = make_hbar(sector_aum, "growth_pct", "sector", COLOR["primary"],
                        "Avg AUM Growth % by Sector",
                        hover_text=[lbl] * len(sector_aum), text_suffix="%", label_position="right_edge")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        sector_rev = (
            _rev_growth_all.groupby("sector")["growth_pct"].mean().reset_index()
            .sort_values("growth_pct", ascending=False)
        )
        fig = make_hbar(sector_rev, "growth_pct", "sector", COLOR["success"],
                        "Avg Revenue Growth % by Sector",
                        hover_text=[lbl] * len(sector_rev), text_suffix="%", label_position="right_edge")
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        sector_pat = (
            _pat_growth_all.groupby("sector")["growth_pct"].mean().reset_index()
            .sort_values("growth_pct", ascending=False)
        )
        fig = make_hbar(sector_pat, "growth_pct", "sector", COLOR["accent"],
                        "Avg PAT Growth % by Sector",
                        hover_text=[lbl] * len(sector_pat), text_suffix="%", label_position="right_edge")
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Revenue Growth vs PAT Growth bubble chart ─────────────────────
    st.markdown('<div class="section-header">Revenue Growth vs PAT Growth</div>', unsafe_allow_html=True)
    latest_lb = get_latest_period_data(fin_filtered)[["name", "loan_book_cr", "sector"]].dropna(subset=["loan_book_cr"])
    bubble_df = (
        rev_growth_df[["name", "growth_pct", "period_label"]].rename(
            columns={"growth_pct": "rev_growth", "period_label": "rev_period"})
        .merge(pat_growth_df[["name", "growth_pct", "period_label"]].rename(
            columns={"growth_pct": "pat_growth", "period_label": "pat_period"}), on="name", how="inner")
        .merge(latest_lb, on="name", how="inner")
        .dropna(subset=["rev_growth", "pat_growth", "loan_book_cr"])
        .query("name != 'Sammaan Capital'")
        .query("pat_growth >= -200 and pat_growth <= 500")
    )
    if not bubble_df.empty:
        default_period = "9MFY26 (Ann.) vs FY25"
        fig = px.scatter(
            bubble_df, x="rev_growth", y="pat_growth",
            size="loan_book_cr", color="sector",
            hover_name="name",
            custom_data=["name", "rev_growth", "pat_growth"],
            color_discrete_sequence=MV_PALETTE,
            labels={"rev_growth": "Revenue Growth %", "pat_growth": "PAT Growth %"},
            title=f"Revenue Growth vs PAT Growth (FY25 to 9MFY26 Growth, Bubble size based on AUM)",
            height=520,
        )
        chart_layout(fig)
        fig.update_layout(
            xaxis=dict(title="Revenue Growth %", title_font=dict(size=12, family=CHART_FONT),
                       autorange=True, tickvals=None, ticktext=None),
            yaxis=dict(title="PAT Growth %", title_font=dict(size=12, family=CHART_FONT),
                       autorange=True, tickvals=None, ticktext=None),
        )
        fig.update_traces(
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Rev Growth = %{customdata[1]:.1f}%<br>"
                "PAT Growth = %{customdata[2]:.1f}%"
                "<extra></extra>"
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # Note any NBFCs where the growth period differs from the default
        diff_rev = bubble_df[bubble_df["rev_period"] != default_period][["name", "rev_period"]]
        diff_pat = bubble_df[bubble_df["pat_period"] != default_period][["name", "pat_period"]]
        diff_notes = []
        for _, row in diff_rev.iterrows():
            diff_notes.append(f"{row['name']} (Revenue: {row['rev_period']})")
        for _, row in diff_pat.iterrows():
            name = row["name"]
            if not any(name in n for n in diff_notes):
                diff_notes.append(f"{name} (PAT: {row['pat_period']})")
        if diff_notes:
            st.caption("Different growth period: " + "; ".join(diff_notes))

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: PROFITABILITY
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    lbl = latest_period_label(fin_filtered)
    latest_snap = get_latest_period_data(fin_filtered).dropna(subset=["roa_pct", "roe_pct"])

    st.markdown(f'<div class="section-header">Return on Assets & Equity — {lbl}</div>',
                unsafe_allow_html=True)
    _exc_caption = ("* KreditBee 9MFY26: annualised adj. PAT ₹252 Cr "
                    "(₹341 Cr reported − ₹152 Cr exceptional items × 4/3).  "
                    "Moneyview 9MFY26: pre-exceptional PAT ₹245 Cr × 4/3 = ₹327 Cr annualised.")
    col1, col2 = st.columns(2)
    with col1:
        all_roa = latest_snap.sort_values("roa_pct", ascending=False)
        fig = make_hbar(all_roa, "roa_pct", "name", COLOR["primary"],
                        f"ROA % ({lbl})",
                        hover_text=all_roa["period"].map(lambda p: PERIOD_SHORT_ANN.get(p, p)).values,
                        text_suffix="%")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        all_roe = latest_snap.sort_values("roe_pct", ascending=False)
        fig = make_hbar(all_roe, "roe_pct", "name", COLOR["accent"],
                        f"ROE % ({lbl})",
                        hover_text=all_roe["period"].map(lambda p: PERIOD_SHORT_ANN.get(p, p)).values,
                        text_suffix="%")
        st.plotly_chart(fig, use_container_width=True)
    st.caption(_exc_caption)

    st.caption(f"Where 9MFY26 data exists: 9MFY26 ROA/ROE used. Otherwise FY25. "
               f"★ = estimated data.")
    note("KreditBee 9MFY26 — PAT & ROA adjusted for one-time exceptional items:  "
         "Reported 9M PAT ₹341 Cr − ₹152 Cr exceptional (₹104 Cr GST provision reversal, Karnataka HC Dec 2025 "
         "+ ₹48 Cr DTA recognition) = Adjusted 9M PAT ₹189 Cr × 4/3 = Annualised PAT ₹252 Cr.  "
         "Adjusted ROA = ₹252 Cr ÷ avg loan book ₹7,049 Cr [(₹5,649 + ₹8,448) ÷ 2] = 3.58%.", "warning")
    note("Moneyview 9MFY26: Loan book = managed AUM (₹19,815 Cr). ROA & ROE use PAT before exceptional items "
         "(₹245 Cr, 9M → annualised ₹327 Cr). Reported 9M PAT per DRHP = ₹210 Cr (after ₹35 Cr exceptional charges). "
         "Annualised credit loss rate = ₹965 Cr / avg AUM ₹18,265 Cr = 5.29%. Source: DRHP Mar-2026.", "info")

    # Sector breakdown — latest period (always all sectors, ignore filter)
    st.markdown(f'<div class="section-header">By Sector — {lbl}</div>', unsafe_allow_html=True)
    _snap_all = get_latest_period_data(fin_df).dropna(subset=["roa_pct", "roe_pct"])
    sector_avg = _snap_all.groupby("sector").agg(
        roa=("roa_pct", "mean"),
        roe=("roe_pct", "mean"),
    ).reset_index().dropna().sort_values("roa", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="ROA %", x=sector_avg["sector"], y=sector_avg["roa"],
                         marker_color=COLOR["primary"],
                         text=sector_avg["roa"].round(1), textposition="outside",
                         textfont=dict(family=CHART_MONO, size=10)))
    fig.add_trace(go.Bar(name="ROE %", x=sector_avg["sector"], y=sector_avg["roe"],
                         marker_color=COLOR["accent"],
                         text=sector_avg["roe"].round(1), textposition="outside",
                         textfont=dict(family=CHART_MONO, size=10)))
    fig.update_layout(barmode="group", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                      title=_title_dict(f"ROA & ROE by Sector ({lbl})"),
                      font=dict(color=COLOR["text_secondary"], family=CHART_FONT),
                      height=420,
                      margin=dict(t=82, b=80, l=10, r=24),
                      legend=dict(font=dict(family=CHART_FONT, size=11),
                                  bgcolor="rgba(255,255,255,0.85)", borderwidth=0,
                                  orientation="h", yanchor="top", y=0.99,
                                  xanchor="right", x=1),
                      xaxis=dict(showticklabels=True, showgrid=False,
                                 tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)", title="",
                                 tickfont=dict(family=CHART_FONT, size=12, color=COLOR["text"]),
                                 tickangle=0),
                      yaxis=dict(showgrid=False,
                                 tickcolor="rgba(0,0,0,0)", title=""),
                      hoverlabel=HOVER_LABEL,
                      uniformtext_minsize=8, uniformtext_mode="hide")
    st.plotly_chart(fig, use_container_width=True)

    # PAT trend — top 10
    st.markdown(f'<div class="section-header">PAT Trend — Top 10 Companies (incl. {lbl})</div>',
                unsafe_allow_html=True)
    top10_names = latest_snap.nlargest(10, "pat_cr")["name"].tolist()
    chart_df = get_chart_periods(fin_filtered)
    pat_trend = chart_df[chart_df["name"].isin(top10_names)][["name", "period", "pat_cr"]].dropna()
    pat_trend = pat_trend.copy()
    pat_trend["period"] = pat_trend["period"].astype(str).replace("9MFY26", "9MFY26 (Ann.)")

    fig = px.line(pat_trend, x="period", y="pat_cr", color="name",
                  color_discrete_sequence=MV_PALETTE,
                  labels={"pat_cr": "PAT (₹ Crore)", "period": "Period"},
                  title=f"Profit After Tax Trend — incl. {lbl} (₹ Crore)", height=460,
                  category_orders={"period": PERIOD_ORDER_ANN},
                  custom_data=["name"])
    fig.update_traces(mode="lines+markers")
    chart_layout(fig)
    # Apply after chart_layout (which resets all hovertemplates to just %{x})
    fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>PAT: ₹%{y:,.0f} Cr<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("9MFY26 (Ann.) = 9-month PAT annualised (×4/3) to be comparable with full-year figures.")
    note("KreditBee 9MFY26 — PAT & ROA adjusted for one-time exceptional items:  "
         "Reported 9M PAT ₹341 Cr − ₹152 Cr exceptional (₹104 Cr GST provision reversal, Karnataka HC Dec 2025 "
         "+ ₹48 Cr DTA recognition) = Adjusted 9M PAT ₹189 Cr × 4/3 = Annualised PAT ₹252 Cr.  "
         "Adjusted ROA = ₹252 Cr ÷ avg loan book ₹7,049 Cr [(₹5,649 + ₹8,448) ÷ 2] = 3.58%.", "warning")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: ASSET QUALITY (GNPA + Annualized Losses combined)
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    note("Annualized Losses = (Net Provisions + Write-offs − Recoveries) ÷ Loan Book — "
         "the P&L cost of defaults. GNPA is a stock/point-in-time measure of bad loans.")

    lbl = latest_period_label(fin_filtered)
    chart_df = get_chart_periods(fin_filtered)
    latest_snap_all = get_latest_period_data(fin_filtered)
    all_gnpa = latest_snap_all.dropna(subset=["gnpa_pct"]).sort_values("gnpa_pct", ascending=True)
    all_loss = latest_snap_all.dropna(subset=["credit_loss_rate_pct"]).sort_values("credit_loss_rate_pct", ascending=True)

    # ── Row 1: GNPA bar | Annualized Losses bar ──────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        fig = make_hbar(all_gnpa, "gnpa_pct", "name", COLOR["success"],
                        f"GNPA % ({period_label_for(all_gnpa)})",
                        hover_text=all_gnpa["period"].map(lambda p: PERIOD_SHORT.get(p, p)).values,
                        text_suffix="%")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Point-in-time metric — 9MFY26 uses Q3 value, no annualisation.")
    with col2:
        fig = make_hbar(all_loss, "credit_loss_rate_pct", "name", COLOR["success"],
                        f"Annualized Losses ({period_label_for(all_loss)})",
                        hover_text=all_loss["period"].map(lambda p: PERIOD_SHORT_ANN.get(p, p)).values,
                        text_suffix="%")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("9MFY26: annualised credit losses (×4/3) ÷ avg loan book.")

    # ── Row 2: Latest GNPA by Sector | Latest Annualized Losses by Sector ────
    # Always use unfiltered data so all sectors appear
    _snap_cq_all = get_latest_period_data(fin_df)
    _all_gnpa_all = _snap_cq_all.dropna(subset=["gnpa_pct"])
    _all_loss_all = _snap_cq_all.dropna(subset=["credit_loss_rate_pct"])

    st.markdown('<div class="section-header">By Sector — Latest Period</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        sector_gnpa_latest = (
            _all_gnpa_all.groupby("sector")["gnpa_pct"].mean().reset_index()
            .sort_values("gnpa_pct", ascending=True)
        )
        fig = make_hbar(sector_gnpa_latest, "gnpa_pct", "sector", COLOR["primary"],
                        "GNPA % by Sector", text_suffix="%")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        sector_loss_latest = (
            _all_loss_all.groupby("sector")["credit_loss_rate_pct"].mean().reset_index()
            .sort_values("credit_loss_rate_pct", ascending=True)
        )
        fig = make_hbar(sector_loss_latest, "credit_loss_rate_pct", "sector", COLOR["primary"],
                        "Annualized Losses % by Sector", text_suffix="%")
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Heatmaps side by side ─────────────────────────────────────────
    st.markdown('<div class="section-header">Heatmaps</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    def _heatmap_fig(df_source, value_col, names, title_str):
        hm_df = df_source[df_source["name"].isin(names)].pivot_table(
            index="name", columns="period", values=value_col)
        col_order = [c for c in PERIOD_ORDER if c in hm_df.columns]
        hm_df = hm_df[col_order]
        hm_df.index = [truncate_name(n) for n in hm_df.index]
        fig = go.Figure(data=go.Heatmap(
            z=hm_df.values, x=hm_df.columns.tolist(), y=hm_df.index.tolist(),
            colorscale=[[0, COLOR["success"]], [0.5, "#FCC945"], [1, COLOR["danger"]]],
            text=[[f"{v:.1f}%" if not np.isnan(v) else "N/A" for v in row] for row in hm_df.values],
            texttemplate="%{text}", showscale=True,
        ))
        fig.update_layout(
            title=_title_dict(title_str),
            paper_bgcolor=CHART_BG,
            height=max(340, len(names) * 22),
            font=dict(color=COLOR["text_secondary"], family=CHART_FONT, size=11),
            margin=dict(t=82, b=30, l=10, r=30),
            xaxis=dict(title=""), yaxis=dict(title=""),
            hoverlabel=HOVER_LABEL,
        )
        fig.update_traces(hovertemplate="%{y} %{x}<extra></extra>")
        return fig

    hm_source = chart_df
    stressed_35 = all_gnpa.nlargest(35, "gnpa_pct")["name"].tolist()
    top35_loss = all_loss.nlargest(35, "credit_loss_rate_pct")["name"].tolist()

    with col1:
        fig = _heatmap_fig(hm_source, "gnpa_pct", stressed_35, f"GNPA % Heatmap (to {lbl})")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = _heatmap_fig(hm_source, "credit_loss_rate_pct", top35_loss,
                           f"Annualized Losses % Heatmap (to {lbl})")
        st.plotly_chart(fig, use_container_width=True)

    # ── Scatter: Annualized Losses vs GNPA ───────────────────────────────────
    st.markdown('<div class="section-header">Annualized Losses vs GNPA</div>', unsafe_allow_html=True)
    scatter_df = latest_snap_all.dropna(subset=["credit_loss_rate_pct", "gnpa_pct", "loan_book_cr"])
    if not scatter_df.empty:
        fig = px.scatter(scatter_df, x="gnpa_pct", y="credit_loss_rate_pct",
                         size="loan_book_cr", color="sector", hover_name="name",
                         color_discrete_sequence=MV_PALETTE,
                         labels={"gnpa_pct": "GNPA %", "credit_loss_rate_pct": "Annualized Losses %"},
                         title=f"Annualized Losses vs GNPA — {lbl} (bubble = loan book)", height=500)
        chart_layout(fig)
        fig.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "GNPA = %{x:.1f}%<br>"
                "Ann. Losses = %{y:.1f}%"
                "<extra></extra>"
            )
        )
        fig.update_layout(
            xaxis=dict(title="GNPA %", title_font=dict(size=12, family=CHART_FONT),
                       autorange=True, tickvals=None, ticktext=None),
            yaxis=dict(title="Annualized Losses %", title_font=dict(size=12, family=CHART_FONT),
                       autorange=True, tickvals=None, ticktext=None),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Waterfall: FY2021 → FY2025 change ────────────────────────────────────
    st.markdown('<div class="section-header">Annualized Losses Change — FY2021 to FY2025</div>',
                unsafe_allow_html=True)
    st.caption("Uses FY2021 vs FY2025 annual data only — 9MFY26 excluded to avoid period mismatch.")
    ann = annual_only(fin_filtered)
    fy21 = ann[ann["period"] == "FY2021"][["name", "credit_loss_rate_pct"]].rename(
        columns={"credit_loss_rate_pct": "fy21"})
    fy25 = ann[ann["period"] == "FY2025"][["name", "credit_loss_rate_pct"]].rename(
        columns={"credit_loss_rate_pct": "fy25"})
    wf = fy21.merge(fy25, on="name").dropna()
    wf["change"] = wf["fy25"] - wf["fy21"]
    wf = wf.sort_values("change")
    wf["color"] = wf["change"].apply(lambda x: COLOR["success"] if x < 0 else COLOR["danger"])
    wf["label"] = wf["name"].apply(truncate_name)
    fig = go.Figure(go.Bar(x=wf["change"], y=wf["label"], orientation="h",
                           marker_color=wf["color"],
                           text=wf["change"].round(2), textposition="outside",
                           textfont=dict(family=CHART_MONO, size=10),
                           cliponaxis=False))
    wf_max = wf["change"].abs().max() if not wf.empty else 1
    fig.update_layout(
        title=_title_dict("Change in Annualized Losses: FY2021 → FY2025 (green = improved)"),
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT),
        height=bar_chart_height(len(wf)),
        xaxis=dict(title="", showgrid=False, showticklabels=False,
                   range=[-(wf_max * 1.5), wf_max * 1.5], zeroline=True,
                   zerolinecolor="#EAEAEA", zerolinewidth=1, tickcolor="rgba(0,0,0,0)"),
        yaxis=dict(showgrid=False, tickcolor="rgba(0,0,0,0)", title=""),
        margin=dict(t=82, b=20, l=10, r=130),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e4ede6",
                        font=dict(family=CHART_FONT, size=12)),
    )
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 8: TRENDS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[7]:
    lbl = latest_period_label(fin_filtered)
    latest_snap = get_latest_period_data(fin_filtered)
    top10 = latest_snap.nlargest(10, "loan_book_cr")["name"].tolist()
    chart_df = get_chart_periods(fin_filtered)

    # Stacked area — loan book (stock, Q3 as-is)
    st.markdown(f'<div class="section-header">Loan Book Growth — Top 10 (to {lbl})</div>',
                unsafe_allow_html=True)
    area_df = chart_df[chart_df["name"].isin(top10)][["name", "period", "loan_book_cr"]].dropna()
    fig = px.area(area_df, x="period", y="loan_book_cr", color="name",
                  color_discrete_sequence=MV_PALETTE,
                  title=f"Loan Book Growth — Top 10 NBFCs (₹ Crore, to {lbl})", height=460,
                  category_orders={"period": PERIOD_ORDER})
    chart_layout(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("9MFY26 loan book = Q3 FY26 closing loan book (point-in-time, not annualised).")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="section-header">NII Trend (to {lbl})</div>', unsafe_allow_html=True)
        nii_df = chart_df[chart_df["name"].isin(top10)][
            ["name", "period", "net_interest_income_cr"]].dropna()
        nii_df = nii_df.copy()
        nii_df["period"] = nii_df["period"].astype(str).replace("9MFY26", "9MFY26 (Ann.)")
        fig = px.line(nii_df, x="period", y="net_interest_income_cr", color="name",
                      color_discrete_sequence=MV_PALETTE,
                      title=f"Net Interest Income (₹ Crore, to {lbl})", height=420,
                      category_orders={"period": PERIOD_ORDER_ANN})
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("9MFY26 (Ann.) = 9-month NII annualised (×4/3) to be comparable with full-year figures.")

    with col2:
        st.markdown(f'<div class="section-header">Industry Assets by RBI Layer (to {lbl})</div>',
                    unsafe_allow_html=True)
        layer_df = chart_df.groupby(["period", "rbi_layer"])["total_assets_cr"].sum().reset_index()
        fig = px.area(layer_df, x="period", y="total_assets_cr", color="rbi_layer",
                      color_discrete_map={"Upper": "#144835", "Middle": "#2CA076", "Base": "#73757A"},
                      title=f"Total Industry Assets by RBI Layer (₹ Crore, to {lbl})", height=420,
                      category_orders={"period": PERIOD_ORDER})
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("9MFY26 assets = Q3 FY26 closing total assets (point-in-time).")

    # ROA trend
    st.markdown(f'<div class="section-header">Return on Assets Trend (to {lbl})</div>',
                unsafe_allow_html=True)
    roa_df = chart_df[chart_df["name"].isin(top10)][["name", "period", "roa_pct"]].dropna()
    fig = px.line(roa_df, x="period", y="roa_pct", color="name",
                  color_discrete_sequence=MV_PALETTE,
                  title=f"ROA % Trend — Top 10 NBFCs (to {lbl})", height=460,
                  category_orders={"period": PERIOD_ORDER})
    chart_layout(fig)
    st.plotly_chart(fig, use_container_width=True)

    # PAT CAGR ranking using FY2021→FY2025
    st.markdown('<div class="section-header">PAT CAGR — FY2021 to FY2025</div>',
                unsafe_allow_html=True)
    pat_cagr = compute_cagr(fin_filtered, "pat_cr").dropna()
    # filter out extreme negatives (loss → profit)
    pat_cagr = pat_cagr[pat_cagr["cagr_pct"].between(-50, 200)]
    top_pat = pat_cagr.sort_values("cagr_pct", ascending=False)
    fig = make_hbar(top_pat, "cagr_pct", "name", COLOR["accent"],
                    "PAT CAGR % (FY21–25)",
                    hover_text=["FY21–FY25"] * len(top_pat), text_suffix="%")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: DEEP DIVE
# ─────────────────────────────────────────────────────────────────────────────
def deep_dive_tab(fin_filtered, nbfc_filtered):
    companies_with_data = (
        fin_filtered[fin_filtered["has_financials"] == 1]["name"]
        .dropna().unique().tolist()
    )

    # Default to KreditBee when nothing is selected
    if not st.session_state.get("dd_company_select") and "KreditBee" in companies_with_data:
        st.session_state["dd_company_select"] = "KreditBee"

    # ── Company selector + inline filter icon ─────────────────────────────────
    dd_base = nbfc_filtered[nbfc_filtered["name"].isin(companies_with_data)]
    avail_layers  = sorted(dd_base["rbi_layer"].dropna().unique().tolist())
    avail_sectors = sorted(dd_base["sector"].dropna().unique().tolist())

    # Read persisted filter values
    dd_layer = st.session_state.get("dd_layer_filter", "All")
    dd_sect  = st.session_state.get("dd_sector_filter", "All")

    dd_filtered = dd_base.copy()
    if dd_layer != "All":
        dd_filtered = dd_filtered[dd_filtered["rbi_layer"] == dd_layer]
    if dd_sect != "All":
        dd_filtered = dd_filtered[dd_filtered["sector"] == dd_sect]
    filtered_companies = sorted(dd_filtered["name"].dropna().unique().tolist())
    if not filtered_companies:
        filtered_companies = sorted(companies_with_data)

    # ── Quick-select shortcut chips ──────────────────────────────────────────
    # (full_name, display_label) — all chips rendered at equal width
    QUICK_NBFCS = [
        ("KreditBee",                      "KreditBee"),
        ("Fibe",                           "Fibe"),
        ("Kissht",                         "Kissht"),
        ("Moneyview",                      "Moneyview"),
        ("Bajaj Finance",                  "Bajaj Finance"),
        ("SBI Cards and Payment Services", "SBI Cards"),
    ]
    # Only show chips for companies that exist in the current data
    available_quick = [(n, lbl) for n, lbl in QUICK_NBFCS if n in companies_with_data]

    if available_quick:
        st.markdown(
            '<p style="font-size:0.68rem;font-weight:600;color:#A0A2A8;'
            'text-transform:uppercase;letter-spacing:0.05em;margin:0 0 0.3rem 0;">'
            'Featured</p>',
            unsafe_allow_html=True,
        )
        # Equal-width columns for all chips — no trailing spacer so each button is maximally wide
        chip_cols = st.columns(len(available_quick), gap="small")
        for i, (name, label) in enumerate(available_quick):
            with chip_cols[i]:
                if st.button(label, key=f"qs_btn_{name}", use_container_width=True):
                    st.session_state["dd_company_select"] = name
                    st.session_state["dd_layer_filter"] = "All"
                    st.session_state["dd_sector_filter"] = "All"

    sel_col, filter_col = st.columns([14, 1])
    with sel_col:
        _default = st.session_state.get("dd_company_select")
        _default_idx = (
            filtered_companies.index(_default)
            if _default in filtered_companies else None
        )
        selected = st.selectbox(
            "Select an NBFC to explore",
            filtered_companies,
            index=_default_idx,
            placeholder="Search or type a company name…",
            key="dd_company_select",
            label_visibility="collapsed",
        )
        st.markdown(
            '<p style="font-size:0.72rem;color:#A0A2A8;margin:-0.35rem 0 0 0.1rem;">'
            'Search or select any NBFC to explore its full financial profile</p>',
            unsafe_allow_html=True,
        )
    with filter_col:
        with st.popover(" ", use_container_width=True):
            st.markdown(
                "<div style='font-size:0.75rem;font-weight:600;color:#28292D;"
                "margin-bottom:0.6rem;'>Narrow the list</div>",
                unsafe_allow_html=True,
            )
            st.selectbox("RBI Layer", ["All"] + avail_layers, key="dd_layer_filter")
            st.selectbox("Sector",    ["All"] + avail_sectors, key="dd_sector_filter")

    # Single combined JS injection: chip highlight + selectbox bold value
    _active_label = dict(available_quick).get(
        st.session_state.get("dd_company_select", ""), ""
    ) if available_quick else ""
    _all_labels = json.dumps([lbl for _, lbl in available_quick]) if available_quick else "[]"
    components.html(f"""
<script>
(function() {{
  var activeLabel = {json.dumps(_active_label)};
  var chipLabels  = {_all_labels};

  // ── One-time setup: style injection + document-level event delegation ───────
  (function() {{
    var doc = window.parent.document;
    if (doc._nbfcSelectReady) return;
    doc._nbfcSelectReady = true;

    // CSS: light-grey selection colour + permanently bold the selected value display
    if (!doc.getElementById('nbfc-sel-style')) {{
      var s = doc.createElement('style');
      s.id = 'nbfc-sel-style';
      s.textContent = [
        '[data-testid="stSelectbox"] input::selection {{ background: #3B7DD8 !important; color: #ffffff !important; }}',
        /* Bold the display-value div inside the NBFC selectbox at all times */
        '[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child > div > div {{',
        '  font-weight: 700 !important;',
        '  font-size: 1.0rem !important;',
        '  color: #1C1E23 !important;',
        '  letter-spacing: -0.01em !important;',
        '}}'
      ].join(' ');
      doc.head.appendChild(s);
    }}

    // Module-level cache: stores the NBFC name last seen in the closed state
    var _nbfcVal = '';

    // Helper: is this element inside the NBFC company selectbox?
    function getNbfcBox(target) {{
      if (!target) return null;
      var box = target.closest('[data-testid="stSelectbox"]');
      if (!box) return null;
      var lbl = box.querySelector('[data-testid="stWidgetLabel"] p');
      if (!lbl || lbl.textContent.trim() !== 'Select an NBFC to explore') return null;
      return box;
    }}

    // Read the displayed name from the closed-state display div
    function readDisplayVal(box) {{
      var sel = box.querySelector('[data-baseweb="select"]');
      if (!sel) return '';
      // The selected-value text sits in a leaf div alongside the hidden input
      var inp = sel.querySelector('input');
      if (!inp) return '';
      var container = inp.parentElement;
      if (!container) return '';
      for (var i = 0; i < container.children.length; i++) {{
        var child = container.children[i];
        if (child.tagName === 'DIV') {{
          var t = child.textContent.trim();
          if (t.length > 1) return t;
        }}
      }}
      // Fallback: first leaf div with text anywhere in the selectbox
      var found = '';
      sel.querySelectorAll('div').forEach(function(d) {{
        if (!found && d.children.length === 0) {{
          var t = d.textContent.trim();
          if (t.length > 1) found = t;
        }}
      }});
      return found;
    }}

    // mousedown fires BEFORE BaseWeb hides the display div — cache the name only.
    doc.addEventListener('mousedown', function(e) {{
      var box = getNbfcBox(e.target);
      if (!box) return;
      var v = readDisplayVal(box);
      if (v) _nbfcVal = v;
    }});

    // focusin: write the cached NBFC name into the input and apply a grey
    // highlight. Re-query inp fresh inside the timeout (avoids stale reference)
    // and drop the activeElement guard (which was silently bailing early).
    // Direct inp.value write keeps BaseWeb out of filter mode → single-click
    // option selection continues to work.
    doc.addEventListener('focusin', function(e) {{
      if (!e.target || e.target.tagName !== 'INPUT') return;
      var box = getNbfcBox(e.target);
      if (!box) return;
      var val = _nbfcVal;
      if (!val) return;

      setTimeout(function() {{
        var inp = box.querySelector('input');  // fresh query — no stale ref
        if (!inp) return;
        inp.value = val;
        inp.style.setProperty('color',         '#1a1a1a', 'important');
        inp.style.setProperty('background',    '#E0E2E8', 'important');
        inp.style.setProperty('border-radius', '2px',     'important');

        function clearHL() {{
          inp.style.removeProperty('color');
          inp.style.removeProperty('background');
          inp.style.removeProperty('border-radius');
          inp.value = '';
        }}
        inp.addEventListener('keydown', clearHL, {{ once: true }});
        setTimeout(clearHL, 6000);
      }}, 50);
    }});

    doc.addEventListener('focusout', function(e) {{
      var box = getNbfcBox(e.target);
      if (box) {{
        // Reset any injected input styles when dropdown closes
        var inp2 = box.querySelector('input');
        if (inp2) {{
          inp2.style.removeProperty('color');
          inp2.style.removeProperty('background');
          inp2.style.removeProperty('border-radius');
        }}
        // Refresh the cache and re-apply bold styling after dropdown closes
        var v = readDisplayVal(box);
        if (v) _nbfcVal = v;
        setTimeout(applyStyles, 80);
        setTimeout(applyStyles, 300);
      }}
    }});

    // MutationObserver: re-apply bold styling whenever the selectbox DOM changes
    var _observer = new MutationObserver(function(mutations) {{
      var relevant = mutations.some(function(m) {{
        var node = m.target;
        return node.closest && node.closest('[data-testid="stSelectbox"]');
      }});
      if (relevant) applyStyles();
    }});
    _observer.observe(doc.body, {{ childList: true, subtree: true }});
  }})();

  function applyStyles() {{
    var doc = window.parent.document;

    // 1. Chip button highlight
    doc.querySelectorAll('button[data-testid="stBaseButton-secondary"],'
      + 'button[data-testid="stBaseButton-primary"]').forEach(function(btn) {{
      var txt = (btn.querySelector('p') || btn).textContent.trim();
      if (!chipLabels.includes(txt)) return;
      btn.style.borderRadius = '999px';
      btn.style.minHeight    = '1.85rem';
      btn.style.fontSize     = '0.76rem';
      btn.style.transition   = 'background 0.15s, border-color 0.15s';
      if (txt === activeLabel) {{
        btn.style.background = '#E8F5EE';
        btn.style.border     = '1.5px solid #2CA076';
        btn.style.color      = '#144835';
        btn.style.fontWeight = '600';
        btn.style.boxShadow  = '0 0 0 2px rgba(44,160,118,0.20)';
      }} else {{
        btn.style.background = '#FFFFFF';
        btn.style.border     = '1.5px solid #D0D2D8';
        btn.style.color      = '#28292D';
        btn.style.fontWeight = '500';
        btn.style.boxShadow  = 'none';
      }}
    }});

    // Bold selected-value styling is handled by the injected CSS rule above.
  }}

  applyStyles();
  setTimeout(applyStyles, 100);
  setTimeout(applyStyles, 400);
}})();
</script>
""", height=0, scrolling=False)

    if selected is None:
        st.markdown(
            '<div class="nbfc-select-hint">&#8593;&nbsp; Pick a company above to explore its full financial profile</div>',
            unsafe_allow_html=True,
        )

    if selected:
        company_info_rows = nbfc_filtered[nbfc_filtered["name"] == selected]
        company_info = company_info_rows.iloc[0] if not company_info_rows.empty else None
        company_fin = fin_filtered[fin_filtered["name"] == selected].sort_values("period")

        # Header: badges + data source
        if company_info is not None:
            layer_colors = {"Upper": "#144835", "Middle": "#217858", "Base": "#73757A"}
            layer = company_info.get("rbi_layer", "Unknown")
            dq = company_info.get("data_quality", "")
            listed_val = company_info.get("listed", 0)
            badges = []
            badges.append(
                f'<span style="background:{layer_colors.get(layer,"#64748b")};'
                f'color:white;padding:3px 10px;border-radius:4px;font-size:12px;'
                f'font-weight:600">{layer} Layer</span>'
            )
            if dq == "audited":
                badges.append(
                    '<span style="background:#D7F4E9;color:#144835;padding:3px 10px;'
                    'border-radius:4px;font-size:12px;font-weight:600;'
                    'border:1px solid #a7f3d0">✓ Audited</span>'
                )
            elif dq == "DRHP":
                badges.append(
                    '<span style="background:#EFF6FF;color:#1e40af;padding:3px 10px;'
                    'border-radius:4px;font-size:12px;font-weight:600;'
                    'border:1px solid #bfdbfe">📄 DRHP</span>'
                )
            elif dq == "estimated":
                badges.append('<span class="estimated-badge">⚠️ Estimated Data</span>')
            elif dq == "unverified":
                badges.append('<span class="unverified-badge">❌ Unverified</span>')
            if listed_val:
                badges.append(
                    '<span style="background:#EFF6FF;color:#1e40af;padding:3px 10px;'
                    'border-radius:4px;font-size:12px;font-weight:600;'
                    'border:1px solid #bfdbfe">Listed</span>'
                )

            # ── Ranking badges: check if this NBFC tops any metric ──────────
            _all_latest = get_latest_period_data(fin_filtered)
            _rank_checks = [
                ("loan_book_cr", "🏆 Biggest AUM"),
                ("pat_cr",       "🏆 Highest PAT"),
                ("roa_pct",      "🏆 Best ROA"),
                ("roe_pct",      "🏆 Best ROE"),
            ]
            _rank_style = (
                'background:#FEF9C3;color:#854D0E;padding:3px 10px;border-radius:4px;'
                'font-size:12px;font-weight:600;border:1px solid #FDE68A;'
            )
            for col, label in _rank_checks:
                if col in _all_latest.columns:
                    _col_data = _all_latest[col].dropna()
                    if not _col_data.empty:
                        _best_name = _all_latest.loc[_col_data.idxmax(), "name"]
                        if _best_name == selected:
                            badges.append(f'<span style="{_rank_style}">{label}</span>')

            st.markdown(" &nbsp; ".join(badges), unsafe_allow_html=True)

            st.markdown("")

        has_q3 = "FY2026-Q3" in company_fin["period"].values

        # Key metrics
        lbl = latest_period_label(company_fin)
        latest_snap = get_latest_period_data(company_fin)
        if not latest_snap.empty:
            r = latest_snap.iloc[0]
            st.markdown(
                f'<div style="font-size:0.72rem;color:#6b7280;font-family:\'Inter\',sans-serif;'
                f'margin-bottom:0.25rem;">Key metrics as of <strong>{lbl}</strong></div>',
                unsafe_allow_html=True,
            )
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            m1.metric("Loan Book", f"₹{r['loan_book_cr']:,.0f} Cr" if pd.notna(r.get("loan_book_cr")) else "N/A")
            m2.metric("Total Assets", f"₹{r['total_assets_cr']:,.0f} Cr" if pd.notna(r.get("total_assets_cr")) else "N/A")
            _ann_sfx = " (Ann.)" if has_q3 else ""
            m3.metric(f"NII{_ann_sfx}", f"₹{r['net_interest_income_cr']:,.0f} Cr" if pd.notna(r.get("net_interest_income_cr")) else "N/A")
            m4.metric(f"PAT{_ann_sfx}", f"₹{r['pat_cr']:,.0f} Cr" if pd.notna(r.get("pat_cr")) else "N/A")
            m5.metric("GNPA %", f"{r['gnpa_pct']:.2f}%" if pd.notna(r.get("gnpa_pct")) else "N/A")
            m6.metric("ROA %", f"{r['roa_pct']:.2f}%" if pd.notna(r.get("roa_pct")) else "N/A")

        chart_df = get_chart_periods(company_fin)

        col1, col2 = st.columns(2)
        DD_MARGIN = dict(t=82, b=120, l=10, r=24)
        DD_LEGEND = dict(
            font=dict(family=CHART_FONT, size=11),
            bgcolor="rgba(255,255,255,0)", borderwidth=0,
            orientation="h", yanchor="bottom", y=-0.38,
            xanchor="left", x=0, title_text="",
        )
        with col1:
            bar_df = chart_df[["period", "total_assets_cr", "loan_book_cr"]].rename(
                columns={"total_assets_cr": "Total Assets", "loan_book_cr": "Loan Book"})
            fig = px.bar(bar_df, x="period", y=["Total Assets", "Loan Book"],
                         barmode="group", text_auto=".3s",
                         color_discrete_sequence=["#144835", "#2CA076"],
                         title=f"Assets & Loan Book (₹ Crore)", height=400,
                         category_orders={"period": PERIOD_ORDER})
            fig.update_traces(textposition="outside", textfont=dict(family=CHART_MONO, size=11),
                              cliponaxis=False)
            chart_layout(fig)
            fig.update_layout(margin=DD_MARGIN, legend=DD_LEGEND)
            fig.update_traces(hovertemplate="₹%{y:,.0f} Cr<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            # Require PAT; NII is optional — plot whichever series has data
            pat_df = chart_df[["period", "pat_cr"]].dropna(subset=["pat_cr"]).copy()
            nii_df = chart_df[["period", "net_interest_income_cr"]].dropna(subset=["net_interest_income_cr"]).copy()
            pat_df["period"] = pat_df["period"].astype(str).replace("9MFY26", "9MFY26 (Ann.)")
            nii_df["period"] = nii_df["period"].astype(str).replace("9MFY26", "9MFY26 (Ann.)")
            has_nii = not nii_df.empty
            fig = go.Figure()
            if has_nii:
                fig.add_trace(go.Scatter(
                    x=nii_df["period"], y=nii_df["net_interest_income_cr"],
                    mode="lines+markers", name="Revenues",
                    line=dict(color="#144835", width=2),
                    marker=dict(size=6),
                    hovertemplate="₹%{y:,.0f} Cr<extra>Revenues</extra>",
                ))
            fig.add_trace(go.Scatter(
                x=pat_df["period"], y=pat_df["pat_cr"],
                mode="lines+markers", name="PAT",
                line=dict(color="#DE5E2B", width=2),
                marker=dict(size=6),
                hovertemplate="₹%{y:,.0f} Cr<extra>PAT</extra>",
            ))
            title_txt = "Revenues\u00a0&\u00a0PAT (₹\u00a0Crore)" if has_nii else "PAT (₹\u00a0Crore)\u00a0—\u00a0Revenues not disclosed"
            fig.update_layout(
                title=_title_dict(title_txt),
                height=400,
                xaxis=dict(categoryorder="array", categoryarray=PERIOD_ORDER_ANN,
                           showgrid=False, tickcolor="rgba(0,0,0,0)",
                           linecolor="rgba(0,0,0,0)", tickfont=dict(family=CHART_FONT, size=11)),
                yaxis=dict(showgrid=False, tickcolor="rgba(0,0,0,0)"),
                paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(color=COLOR["text_secondary"], family=CHART_FONT),
                hoverlabel=HOVER_LABEL,
            )
            chart_layout(fig)
            # Re-apply per-trace hovertemplates after chart_layout (which resets all to %{x})
            for trace in fig.data:
                trace.update(hovertemplate="₹%{y:,.0f} Cr<extra>" + trace.name + "</extra>")
            fig.update_layout(margin=DD_MARGIN, legend=DD_LEGEND)
            st.plotly_chart(fig, use_container_width=True)
            if selected == "KreditBee" and has_q3:
                st.caption("* 9MFY26 PAT annualised (×4/3) and adjusted for one-time exceptional items: "
                           "₹341 Cr reported − ₹152 Cr = ₹189 Cr × 4/3 = ₹252 Cr annualised.")
                note("9MFY26 PAT annualised and adjusted to ~₹252 Cr (adj. 9M PAT ~₹189 Cr × 4/3, "
                     "ex ~₹152 Cr one-time items). "
                     "NII (₹1,304 Cr annualised) is unaffected by exceptional items.", "warning")
            if selected == "Moneyview" and has_q3:
                st.caption("* 9MFY26 PAT annualised (×4/3) using pre-exceptional PAT: "
                           "₹245 Cr × 4/3 = ₹327 Cr annualised.")

        col3, col4 = st.columns(2)
        with col3:
            gnpa_df = chart_df[["period", "gnpa_pct"]].dropna()
            fig = px.line(gnpa_df, x="period", y="gnpa_pct",
                          title=f"GNPA % Trend", markers=True, height=380,
                          category_orders={"period": PERIOD_ORDER})
            fig.update_traces(line_color=COLOR["danger"], marker_color=COLOR["danger"])
            chart_layout(fig)
            fig.update_layout(margin=DD_MARGIN, showlegend=False)
            fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)
        with col4:
            ror_df = chart_df[["period", "roa_pct", "roe_pct"]].dropna().rename(
                columns={"roa_pct": "ROA %", "roe_pct": "ROE %"})
            fig = px.line(ror_df, x="period", y=["ROA %", "ROE %"],
                          color_discrete_sequence=["#144835", "#2CA076"],
                          title=f"ROA & ROE %", markers=True, height=380,
                          category_orders={"period": PERIOD_ORDER})
            chart_layout(fig)
            fig.update_layout(margin=DD_MARGIN, legend=DD_LEGEND)
            fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)
            if selected == "KreditBee" and has_q3:
                st.caption("* 9MFY26 ROA & ROE annualised (×4/3) and adjusted for one-time exceptional items "
                           "(₹341 Cr reported PAT → ₹252 Cr after −₹152 Cr exceptional).")
            if selected == "Moneyview" and has_q3:
                st.caption("* 9MFY26 ROA & ROE annualised (×4/3) using pre-exceptional PAT "
                           "(₹245 Cr × 4/3 = ₹327 Cr annualised).")

        cl_df = chart_df[["period", "credit_loss_rate_pct"]].dropna()
        fig = px.line(cl_df, x="period", y="credit_loss_rate_pct",
                      title=f"Annualized Losses %", markers=True, height=380,
                      category_orders={"period": PERIOD_ORDER})
        fig.add_hline(y=2.0, line_dash="dot", line_color=COLOR["warning"],
                      annotation_text="2% reference")
        chart_layout(fig)
        fig.update_layout(margin=DD_MARGIN, showlegend=False)
        fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)

        # Financial table
        st.markdown('<div class="section-header">Financial Summary</div>', unsafe_allow_html=True)
        display_cols = ["period", "loan_book_cr", "total_assets_cr", "equity_cr",
                        "net_interest_income_cr", "pat_cr", "credit_loss_rate_pct",
                        "gnpa_pct", "roa_pct", "roe_pct"]
        _table_src = chart_df[[c for c in display_cols if c in chart_df.columns]].copy()
        _table_src["period"] = _table_src["period"].astype(str).replace("9MFY26", "9MFY26 (Ann.)")
        table_df = _table_src.set_index("period").T
        table_df.index = ["Loan Book (₹ Cr)", "Total Assets (₹ Cr)", "Equity (₹ Cr)",
                          "NII (₹ Cr)", "PAT (₹ Cr)", "Annualized Losses %",
                          "GNPA %", "ROA %", "ROE %"][:len(table_df)]
        st.dataframe(table_df.style.format("{:.1f}", na_rep="N/A"), use_container_width=True)
        if has_q3:
            st.caption("9MFY26: NII & PAT are annualised (×4/3). Credit losses are raw 9-month values. ROA & ROE use annualised PAT.")
        if has_q3 and selected == "KreditBee":
            note("KreditBee 9MFY26 — PAT & ROA adjusted for one-time exceptional items:  "
                 "Reported 9M PAT ₹341 Cr − ₹152 Cr exceptional (₹104 Cr GST provision reversal, Karnataka HC Dec 2025 "
                 "+ ₹48 Cr DTA recognition) = Adjusted 9M PAT ₹189 Cr × 4/3 = Annualised PAT ₹252 Cr.  "
                 "Adjusted ROA = ₹252 Cr ÷ avg loan book ₹7,049 Cr [(₹5,649 + ₹8,448) ÷ 2] = 3.58%.", "warning")
        if has_q3 and selected == "Moneyview":
            note("Loan book = managed AUM (on-book + off-book DLG). "
                 "9MFY26: ROA & ROE use PAT before exceptional items (₹245 Cr, 9M → annualised ₹327 Cr). "
                 "Reported 9M PAT = ₹210 Cr (after ₹35 Cr one-time charges). "
                 "Annualised loss rate = ₹965 Cr / avg AUM ₹18,265 Cr = 5.29%. Source: DRHP Mar-2026.", "info")
        if selected == "Kissht":
            note("Kissht FY2025 (latest): ROA = ₹161 Cr PAT / avg Loan Book AUM ₹3,346 Cr = 4.81% "
                 "(DRHP reported 7.14% using avg total assets ₹2,249 Cr). "
                 "ROE = ₹161 Cr / avg equity ₹906 Cr = 17.74%. "
                 "Source: Kissht DRHP (OnEMI Technology Solutions) filed Aug 2025.", "info")

    if selected:
        _src = nbfc_filtered[nbfc_filtered["name"] == selected]["source"].values
        _src_txt = _src[0] if len(_src) and _src[0] else ""
        if _src_txt:
            st.markdown(
                f'<p style="font-size:0.70rem;color:#B0B2B8;margin-top:2rem;'
                f'font-family:\'Inter\',sans-serif;">Source: {_src_txt}</p>',
                unsafe_allow_html=True,
            )

with tabs[3]:
    deep_dive_tab(fin_filtered, nbfc_filtered)

TICKER_MAP = {
    "Bajaj Finance": "BAJFINANCE.NS",
    "Bajaj Housing Finance": "BAJAJHFL.NS",
    "LIC Housing Finance": "LICHSGFIN.NS",
    "Mahindra & Mahindra Financial Services": "M&MFIN.NS",
    "Shriram Finance": "SHRIRAMFIN.NS",
    "Muthoot Finance": "MUTHOOTFIN.NS",
    "Cholamandalam Investment and Finance": "CHOLAFIN.NS",
    "L&T Finance": "LTF.NS",
    "Poonawalla Fincorp": "POONAWALLA.NS",
    "IIFL Finance": "IIFL.NS",
    "CreditAccess Grameen": "CREDITACC.NS",
    "Spandana Sphoorty": "SPANDANA.NS",
    "Fusion Micro Finance": "FUSION.NS",
    "Five-Star Business Finance": "FIVESTAR.NS",
    "Home First Finance": "HOMEFIRST.NS",
    "Aavas Financiers": "AAVAS.NS",
    "Aptus Value Housing Finance": "APTUS.NS",
    "India Shelter Finance": "INDIASHLTR.NS",
    "Satin Creditcare Network": "SATIN.NS",
    "Manappuram Finance": "MANAPPURAM.NS",
    "MAS Financial Services": "MASFIN.NS",
    "Repco Home Finance": "REPCOHOME.NS",
    "SK Finance": "SKFIN.NS",
    "Jio Financial Services": "JIOFIN.NS",
    "Sammaan Capital": "SAMMAANCAP.NS",
    "Ugro Capital": "UGROCAP.NS",
    "Muthoot Microfin": "MUTHOOTMF.NS",
    "SBI Cards and Payment Services": "SBICARD.NS",
}

# Explicit sector classification for listed NBFCs — keyed by TICKER_MAP company names
# so Valuation tab sector filter is reliable regardless of DB name matching.
TICKER_SECTOR = {
    "Bajaj Finance":                          "Consumer Finance",
    "Bajaj Housing Finance":                  "Housing Finance",
    "LIC Housing Finance":                    "Housing Finance",
    "Mahindra & Mahindra Financial Services": "Consumer Finance",
    "Shriram Finance":                        "Consumer Finance",
    "Muthoot Finance":                        "Gold Loan",
    "Cholamandalam Investment and Finance":   "Consumer Finance",
    "L&T Finance":                            "Consumer Finance",
    "Poonawalla Fincorp":                     "Consumer Finance",
    "IIFL Finance":                           "Consumer Finance",
    "CreditAccess Grameen":                   "Microfinance",
    "Spandana Sphoorty":                      "Microfinance",
    "Fusion Micro Finance":                   "Microfinance",
    "Five-Star Business Finance":             "SME",
    "Home First Finance":                     "Housing Finance",
    "Aavas Financiers":                       "Housing Finance",
    "Aptus Value Housing Finance":            "Housing Finance",
    "India Shelter Finance":                  "Housing Finance",
    "Satin Creditcare Network":               "Microfinance",
    "Manappuram Finance":                     "Gold Loan",
    "MAS Financial Services":                 "SME",
    "Repco Home Finance":                     "Housing Finance",
    "SK Finance":                             "Consumer Finance",
    "Jio Financial Services":                 "Other",
    "Sammaan Capital":                        "Other",
    "Ugro Capital":                           "SME",
    "Muthoot Microfin":                       "Microfinance",
    "SBI Cards and Payment Services":         "Consumer Finance",
}


def fetch_valuation_data():
    tickers = list(TICKER_MAP.values())
    rows = []
    try:
        hist = yf.download(tickers, period="13mo", interval="1mo",
                           auto_adjust=True, progress=False)
        prices_hist = hist["Close"] if "Close" in hist.columns.get_level_values(0) else hist
    except Exception:
        prices_hist = pd.DataFrame()

    for company, ticker in TICKER_MAP.items():
        try:
            t = yf.Ticker(ticker)
            try:
                fi = t.fast_info
                pe = getattr(fi, "trailing_pe", None) or t.info.get("trailingPE")
                pb = getattr(fi, "price_to_book", None) or t.info.get("priceToBook")
                price = getattr(fi, "last_price", None) or t.info.get("currentPrice")
                mktcap = getattr(fi, "market_cap", None) or t.info.get("marketCap")
            except Exception:
                info = t.info
                pe = info.get("trailingPE")
                pb = info.get("priceToBook")
                price = info.get("currentPrice")
                mktcap = info.get("marketCap")

            chg_12m = None
            if not prices_hist.empty and ticker in prices_hist.columns:
                p = prices_hist[ticker].dropna()
                if len(p) >= 2:
                    chg_12m = round((p.iloc[-1] / p.iloc[0] - 1) * 100, 1)

            mktcap_cr = round(mktcap / 1e7, 0) if mktcap else None
            rows.append({
                "company": company, "ticker": ticker,
                "price": round(price, 2) if price else None,
                "pe": round(pe, 1) if pe else None,
                "pb": round(pb, 2) if pb else None,
                "mktcap_cr": mktcap_cr,
                "chg_12m": chg_12m,
            })
        except Exception:
            rows.append({"company": company, "ticker": ticker,
                         "price": None, "pe": None, "pb": None,
                         "mktcap_cr": None, "chg_12m": None})
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: TOP RANKED
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    _lbl_tr = latest_period_label(fin_filtered)
    _snap   = get_latest_period_data(fin_filtered)

    # Map each company to the period used in _snap
    _snap_period = _snap.set_index("name")["period"].to_dict() if "period" in _snap.columns else {}

    def _top20_hbar(metric, label, color, bar_fmt=None, hover_fmt=None, is_inr=False):
        cols = ["name", metric] + (["period"] if "period" in _snap.columns else [])
        df = _snap[cols].dropna(subset=[metric]).sort_values(metric, ascending=False).head(10).copy()
        period_col = df["period"] if "period" in df.columns else df["name"].map(_snap_period)

        # Bar label: formatted value
        if is_inr:
            df["bar_label"] = df[metric].apply(lambda v: f"₹{v:,.0f} Cr")
        else:
            df["bar_label"] = df[metric].apply(lambda v: (bar_fmt or "{:.2f}%").format(v))

        # Hover: value + period
        df["hover"] = df.apply(
            lambda r: (f"₹{r[metric]:,.0f} Cr" if is_inr else (bar_fmt or "{:.2f}%").format(r[metric]))
                      + f"  ·  {_snap_period.get(r['name'], '')}",
            axis=1,
        )

        # Build title period label from periods actually in this chart
        _periods_used = df["period"].dropna().unique() if "period" in df.columns else []
        _has_fy25  = any("FY2025" in p for p in _periods_used)
        _has_9m    = any("9M" in p or "Q3" in p for p in _periods_used)
        if _has_fy25 and _has_9m:
            _chart_lbl = "FY25 / 9MFY26"
        elif _has_9m:
            _chart_lbl = "9MFY26"
        else:
            _chart_lbl = "FY25"

        fig = make_hbar(
            df, metric, "name", color,
            f"Top 10 by {label} (as of {_chart_lbl})",
            hover_text=df["hover"].tolist(),
            text_labels=df["bar_label"].tolist(),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f'<div class="section-header">Rankings as of {_lbl_tr}</div>',
                unsafe_allow_html=True)

    _exc_caption_tr = ("* KreditBee 9MFY26: annualised adj. PAT ₹252 Cr "
                       "(₹341 Cr reported − ₹152 Cr exceptional items × 4/3).  "
                       "Moneyview 9MFY26: pre-exceptional PAT ₹245 Cr × 4/3 = ₹327 Cr annualised.")
    col1, col2 = st.columns(2)
    with col1:
        _top20_hbar("loan_book_cr", "AUM (Loan Book)", COLOR["accent"], is_inr=True)
    with col2:
        _top20_hbar("pat_cr", "PAT", COLOR["success"], is_inr=True)
    st.caption(_exc_caption_tr)

    col3, col4 = st.columns(2)
    with col3:
        _top20_hbar("roa_pct", "Return on Assets (ROA)", "#217858", bar_fmt="{:.2f}%")
    with col4:
        _top20_hbar("roe_pct", "Return on Equity (ROE)", "#2CA076", bar_fmt="{:.2f}%")
    st.caption(_exc_caption_tr)

    note("KreditBee 9MFY26 — PAT & ROA adjusted for one-time exceptional items:  "
         "Reported 9M PAT ₹341 Cr − ₹152 Cr exceptional (₹104 Cr GST provision reversal, Karnataka HC Dec 2025 "
         "+ ₹48 Cr DTA recognition) = Adjusted 9M PAT ₹189 Cr × 4/3 = Annualised PAT ₹252 Cr.  "
         "Adjusted ROA = ₹252 Cr ÷ avg loan book ₹7,049 Cr [(₹5,649 + ₹8,448) ÷ 2] = 3.58%.", "warning")
    note("Moneyview 9MFY26: Loan book = managed AUM (₹19,815 Cr incl. co-lending & off-book). "
         "ROA & ROE use PAT before exceptional items (₹245 Cr, 9M → annualised ₹327 Cr). "
         "Reported 9M PAT = ₹210 Cr (after ₹35 Cr one-time charges). Source: DRHP Mar-2026.", "info")

    # Market cap — live from Yahoo Finance (listed NBFCs only)
    st.markdown('<div class="section-header">Market Capitalisation (Listed NBFCs)</div>',
                unsafe_allow_html=True)
    note("Live market cap from Yahoo Finance. Only listed NBFCs shown. Refreshes every hour.")
    with st.spinner("Fetching live market cap…"):
        _val_df = fetch_valuation_data()
    _mc = (_val_df[["company", "mktcap_cr"]]
           .dropna(subset=["mktcap_cr"])
           .sort_values("mktcap_cr", ascending=False)
           .head(10)
           .rename(columns={"company": "name"}))
    if not _mc.empty:
        _mc["bar_label"] = _mc["mktcap_cr"].apply(lambda v: f"₹{v:,.0f} Cr")
        _mc["hover"]     = _mc["mktcap_cr"].apply(lambda v: f"₹{v:,.0f} Cr  ·  Live")
        fig_mc = make_hbar(_mc, "mktcap_cr", "name", "#1e40af",
                           "Top 10 by Market Cap (Live)",
                           hover_text=_mc["hover"].tolist(),
                           text_labels=_mc["bar_label"].tolist())
        st.plotly_chart(fig_mc, use_container_width=True)
    else:
        st.info("Market cap data unavailable.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7: VALUATION
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    note("Live data from Yahoo Finance. P/E is trailing twelve months. Refreshes once a day.")

    VAL_CACHE_PATH = "data/valuation_cache.json"

    def save_val_cache(df):
        import json
        record = {
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "data": df.to_dict(orient="records"),
        }
        try:
            os.makedirs("data", exist_ok=True)
            with open(VAL_CACHE_PATH, "w") as f:
                json.dump(record, f)
        except Exception:
            pass

    def load_val_cache():
        import json
        try:
            with open(VAL_CACHE_PATH) as f:
                record = json.load(f)
            return pd.DataFrame(record["data"]), record["fetched_at"]
        except Exception:
            return None, None

    def _cache_is_fresh(fetched_at_str, hours=24):
        try:
            ts = datetime.strptime(fetched_at_str, "%Y-%m-%d %H:%M")
            return (datetime.now() - ts).total_seconds() < hours * 3600
        except Exception:
            return False

    # Use disk cache if fresh (< 24 h); only hit Yahoo Finance when stale / missing
    cached_df, cache_ts = load_val_cache()
    using_cache = False
    val_with_price = pd.DataFrame()

    if cached_df is not None and _cache_is_fresh(cache_ts, hours=24):
        val_with_price = cached_df.dropna(subset=["price"])
        using_cache = True
    else:
        with st.spinner("Fetching market data…"):
            val_df = fetch_valuation_data()
        val_with_price = val_df.dropna(subset=["price"])
        if not val_with_price.empty:
            save_val_cache(val_with_price)
            cache_ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        elif cached_df is not None:
            # Live fetch failed — fall back to stale cache
            val_with_price = cached_df.dropna(subset=["price"])
            using_cache = True
        else:
            note("Could not fetch live data and no cached data available. Try again later.", "error")
            st.stop()

    if using_cache:
        note(f"Showing cached data from {cache_ts}. Refreshes once a day.", "warning")
    else:
        st.caption(f"Last updated: {cache_ts}")

    # Apply sidebar sector filter to Valuation tab
    _val_sector_filter = sector_filter  # explicit local copy to avoid any closure issue
    if _val_sector_filter and not val_with_price.empty:
        val_with_price = val_with_price[
            val_with_price["company"].apply(
                lambda c: TICKER_SECTOR.get(c, "Other") in _val_sector_filter
            )
        ]
        st.caption(f"Showing: {', '.join(_val_sector_filter)} — {len(val_with_price)} companies")
    else:
        st.caption(f"Showing: All sectors — {len(val_with_price)} companies")

    if not val_with_price.empty:
        med_pe = val_with_price["pe"].median()
        med_pb = val_with_price["pb"].median()
        med_chg = val_with_price["chg_12m"].median()

        pe_val   = f"{med_pe:.1f}x"   if pd.notna(med_pe)  else "N/A"
        pb_val   = f"{med_pb:.2f}x"   if pd.notna(med_pb)  else "N/A"
        chg_val  = f"{med_chg:.1f}%"  if pd.notna(med_chg) else "N/A"
        chg_color = "#144835" if pd.notna(med_chg) and med_chg >= 0 else "#c0392b"
        st.markdown(f"""
        <div style="display:flex;gap:1.2rem;margin:0.6rem 0 1.4rem;">
            <div style="flex:1;background:#f8fafb;border:1px solid #EAEAEA;border-radius:14px;
                        padding:1.1rem 1.5rem;text-align:center;">
                <div style="font-size:0.68rem;font-weight:600;color:#8B8FA8;letter-spacing:0.08em;
                            text-transform:uppercase;margin-bottom:0.45rem;">Median P/E (TTM)</div>
                <div style="font-size:1.65rem;font-weight:700;color:#1a1a1a;line-height:1.1;">{pe_val}</div>
            </div>
            <div style="flex:1;background:#f8fafb;border:1px solid #EAEAEA;border-radius:14px;
                        padding:1.1rem 1.5rem;text-align:center;">
                <div style="font-size:0.68rem;font-weight:600;color:#8B8FA8;letter-spacing:0.08em;
                            text-transform:uppercase;margin-bottom:0.45rem;">Median P/B</div>
                <div style="font-size:1.65rem;font-weight:700;color:#1a1a1a;line-height:1.1;">{pb_val}</div>
            </div>
            <div style="flex:1;background:#f8fafb;border:1px solid #EAEAEA;border-radius:14px;
                        padding:1.1rem 1.5rem;text-align:center;">
                <div style="font-size:0.68rem;font-weight:600;color:#8B8FA8;letter-spacing:0.08em;
                            text-transform:uppercase;margin-bottom:0.45rem;">Median 12M Return</div>
                <div style="font-size:1.65rem;font-weight:700;color:{chg_color};line-height:1.1;">{chg_val}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            pe_df = val_with_price.dropna(subset=["pe"]).sort_values("pe", ascending=False)
            fig = make_hbar(pe_df, "pe", "company", COLOR["primary"], "P/E Ratio (TTM)",
                            height=bar_chart_height(len(pe_df)),
                            hover_text=["TTM"] * len(pe_df), text_suffix="×")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            pb_df = val_with_price.dropna(subset=["pb"]).sort_values("pb", ascending=False)
            fig = make_hbar(pb_df, "pb", "company", COLOR["accent"], "P/B Ratio",
                            height=bar_chart_height(len(pb_df)),
                            hover_text=["Latest"] * len(pb_df), text_suffix="×")
            st.plotly_chart(fig, use_container_width=True)

        # P/E by sector  ·  ROE by sector
        st.markdown('<div class="section-header">Valuations &amp; Returns by Sector</div>',
                    unsafe_allow_html=True)
        _sector_map = nbfc_df.set_index("name")["sector"].to_dict()
        val_sect = val_with_price.copy()
        val_sect["sector"] = val_sect["company"].map(_sector_map)
        pe_sect = (
            val_sect.dropna(subset=["pe", "sector"])
            .groupby("sector")["pe"]
            .median()
            .reset_index()
            .sort_values("pe", ascending=False)
        )
        # ROE by sector — from latest financials snapshot
        _roe_snap = get_latest_period_data(fin_filtered)
        _lbl_val  = latest_period_label(fin_filtered)

        # Sector order is set by P/E (pe_sect already sorted descending)
        _sector_order = pe_sect["sector"].tolist() if not pe_sect.empty else []

        def _apply_sector_order(df, sector_col="sector"):
            """Reindex df rows to match _sector_order; drop sectors not in order."""
            if not _sector_order:
                return df
            order_map = {s: i for i, s in enumerate(_sector_order)}
            df = df[df[sector_col].isin(order_map)].copy()
            df["_ord"] = df[sector_col].map(order_map)
            return df.sort_values("_ord").drop(columns="_ord")

        roe_sect = (
            _roe_snap.dropna(subset=["roe_pct", "sector"])
            .groupby("sector")["roe_pct"]
            .median()
            .reset_index()
        )
        roe_sect = _apply_sector_order(roe_sect)

        # Revenue (NII) growth by sector — NII is the primary revenue line for NBFCs
        _nii_growth = compute_latest_growth(fin_filtered, "net_interest_income_cr")
        _nii_growth = _nii_growth.merge(
            fin_filtered[["name", "sector"]].drop_duplicates(), on="name", how="left"
        )
        nii_sect = (
            _nii_growth.dropna(subset=["growth_pct", "sector"])
            .groupby("sector")["growth_pct"]
            .median()
            .reset_index()
        )
        nii_sect = _apply_sector_order(nii_sect)
        _nii_lbl = _nii_growth["period_label"].mode()[0] if not _nii_growth.empty else _lbl_val

        _chart_h = bar_chart_height(max(len(pe_sect), len(roe_sect), len(nii_sect)))
        col_pe, col_roe, col_nii = st.columns(3)
        with col_pe:
            if not pe_sect.empty:
                fig = make_hbar(
                    pe_sect, "pe", "sector", COLOR["primary"], "Median P/E by Sector (TTM)",
                    height=_chart_h,
                    hover_text=["TTM"] * len(pe_sect), text_suffix="×",
                )
                st.plotly_chart(fig, use_container_width=True)
        with col_roe:
            if not roe_sect.empty:
                fig = make_hbar(
                    roe_sect, "roe_pct", "sector", COLOR["accent"],
                    f"Median ROE by Sector ({_lbl_val})",
                    height=_chart_h,
                    hover_text=[_lbl_val] * len(roe_sect), text_suffix="%",
                )
                st.plotly_chart(fig, use_container_width=True)
        with col_nii:
            if not nii_sect.empty:
                fig = make_hbar(
                    nii_sect, "growth_pct", "sector", COLOR["success"],
                    f"Median Revenue Growth by Sector ({_nii_lbl})",
                    height=_chart_h,
                    hover_text=[_nii_lbl] * len(nii_sect), text_suffix="%",
                )
                st.plotly_chart(fig, use_container_width=True)

        # 12M price change
        st.markdown('<div class="section-header">12-Month Stock Price Change</div>',
                    unsafe_allow_html=True)
        chg_df = val_with_price.dropna(subset=["chg_12m"]).sort_values("chg_12m", ascending=False)
        chg_df["color"] = chg_df["chg_12m"].apply(
            lambda x: COLOR["success"] if x >= 0 else COLOR["danger"])
        chg_df["label"] = chg_df["company"].apply(truncate_name)

        fig = go.Figure(go.Bar(
            x=chg_df["chg_12m"], y=chg_df["label"], orientation="h",
            marker_color=chg_df["color"],
            text=chg_df["chg_12m"].round(1), textposition="outside",
            textfont=dict(family=CHART_MONO, size=10),
            cliponaxis=False,
        ))
        chg_max = chg_df["chg_12m"].abs().max() if not chg_df.empty else 1
        fig.update_layout(
            title=dict(text="12-Month Price Change %",
                       font=dict(color=COLOR["text"], family=CHART_FONT, size=14),
                       x=0.5, xanchor="center", xref="paper", pad=dict(t=6, b=10)),
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            font=dict(color=COLOR["text_secondary"], family=CHART_FONT),
            height=bar_chart_height(len(chg_df)),
            yaxis=dict(autorange="reversed",
                       showgrid=False, tickcolor="rgba(0,0,0,0)", title=""),
            xaxis=dict(title="", showgrid=False, showticklabels=False,
                       range=[-(chg_max * 1.5), chg_max * 1.5],
                       zeroline=True, zerolinecolor="#EAEAEA", zerolinewidth=1,
                       tickcolor="rgba(0,0,0,0)"),
            margin=dict(t=82, b=20, l=10, r=130),
            hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e4ede6",
                            font=dict(family=CHART_FONT, size=12)),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary table
        st.markdown('<div class="section-header">All Listed NBFCs</div>', unsafe_allow_html=True)
        display_val = val_df.sort_values("mktcap_cr", ascending=False, na_position="last")

        _cols   = ["ticker", "company", "price", "pe", "pb", "mktcap_cr", "chg_12m"]
        _heads  = ["Ticker", "Company", "Price (₹)", "P/E", "P/B", "Mkt Cap (₹ Cr)", "12M Chg %"]
        _right  = {2, 3, 4, 5, 6}   # 0-indexed columns that should be right-aligned

        def _fmt_val_cell(col, val):
            if pd.isna(val): return "—"
            if col == "price":    return f"₹{val:,.2f}"
            if col == "pe":       return f"{val:.1f}"
            if col == "pb":       return f"{val:.2f}"
            if col == "mktcap_cr":return f"₹{val:,.0f}"
            if col == "chg_12m":  return f"{val:+.1f}%"
            return str(val)

        _th = ("padding:9px 14px;font-size:12px;font-weight:700;color:#1a1a1a;"
               "border-bottom:2px solid #DCDCDE;white-space:nowrap;background:#f8fafb;")
        _td = "padding:8px 14px;font-size:13px;border-bottom:1px solid #f0f0f0;white-space:nowrap;"

        rows_html = ""
        for _, r in display_val[_cols].iterrows():
            cells = ""
            for i, c in enumerate(_cols):
                val_str = _fmt_val_cell(c, r[c])
                color   = ""
                if c == "chg_12m" and pd.notna(r[c]):
                    color = "color:#144835;" if r[c] >= 0 else "color:#c0392b;"
                align = "right" if i in _right else "left"
                cells += f'<td style="{_td}text-align:{align};{color}">{val_str}</td>'
            rows_html += f"<tr>{cells}</tr>"

        headers_html = "".join(
            f'<th style="{_th}text-align:{"right" if i in _right else "left"}">{h}</th>'
            for i, h in enumerate(_heads)
        )

        st.markdown(f"""
        <div style="overflow-x:auto;border:1px solid #EAEAEA;border-radius:12px;margin-top:0.5rem;">
        <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
          <thead><tr>{headers_html}</tr></thead>
          <tbody>{rows_html}</tbody>
        </table></div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 9: DATA
# ─────────────────────────────────────────────────────────────────────────────
with tabs[6]:
    lbl = latest_period_label(fin_filtered)
    all_names = sorted(fin_filtered["name"].dropna().unique().tolist())
    selected_name = st.selectbox(
        "Select Company",
        options=["All companies"] + all_names,
        index=0,
    )

    st.markdown(f'<div class="section-header">All Companies — Financial Metrics as of {lbl}</div>',
                unsafe_allow_html=True)
    metrics_df = get_latest_period_data(fin_filtered).copy()
    if selected_name != "All companies":
        metrics_df = metrics_df[metrics_df["name"] == selected_name]
    search = "" if selected_name == "All companies" else selected_name

    metrics_df["Audited"] = metrics_df["data_quality"].apply(
        lambda x: "⚠️ Est." if x == "estimated" else ("❌ Unverified" if x == "unverified" else ("📄 DRHP" if x == "DRHP" else "✓"))
    )

    _m_cols  = ["name", "rbi_layer", "sector", "period",
                "loan_book_cr", "total_assets_cr",
                "gnpa_pct", "credit_loss_rate_pct", "roa_pct", "roe_pct", "Audited"]
    _m_heads = ["Company", "Layer", "Sector", "Period",
                "Loan Book (₹ Cr)", "Assets (₹ Cr)",
                "GNPA %", "Ann. Loss %", "ROA %", "ROE %", "Audited"]
    _m_right = {4, 5, 6, 7, 8, 9, 10}   # 0-indexed numeric / status cols

    def _fmt_metric_cell(col, val):
        if pd.isna(val) or val is None: return "—"
        if col in ("loan_book_cr", "total_assets_cr"): return f"₹{val:,.0f}"
        if col in ("gnpa_pct", "credit_loss_rate_pct", "roa_pct", "roe_pct"): return f"{val:.2f}%"
        return str(val)

    _mth = ("padding:9px 14px;font-size:12px;font-weight:700;color:#1a1a1a;"
            "border-bottom:2px solid #DCDCDE;white-space:nowrap;background:#f8fafb;")
    _mtd = "padding:8px 14px;font-size:12px;border-bottom:1px solid #f0f0f0;white-space:nowrap;"

    _m_rows = ""
    for _, r in metrics_df[_m_cols].iterrows():
        cells = ""
        for i, c in enumerate(_m_cols):
            val_str = str(r[c]) if c in ("name","rbi_layer","sector","period","Audited") else _fmt_metric_cell(c, r[c])
            align   = "right" if i in _m_right else "left"
            cells  += f'<td style="{_mtd}text-align:{align};">{val_str}</td>'
        _m_rows += f"<tr>{cells}</tr>"

    _m_headers = "".join(
        f'<th style="{_mth}text-align:{"right" if i in _m_right else "left"}">{h}</th>'
        for i, h in enumerate(_m_heads)
    )
    st.markdown(f"""
    <div style="overflow-x:auto;border:1px solid #EAEAEA;border-radius:12px;margin-top:0.5rem;">
    <table style="width:100%;border-collapse:collapse;font-family:Inter,sans-serif;">
      <thead><tr>{_m_headers}</tr></thead>
      <tbody>{_m_rows}</tbody>
    </table></div>
    """, unsafe_allow_html=True)
    st.caption(
        f"Showing most recent available period per company. "
        f"Where FY2026-Q3 data exists, 9MFY26 is shown. "
        f"Flow metrics annualised ×4/3. Ratios/stock metrics are Q3 point-in-time."
    )

    # CSV download
    csv = metrics_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "nbfc_metrics.csv", "text/csv")

    # Full history
    st.markdown('<div class="section-header">Full Financial History (Annual + 9MFY26)</div>',
                unsafe_allow_html=True)
    raw = get_chart_periods(fin_filtered).copy()
    if selected_name != "All companies":
        raw = raw[raw["name"] == selected_name]
    st.dataframe(raw.drop(columns=["id", "nbfc_id"], errors="ignore"),
                 use_container_width=True, hide_index=True)
    st.caption("Raw quarterly rows (Q1, Q2, Q3) are excluded. Only annual (FY2021–FY2025) and annualised 9MFY26 rows shown.")
