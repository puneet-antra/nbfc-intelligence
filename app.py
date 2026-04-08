"""
NBFC Intelligence — Streamlit app
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
import yfinance as yf
import numpy as np
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
    max-width: 1460px !important;
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
    margin: 2.4rem 0 1.0rem 0;
    padding: 0.45rem 0.9rem 0.45rem 0.9rem;
    background: #D7F4E9;
    border-left: 3px solid #144835;
    border-radius: 0 4px 4px 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    line-height: 1.2;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #101012 !important;
    border-right: 1px solid #1e1e20 !important;
}
/* Collapse button (‹) inside open sidebar */
[data-testid="stSidebarCollapseButton"] {
    background: #1a1a1c !important;
    border-radius: 6px !important;
    opacity: 1 !important;
    visibility: visible !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    color: #D7F4E9 !important;
    fill: #D7F4E9 !important;
}
[data-testid="stSidebarCollapseButton"]:hover {
    background: #217858 !important;
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
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #1a1a1c !important;
    border-color: #2a2a2e !important;
    color: #e8e8e8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"] label span,
[data-testid="stSidebar"] [data-baseweb="checkbox"] label span {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84rem !important;
    color: #B9BABD !important;
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
    gap: 2px !important;
    border: 1px solid #DCDCDE !important;
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
[data-testid="stPlotlyChart"] > div {
    border-radius: 16px !important;
    border: 1px solid #EAEAEA !important;
    overflow: hidden !important;
    box-shadow: 0px 2px 8px 0px rgba(16, 16, 18, 0.08) !important;
    background: #ffffff !important;
    transition: box-shadow 0.2s ease !important;
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
    text-decoration: none;
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
    text-decoration: none;
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
    /* Charts full width */
    [data-testid="stPlotlyChart"] > div {
        border-radius: 10px !important;
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
PERIOD_SHORT = {
    "FY2021": "FY21", "FY2022": "FY22", "FY2023": "FY23",
    "FY2024": "FY24", "FY2025": "FY25", "9MFY26": "9MFY26",
}

# ── Ensure DB exists ─────────────────────────────────────────────────────────
import os as _os
if not _os.path.exists("data/nbfc_full.db"):
    import build_db as _build_db
    _build_db.build()

# ── Data loaders ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_nbfc_table():
    conn = sqlite3.connect("data/nbfc_full.db")
    df = pd.read_sql("SELECT * FROM nbfc", conn)
    conn.close()
    return df


@st.cache_data(ttl=300)
def load_financials():
    conn = sqlite3.connect("data/nbfc_full.db")
    df = pd.read_sql("""
        SELECT f.*, n.name, n.rbi_layer, n.sector, n.listed,
               n.data_quality AS company_dq, n.has_financials
        FROM financials f
        JOIN nbfc n ON f.nbfc_id = n.id
    """, conn)
    conn.close()
    return df

# ── Helper functions ──────────────────────────────────────────────────────────

def annual_only(df):
    """Return only annual period rows (excludes Q1/Q2/Q3)."""
    return df[~df["period"].str.contains("Q")]


def truncate_name(name, n=24):
    return name[:n] + "…" if len(name) > n else name


# Post-tax one-time exceptional items excluded from ROA/ROE calculations (₹ Crore).
# These inflate reported PAT but do not reflect recurring earnings power.
EXCEPTIONAL_ITEMS_ADJ = {
    ("KreditBee", "9MFY26"): 152,  # GST provision reversal ₹104 Cr + DTA recognition ₹48 Cr
}


def annualise_9m(df):
    """
    Build 9MFY26 rows from FY2026-Q3 data.
    - NII, PAT, credit_losses_cr: raw 9-month values (not scaled).
    - ROA: recalculated using annualised PAT (×4/3) ÷ avg loan book.
    - ROE: recalculated using annualised PAT (×4/3) ÷ avg equity.
    - credit_loss_rate_pct: annualised credit losses (×4/3) ÷ avg loan book
      (avg of FY2025 closing and Q3 closing).
    - EXCEPTIONAL_ITEMS_ADJ: company-specific post-tax one-time items subtracted
      from annualised PAT before computing ROA/ROE (pat_cr column unchanged).
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

    # Adjust pat_cr itself so PAT charts/tables also reflect ex-exceptional figures
    if "pat_cr" in ann.columns:
        ann["pat_cr"] = _adj_9m_pat(ann["pat_cr"])

    # ROA: annualised adjusted PAT ÷ avg loan book (FY25 + Q3) / 2
    # pat_cr is already adjusted above — multiply by 4/3 directly, no second adjustment
    if "pat_cr" in ann.columns and "loan_book_cr" in ann.columns and not fy25.empty:
        ann_pat = ann["pat_cr"] * (4 / 3)
        fy25_lb = fy25.set_index("nbfc_id")["loan_book_cr"]
        avg_lb = ann.apply(
            lambda r: (fy25_lb.get(r["nbfc_id"], r["loan_book_cr"]) + r["loan_book_cr"]) / 2,
            axis=1,
        )
        ann["roa_pct"] = (ann_pat.values / avg_lb.values * 100)

    # ROE: annualised adjusted PAT ÷ avg equity (FY25 + Q3) / 2
    if "pat_cr" in ann.columns and "equity_cr" in ann.columns and not fy25.empty:
        ann_pat = ann["pat_cr"] * (4 / 3)
        fy25_equity = fy25.set_index("nbfc_id")["equity_cr"]
        avg_equity = ann.apply(
            lambda r: (fy25_equity.get(r["nbfc_id"], r["equity_cr"]) + r["equity_cr"]) / 2,
            axis=1,
        )
        ann["roe_pct"] = (ann_pat.values / avg_equity.values * 100)

    # Credit loss rate: annualised credit losses (×4/3) ÷ avg loan book (FY25 + Q3) / 2
    if "credit_losses_cr" in ann.columns and "loan_book_cr" in ann.columns and not fy25.empty:
        ann_cl = ann["credit_losses_cr"] * (4 / 3)
        fy25_lb = fy25.set_index("nbfc_id")["loan_book_cr"]
        avg_lb = ann.apply(
            lambda r: (fy25_lb.get(r["nbfc_id"], r["loan_book_cr"]) + r["loan_book_cr"]) / 2,
            axis=1,
        )
        ann["credit_loss_rate_pct"] = (ann_cl.values / avg_lb.values * 100)

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
        merged = merged[(merged["recent"] > 0) & (merged["fy25"] > 0)]
        # Annualise: 9MFY26 covers 9 months vs FY25's 12 months
        merged["growth_pct"] = ((merged["recent"] / merged["fy25"]) ** (12 / 9) - 1) * 100
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


def bar_chart_height(n, min_h=340, max_h=800, px_per_row=30):
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


def wrap_title(title, max_len=32):
    """Insert <br> at a natural break point so long chart titles don't overflow."""
    if len(title) <= max_len:
        return title
    for sep in [" — ", " (", ": ", " - ", " vs "]:
        idx = title.find(sep)
        if 0 < idx <= max_len:
            return title[:idx] + "<br>" + title[idx:].lstrip()
    idx = title.rfind(" ", 0, max_len)
    if idx > 0:
        return title[:idx] + "<br>" + title[idx + 1:]
    return title


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


def make_hbar(df, x_col, y_col, color, title, height=None, hover_text=None):
    """Standard horizontal bar chart — pass data sorted DESCENDING (chart reverses y-axis)."""
    df = df.copy()
    df[y_col] = df[y_col].apply(lambda n: truncate_name(str(n)))
    h = height or bar_chart_height(len(df))
    vals = df[x_col].dropna()
    x_max = vals.abs().max() if not vals.empty else 1
    x_range = [vals.min() * 1.05 if vals.min() < 0 else 0, x_max * 1.4]
    fig = px.bar(df, x=x_col, y=y_col, orientation="h", height=h,
                 text=df[x_col].round(1))
    fig.update_traces(
        marker_color=color, marker_line_width=0,
        marker_opacity=0.88,
        textposition="outside",
        textfont=dict(family=CHART_MONO, size=11, color=COLOR["text_secondary"]),
        cliponaxis=False,
    )
    fig.update_layout(
        title=dict(
            text=wrap_title(title),
            font=dict(color=COLOR["text"], size=15, family=CHART_TITLE_FONT, weight="bold"),
            x=0.5, xanchor="center", xref="paper",
            pad=dict(t=8, b=12),
        ),
        paper_bgcolor=CHART_PAPER, plot_bgcolor=CHART_BG,
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT, size=12),
        yaxis=dict(autorange="reversed", tickfont=dict(family=CHART_FONT, size=12),
                   showgrid=False, tickcolor="rgba(0,0,0,0)", title=""),
        xaxis=dict(showgrid=False, showticklabels=False,
                   range=x_range, zeroline=True, zerolinecolor=CHART_GRID,
                   zerolinewidth=1.5, tickcolor="rgba(0,0,0,0)", title=""),
        margin=dict(l=10, r=130, t=86, b=20),
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
    t = wrap_title(title) if title else (wrap_title(existing) if existing else "")
    fig.update_layout(
        paper_bgcolor=CHART_PAPER, plot_bgcolor=CHART_BG,
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT, size=12),
        title=dict(
            text=t,
            font=dict(color=COLOR["text"], size=15, family=CHART_TITLE_FONT, weight="bold"),
            x=0.5, xanchor="center", xref="paper",
            pad=dict(t=8, b=12),
        ),
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

rbi_layer = st.sidebar.selectbox("RBI Layer", ["All", "Upper", "Middle", "Base"])
sectors = ["All"] + sorted(nbfc_df["sector"].dropna().unique().tolist())
sector_filter = st.sidebar.selectbox("Sector", sectors)
listing_filter = st.sidebar.radio("Listing Status", ["All", "Listed Only", "Unlisted Only"])
top_n = st.sidebar.slider("Companies in Rankings", min_value=10, max_value=80, value=40, step=5)
include_estimated = st.sidebar.checkbox("Include Estimated Data", value=True)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: Company annual reports, Screener.in. "
    "⚠️ = estimated from rating reports. "
    "❌ = unverified. "
    "Live valuations from Yahoo Finance."
)


def apply_filters(df):
    d = df.copy()
    if rbi_layer != "All":
        d = d[d["rbi_layer"] == rbi_layer]
    if sector_filter != "All":
        d = d[d["sector"] == sector_filter]
    if listing_filter == "Listed Only":
        d = d[d["listed"] == 1]
    elif listing_filter == "Unlisted Only":
        d = d[d["listed"] == 0]
    if not include_estimated:
        dq_col = "data_quality" if "data_quality" in d.columns else "company_dq"
        d = d[d[dq_col] == "audited"]
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

annual_fin = annual_only(fin_filtered)
latest_annual = annual_fin[annual_fin["period"] == "FY2025"]

total_nbfcs = 9359
with_data = nbfc_filtered[nbfc_filtered["has_financials"] == 1].shape[0]
total_assets = latest_annual["total_assets_cr"].sum() / 1e5  # to Lakh Crore
avg_gnpa = latest_annual["gnpa_pct"].mean()

growth_df_header = compute_latest_growth(fin_filtered, "loan_book_cr")
avg_growth = growth_df_header["growth_pct"].mean() if not growth_df_header.empty else 0.0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total NBFCs", f"{total_nbfcs:,}", help="RBI Registry")
c2.metric("With Financials", f"{with_data:,}")
c3.metric("Combined Assets", f"₹{total_assets:.1f}L Cr", help="FY25")
c4.metric("Avg AUM Growth", f"{avg_growth:.1f}%", help="Latest 1Y")
c5.metric("Avg GNPA", f"{avg_gnpa:.2f}%", help="FY25")

# ── Tabs ──────────────────────────────────────────────────────────────────────

tabs = st.tabs([
    "Growth", "Profitability", "Asset Quality",
    "Credit Losses", "NBFC Specific",
    "Valuation", "Data", "Trends",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: GROWTH
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown('<div class="section-header">AUM Growth — Latest 1 Year (9MFY26 vs FY25 where available, else FY25 vs FY24)</div>',
                unsafe_allow_html=True)

    growth_df = compute_latest_growth(fin_filtered, "loan_book_cr").dropna(subset=["growth_pct"])

    estimated_names = set(
        fin_filtered[fin_filtered["data_quality"] == "estimated"]["name"].unique()
    )
    growth_df["display_name"] = growth_df["name"].apply(
        lambda n: n + " ★" if n in estimated_names else n
    )

    top_growers = growth_df.head(20).sort_values("growth_pct", ascending=False)
    bottom_growers = growth_df.tail(20).sort_values("growth_pct", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        fig = make_hbar(top_growers, "growth_pct", "display_name",
                        COLOR["success"], f"Top {min(20, len(top_growers))} Fastest Growing",
                        hover_text=top_growers["period_label"].values)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = make_hbar(bottom_growers, "growth_pct", "display_name",
                        COLOR["danger"], "Slowest Growing / Contracting",
                        hover_text=bottom_growers["period_label"].values)
        st.plotly_chart(fig, use_container_width=True)

    st.caption("★ = estimated data. Where 9MFY26 data exists: growth is annualised ((9M AUM / FY25 AUM)^(12/9) − 1) to make it comparable to a full year. Otherwise: FY25 vs FY24.")

    # Bubble: growth vs profitability
    st.markdown('<div class="section-header">Growth vs Profitability</div>', unsafe_allow_html=True)
    latest_snap = get_latest_period_data(fin_filtered)
    lbl = latest_period_label(fin_filtered)

    bubble_df = growth_df.merge(
        latest_snap[["name", "roa_pct", "loan_book_cr", "sector"]].dropna(),
        on="name", how="inner"
    ).dropna(subset=["roa_pct", "growth_pct", "loan_book_cr"])

    if not bubble_df.empty:
        median_growth = bubble_df["growth_pct"].median()
        fig = px.scatter(
            bubble_df, x="growth_pct", y="roa_pct",
            size="loan_book_cr", color="sector",
            color_discrete_sequence=MV_PALETTE,
            hover_name="name",
            labels={"growth_pct": "AUM Growth % (Latest 1Y)", "roa_pct": f"ROA % ({lbl})"},
            title=f"Growth vs Profitability — ROA as of {lbl} (bubble = loan book)",
            height=500,
        )
        fig.add_vline(x=median_growth, line_dash="dot", line_color=COLOR["text_secondary"],
                      annotation_text=f"Median: {median_growth:.1f}%")
        chart_layout(fig)
        fig.update_traces(hovertemplate="%{hovertext}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)

    # Growth by sector
    st.markdown('<div class="section-header">AUM Growth by Sector (Latest 1Y)</div>', unsafe_allow_html=True)
    sector_growth = growth_df.merge(
        fin_filtered[["name", "sector"]].drop_duplicates(), on="name", how="left"
    ).groupby("sector")["growth_pct"].mean().reset_index().sort_values("growth_pct", ascending=False)
    fig = make_hbar(sector_growth, "growth_pct", "sector", COLOR["primary"],
                    "Avg AUM Growth % by Sector",
                    hover_text=[lbl] * len(sector_growth))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: PROFITABILITY
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    lbl = latest_period_label(fin_filtered)
    latest_snap = get_latest_period_data(fin_filtered).dropna(subset=["roa_pct", "roe_pct"])

    st.markdown(f'<div class="section-header">Return on Assets & Equity — {lbl}</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        top_roa = latest_snap.nlargest(top_n, "roa_pct").sort_values("roa_pct", ascending=False)
        fig = make_hbar(top_roa, "roa_pct", "name", COLOR["primary"],
                        f"Top {top_n} by ROA %",
                        hover_text=top_roa["period"].map(lambda p: PERIOD_SHORT.get(p, p)).values)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        top_roe = latest_snap.nlargest(top_n, "roe_pct").sort_values("roe_pct", ascending=False)
        fig = make_hbar(top_roe, "roe_pct", "name", COLOR["accent"],
                        f"Top {top_n} by ROE %",
                        hover_text=top_roe["period"].map(lambda p: PERIOD_SHORT.get(p, p)).values)
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Where 9MFY26 data exists: 9MFY26 ROA/ROE used. Otherwise FY25. "
               f"★ = estimated data.")
    note("KreditBee 9MFY26: ROA & ROE adjusted to exclude ~₹152 Cr post-tax one-time items "
         "(₹104 Cr GST provision reversal after Karnataka HC ruling, Dec 2025 + ₹48 Cr DTA recognition). "
         "Reported 9M PAT was ₹341 Cr; adjusted figure used for ratios is ~₹189 Cr.", "warning")

    # Sector breakdown — latest period
    st.markdown(f'<div class="section-header">By Sector — {lbl}</div>', unsafe_allow_html=True)
    sector_avg = latest_snap.groupby("sector").agg(
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
                      title=dict(text=wrap_title(f"ROA & ROE by Sector ({lbl})"),
                                 font=dict(color=COLOR["text"], family=CHART_FONT, size=14, weight="bold"),
                                 x=0.5, xanchor="center", xref="paper",
                                 pad=dict(t=6, b=10)),
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
                                 tickangle=0, ticklabelstandoff=4),
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

    fig = px.line(pat_trend, x="period", y="pat_cr", color="name",
                  color_discrete_sequence=MV_PALETTE,
                  labels={"pat_cr": "PAT (₹ Crore)", "period": "Period"},
                  title=f"Profit After Tax Trend — incl. {lbl} (₹ Crore)", height=460,
                  category_orders={"period": PERIOD_ORDER})
    chart_layout(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("9MFY26 = Q3 FY26 nine-month PAT (raw, not annualised).")
    note("KreditBee 9MFY26 PAT shown above is adjusted (~₹189 Cr) excluding ~₹152 Cr post-tax "
         "one-time items (₹104 Cr GST provision reversal + ₹48 Cr DTA recognition). "
         "Reported 9M PAT was ₹341 Cr.", "warning")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: ASSET QUALITY
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    lbl = latest_period_label(fin_filtered)
    latest_snap = get_latest_period_data(fin_filtered).dropna(subset=["gnpa_pct"])

    st.markdown(f'<div class="section-header">GNPA % — {lbl}</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        cleanest = latest_snap.nsmallest(20, "gnpa_pct").sort_values("gnpa_pct", ascending=False)
        fig = make_hbar(cleanest, "gnpa_pct", "name", COLOR["success"],
                        f"Lowest GNPA % ({lbl})",
                        hover_text=cleanest["period"].map(lambda p: PERIOD_SHORT.get(p, p)).values)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        stressed = latest_snap.nlargest(20, "gnpa_pct").sort_values("gnpa_pct", ascending=False)
        fig = make_hbar(stressed, "gnpa_pct", "name", COLOR["danger"],
                        f"Highest GNPA % ({lbl})",
                        hover_text=stressed["period"].map(lambda p: PERIOD_SHORT.get(p, p)).values)
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"GNPA % is a stock/point-in-time metric — 9MFY26 uses Q3 value directly, no annualisation.")

    # Trend by sector
    st.markdown(f'<div class="section-header">GNPA Trend by Sector — FY2021 to {lbl}</div>',
                unsafe_allow_html=True)
    chart_df = get_chart_periods(fin_filtered)
    sector_gnpa = chart_df.groupby(["period", "sector"])["gnpa_pct"].mean().reset_index()
    fig = px.line(sector_gnpa, x="period", y="gnpa_pct", color="sector",
                  color_discrete_sequence=MV_PALETTE,
                  labels={"gnpa_pct": "Avg GNPA %", "period": "Period"},
                  title=f"Average GNPA % by Sector (FY2021–{lbl})", height=460,
                  category_orders={"period": PERIOD_ORDER})
    chart_layout(fig)
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap — top 35 most stressed
    st.markdown('<div class="section-header">GNPA Heatmap — Top 35 Most Stressed</div>',
                unsafe_allow_html=True)
    stressed_35 = latest_snap.nlargest(35, "gnpa_pct")["name"].tolist()
    hm_source = get_chart_periods(fin_filtered)
    hm_df = hm_source[hm_source["name"].isin(stressed_35)].pivot_table(
        index="name", columns="period", values="gnpa_pct")
    col_order = [c for c in PERIOD_ORDER if c in hm_df.columns]
    hm_df = hm_df[col_order]
    hm_df.index = [truncate_name(n) for n in hm_df.index]

    fig = go.Figure(data=go.Heatmap(
        z=hm_df.values,
        x=hm_df.columns.tolist(),
        y=hm_df.index.tolist(),
        colorscale=[[0, COLOR["success"]], [0.5, "#FCC945"], [1, COLOR["danger"]]],
        text=[[f"{v:.1f}%" if not np.isnan(v) else "N/A" for v in row] for row in hm_df.values],
        texttemplate="%{text}",
        showscale=True,
    ))
    fig.update_layout(
        title=dict(text=wrap_title(f"GNPA % Heatmap (to {lbl})"),
                   font=dict(color=COLOR["text"], family=CHART_FONT, size=14, weight="bold"),
                   x=0.5, xanchor="center", xref="paper", pad=dict(t=6, b=8)),
        paper_bgcolor=CHART_BG,
        height=max(340, len(stressed_35) * 26),
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT, size=12),
        margin=dict(t=82, b=30, l=10, r=30),
        xaxis=dict(title=""),
        yaxis=dict(title=""),
        hoverlabel=HOVER_LABEL,
    )
    fig.update_traces(hovertemplate="%{x}<extra></extra>")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: CREDIT LOSSES
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    note("Credit Loss Rate = (Net Provisions + Write-offs − Recoveries) ÷ Loan Book. "
         "This is the actual P&L cost of defaults — different from GNPA which is a stock measure.")

    lbl = latest_period_label(fin_filtered)
    latest_snap = get_latest_period_data(fin_filtered).dropna(subset=["credit_loss_rate_pct"])

    col1, col2 = st.columns(2)
    with col1:
        lowest = latest_snap.nsmallest(20, "credit_loss_rate_pct").sort_values(
            "credit_loss_rate_pct", ascending=False)
        fig = make_hbar(lowest, "credit_loss_rate_pct", "name", COLOR["success"],
                        f"Lowest Credit Loss Rate ({lbl})",
                        hover_text=lowest["period"].map(lambda p: PERIOD_SHORT.get(p, p)).values)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        highest = latest_snap.nlargest(20, "credit_loss_rate_pct").sort_values(
            "credit_loss_rate_pct", ascending=False)
        fig = make_hbar(highest, "credit_loss_rate_pct", "name", COLOR["danger"],
                        f"Highest Credit Loss Rate ({lbl})",
                        hover_text=highest["period"].map(lambda p: PERIOD_SHORT.get(p, p)).values)
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Credit loss rate % shown as of {lbl}. 9MFY26 uses Q3 ratio — not annualised.")

    # Trend for top stressed
    st.markdown(f'<div class="section-header">Credit Loss Rate Trend — FY2021 to {lbl}</div>',
                unsafe_allow_html=True)
    high12 = latest_snap.nlargest(12, "credit_loss_rate_pct")["name"].tolist()
    chart_df = get_chart_periods(fin_filtered)
    trend_df = chart_df[chart_df["name"].isin(high12)][
        ["name", "period", "credit_loss_rate_pct"]].dropna()

    fig = px.line(trend_df, x="period", y="credit_loss_rate_pct", color="name",
                  color_discrete_sequence=MV_PALETTE,
                  title=f"Credit Loss Rate % Trend (to {lbl})", height=460,
                  category_orders={"period": PERIOD_ORDER})
    fig.add_hline(y=2.0, line_dash="dot", line_color=COLOR["warning"],
                  annotation_text="2% Reference Line")
    chart_layout(fig)
    st.plotly_chart(fig, use_container_width=True)

    # Scatter: credit loss vs GNPA
    st.markdown('<div class="section-header">Credit Loss Rate vs GNPA</div>', unsafe_allow_html=True)
    scatter_df = latest_snap.dropna(subset=["credit_loss_rate_pct", "gnpa_pct", "loan_book_cr"])
    if not scatter_df.empty:
        fig = px.scatter(scatter_df, x="gnpa_pct", y="credit_loss_rate_pct",
                         size="loan_book_cr", color="sector", hover_name="name",
                         color_discrete_sequence=MV_PALETTE,
                         labels={"gnpa_pct": "GNPA %", "credit_loss_rate_pct": "Credit Loss Rate %"},
                         title=f"Credit Loss Rate vs GNPA — {lbl} (bubble = loan book)", height=520)
        chart_layout(fig)
        fig.update_traces(hovertemplate="%{hovertext}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True)

    # Waterfall: FY2021 → FY2025 (annual only)
    st.markdown('<div class="section-header">Credit Loss Rate Change — FY2021 to FY2025</div>',
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
        title=dict(text=wrap_title("Change in Credit Loss Rate: FY2021 → FY2025 (green = improved)"),
                   font=dict(color=COLOR["text"], family=CHART_FONT, size=14, weight="bold"),
                   x=0.5, xanchor="center", xref="paper", pad=dict(t=6, b=10)),
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT),
        height=bar_chart_height(len(wf)),
        xaxis=dict(title="", showgrid=False, showticklabels=False,
                   range=[-(wf_max * 1.5), wf_max * 1.5], zeroline=True,
                   zerolinecolor="#EAEAEA", zerolinewidth=1, tickcolor="rgba(0,0,0,0)"),
        yaxis=dict(showgrid=False,
                   tickcolor="rgba(0,0,0,0)", title=""),
        margin=dict(t=82, b=20, l=10, r=130),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e4ede6",
                        font=dict(family=CHART_FONT, size=12)),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap
    st.markdown(f'<div class="section-header">Credit Loss Rate Heatmap — to {lbl}</div>',
                unsafe_allow_html=True)
    top40 = latest_snap.nlargest(40, "credit_loss_rate_pct")["name"].tolist()
    hm_source = get_chart_periods(fin_filtered)
    hm_df = hm_source[hm_source["name"].isin(top40)].pivot_table(
        index="name", columns="period", values="credit_loss_rate_pct")
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
        title=dict(text=wrap_title(f"Credit Loss Rate % Heatmap (to {lbl})"),
                   font=dict(color=COLOR["text"], family=CHART_FONT, size=14, weight="bold"),
                   x=0.5, xanchor="center", xref="paper", pad=dict(t=6, b=8)),
        paper_bgcolor=CHART_BG, height=max(340, len(top40) * 26),
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT, size=12),
        margin=dict(t=82, b=30, l=10, r=30),
        xaxis=dict(title=""),
        yaxis=dict(title=""),
        hoverlabel=HOVER_LABEL,
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
        fig = px.line(nii_df, x="period", y="net_interest_income_cr", color="name",
                      color_discrete_sequence=MV_PALETTE,
                      title=f"Net Interest Income (₹ Crore, to {lbl})", height=420,
                      category_orders={"period": PERIOD_ORDER})
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("9MFY26 NII = raw 9-month NII (not annualised).")

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
    top_pat = pat_cagr.head(top_n).sort_values("cagr_pct", ascending=False)
    fig = make_hbar(top_pat, "cagr_pct", "name", COLOR["accent"],
                    f"PAT CAGR % (FY21–25) — Top {top_n}",
                    hover_text=["FY21–FY25"] * len(top_pat))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: DEEP DIVE
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    companies_with_data = (
        fin_filtered[fin_filtered["has_financials"] == 1]["name"]
        .dropna().unique().tolist()
    )

    # Default to KreditBee on first load
    if "dd_company_select" not in st.session_state and "KreditBee" in companies_with_data:
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
        ("Bajaj Finance",                  "Bajaj Finance"),
        ("SBI Cards and Payment Services", "SBI Cards"),
    ]
    # Only show chips for companies that exist in the current data
    available_quick = [(n, lbl) for n, lbl in QUICK_NBFCS if n in companies_with_data]

    # Handle chip click via query param (set before widgets render)
    _qs_click = st.query_params.get("qs_select")
    if _qs_click and _qs_click in companies_with_data:
        st.session_state["dd_company_select"] = _qs_click
        st.session_state["dd_layer_filter"] = "All"
        st.session_state["dd_sector_filter"] = "All"
        st.query_params.pop("qs_select", None)

    if available_quick:
        _current = st.session_state.get("dd_company_select", "")
        chips_html = (
            '<p style="font-size:0.68rem;font-weight:600;color:#A0A2A8;'
            'text-transform:uppercase;letter-spacing:0.05em;margin:0 0 0.45rem 0;">'
            'Featured</p>'
            '<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.6rem;">'
        )
        for name, label in available_quick:
            active_cls = " qs-active" if _current == name else ""
            chips_html += (
                f'<a href="?qs_select={name}" class="qs-chip{active_cls}">{label}</a>'
            )
        chips_html += "</div>"
        st.markdown(chips_html, unsafe_allow_html=True)

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
        )
    with filter_col:
        st.markdown("<div style='margin-top:1.85rem'></div>", unsafe_allow_html=True)
        with st.popover(" ", use_container_width=True):
            st.markdown(
                "<div style='font-size:0.75rem;font-weight:600;color:#28292D;"
                "margin-bottom:0.6rem;'>Narrow the list</div>",
                unsafe_allow_html=True,
            )
            st.selectbox("RBI Layer", ["All"] + avail_layers, key="dd_layer_filter")
            st.selectbox("Sector",    ["All"] + avail_sectors, key="dd_sector_filter")

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
            st.markdown(" &nbsp; ".join(badges), unsafe_allow_html=True)

            # Data source line
            src = company_info.get("source", "")
            if src:
                st.markdown(
                    f'<div style="font-size:0.7rem;color:#6b7280;margin-top:4px;'
                    f'font-family:\'Inter\',sans-serif;">Source: {src}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("")

        if company_info is not None and company_info.get("data_quality") in ["estimated", "unverified"]:
            note("This company's data includes estimated or unverified figures.", "warning")

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
            m3.metric("NII", f"₹{r['net_interest_income_cr']:,.0f} Cr" if pd.notna(r.get("net_interest_income_cr")) else "N/A")
            m4.metric("PAT", f"₹{r['pat_cr']:,.0f} Cr" if pd.notna(r.get("pat_cr")) else "N/A")
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
                         title=f"Assets & Loan Book (₹ Crore, to {lbl})", height=400,
                         category_orders={"period": PERIOD_ORDER})
            fig.update_traces(textposition="outside", textfont=dict(family=CHART_MONO, size=11),
                              cliponaxis=False)
            chart_layout(fig)
            fig.update_layout(margin=DD_MARGIN, legend=DD_LEGEND)
            fig.update_traces(hovertemplate="₹%{y:,.0f} Cr<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            # Require PAT; NII is optional — plot whichever series has data
            pat_df = chart_df[["period", "pat_cr"]].dropna(subset=["pat_cr"])
            nii_df = chart_df[["period", "net_interest_income_cr"]].dropna(subset=["net_interest_income_cr"])
            has_nii = not nii_df.empty
            fig = go.Figure()
            if has_nii:
                fig.add_trace(go.Scatter(
                    x=nii_df["period"], y=nii_df["net_interest_income_cr"],
                    mode="lines+markers", name="NII",
                    line=dict(color="#144835", width=2),
                    marker=dict(size=6),
                    hovertemplate="₹%{y:,.0f} Cr<extra>NII</extra>",
                ))
            fig.add_trace(go.Scatter(
                x=pat_df["period"], y=pat_df["pat_cr"],
                mode="lines+markers", name="PAT",
                line=dict(color="#DE5E2B", width=2),
                marker=dict(size=6),
                hovertemplate="₹%{y:,.0f} Cr<extra>PAT</extra>",
            ))
            title_txt = f"NII & PAT (₹ Crore, to {lbl})" if has_nii else f"PAT (₹ Crore, to {lbl}) — NII not disclosed"
            fig.update_layout(
                title=dict(text=wrap_title(title_txt),
                           font=dict(color=COLOR["text"], family=CHART_FONT, size=14, weight="bold"),
                           x=0.5, xanchor="center", xref="paper", pad=dict(t=6, b=10)),
                height=400,
                xaxis=dict(categoryorder="array", categoryarray=PERIOD_ORDER,
                           showgrid=False, tickcolor="rgba(0,0,0,0)",
                           linecolor="rgba(0,0,0,0)", tickfont=dict(family=CHART_FONT, size=11)),
                yaxis=dict(showgrid=False, tickcolor="rgba(0,0,0,0)"),
                paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(color=COLOR["text_secondary"], family=CHART_FONT),
                hoverlabel=HOVER_LABEL,
            )
            chart_layout(fig)
            # Re-apply per-trace hovertemplates after chart_layout (which sets a global override)
            for trace in fig.data:
                if trace.name == "NII":
                    trace.hovertemplate = "₹%{y:,.0f} Cr<extra>NII</extra>"
                elif trace.name == "PAT":
                    trace.hovertemplate = "₹%{y:,.0f} Cr<extra>PAT</extra>"
            fig.update_layout(margin=DD_MARGIN, legend=DD_LEGEND)
            st.plotly_chart(fig, use_container_width=True)
            if selected == "KreditBee" and has_q3:
                note("9MFY26 PAT adjusted to ~₹189 Cr (ex ~₹152 Cr one-time items). "
                     "NII (₹978 Cr) is unaffected — the GST provision reversal reduced expenses, "
                     "not income.", "warning")

        col3, col4 = st.columns(2)
        with col3:
            gnpa_df = chart_df[["period", "gnpa_pct"]].dropna()
            fig = px.line(gnpa_df, x="period", y="gnpa_pct",
                          title=f"GNPA % Trend (to {lbl})", markers=True, height=380,
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
                          title=f"ROA & ROE % (to {lbl})", markers=True, height=380,
                          category_orders={"period": PERIOD_ORDER})
            chart_layout(fig)
            fig.update_layout(margin=DD_MARGIN, legend=DD_LEGEND)
            fig.update_traces(hovertemplate="%{y:.2f}%<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)

        cl_df = chart_df[["period", "credit_loss_rate_pct"]].dropna()
        fig = px.line(cl_df, x="period", y="credit_loss_rate_pct",
                      title=f"Credit Loss Rate % (to {lbl})", markers=True, height=380,
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
        table_df = chart_df[[c for c in display_cols if c in chart_df.columns]].set_index("period").T
        table_df.index = ["Loan Book (₹ Cr)", "Total Assets (₹ Cr)", "Equity (₹ Cr)",
                          "NII (₹ Cr)", "PAT (₹ Cr)", "Credit Loss Rate %",
                          "GNPA %", "ROA %", "ROE %"][:len(table_df)]
        st.dataframe(table_df.style.format("{:.1f}", na_rep="N/A"), use_container_width=True)
        if has_q3:
            st.caption("9MFY26: all figures are raw 9-month / Q3 point-in-time values. ROA/ROE are annualised at ×4/3.")
        if has_q3 and selected == "KreditBee":
            note("ROA, ROE & PAT exclude ~₹152 Cr post-tax one-time items: ₹104 Cr GST provision reversal "
                 "(Karnataka HC ruling, Dec 2025) + ₹48 Cr DTA recognition. "
                 "Reported 9M PAT: ₹341 Cr → Adjusted: ~₹189 Cr.", "warning")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7: VALUATION
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    note("Live data from Yahoo Finance. P/E is trailing twelve months. Refreshes every hour.")

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
    }

    VAL_CACHE_PATH = "data/valuation_cache.json"

    def save_val_cache(df):
        record = {
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "data": df.to_dict(orient="records"),
        }
        import json
        with open(VAL_CACHE_PATH, "w") as f:
            json.dump(record, f)

    def load_val_cache():
        import json
        try:
            with open(VAL_CACHE_PATH) as f:
                record = json.load(f)
            return pd.DataFrame(record["data"]), record["fetched_at"]
        except Exception:
            return None, None

    @st.cache_data(ttl=3600)
    def fetch_valuation_data():
        tickers = list(TICKER_MAP.values())
        rows = []

        # Batch price history
        try:
            hist = yf.download(tickers, period="13mo", interval="1mo",
                               auto_adjust=True, progress=False)
            if "Close" in hist.columns.get_level_values(0):
                prices_hist = hist["Close"]
            else:
                prices_hist = hist
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

    with st.spinner("Fetching live market data…"):
        val_df = fetch_valuation_data()

    # If live fetch returned no prices, fall back to disk cache
    val_with_price = val_df.dropna(subset=["price"])
    using_cache = False
    cache_ts = None

    if val_with_price.empty:
        cached_df, cache_ts = load_val_cache()
        if cached_df is not None:
            val_df = cached_df
            val_with_price = val_df.dropna(subset=["price"])
            using_cache = True
        else:
            note("Could not fetch live data and no cached data available. Try again later.", "error")
            st.stop()
    else:
        # Successful fetch — save to disk cache for next time
        save_val_cache(val_with_price)

    if using_cache:
        note(f"Live fetch failed (Yahoo Finance rate limit). Showing cached data from {cache_ts}.", "warning")
    else:
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    if not val_with_price.empty:
        med_pe = val_with_price["pe"].median()
        med_pb = val_with_price["pb"].median()
        med_chg = val_with_price["chg_12m"].median()

        c1, c2, c3 = st.columns(3)
        c1.metric("Median P/E (TTM)", f"{med_pe:.1f}x" if pd.notna(med_pe) else "N/A")
        c2.metric("Median P/B", f"{med_pb:.2f}x" if pd.notna(med_pb) else "N/A")
        c3.metric("Median 12M Return", f"{med_chg:.1f}%" if pd.notna(med_chg) else "N/A")

        col1, col2 = st.columns(2)
        with col1:
            pe_df = val_with_price.dropna(subset=["pe"]).sort_values("pe", ascending=False)
            fig = make_hbar(pe_df, "pe", "company", COLOR["primary"], "P/E Ratio (TTM)",
                            height=bar_chart_height(len(pe_df)),
                            hover_text=["TTM"] * len(pe_df))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            pb_df = val_with_price.dropna(subset=["pb"]).sort_values("pb", ascending=False)
            fig = make_hbar(pb_df, "pb", "company", COLOR["accent"], "P/B Ratio",
                            height=bar_chart_height(len(pb_df)),
                            hover_text=["Latest"] * len(pb_df))
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
                       font=dict(color=COLOR["text"], family=CHART_FONT, size=14, weight="bold"),
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
        display_val = val_df.sort_values("mktcap_cr", ascending=False, na_position="last").rename(
            columns={"company": "Company", "ticker": "Ticker", "price": "Price (₹)",
                     "pe": "P/E", "pb": "P/B", "mktcap_cr": "Mkt Cap (₹ Cr)", "chg_12m": "12M Chg %"})
        st.dataframe(
            display_val[["Ticker", "Company", "Price (₹)", "P/E", "P/B", "Mkt Cap (₹ Cr)", "12M Chg %"]],
            use_container_width=True, hide_index=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 8: DATA
# ─────────────────────────────────────────────────────────────────────────────
with tabs[6]:
    search = st.text_input("Search companies", placeholder="Type company name…")
    lbl = latest_period_label(fin_filtered)

    st.markdown(f'<div class="section-header">All Companies — Financial Metrics as of {lbl}</div>',
                unsafe_allow_html=True)
    metrics_df = get_latest_period_data(fin_filtered).copy()
    if search:
        metrics_df = metrics_df[metrics_df["name"].str.contains(search, case=False, na=False)]

    metrics_df["⚠️"] = metrics_df["data_quality"].apply(
        lambda x: "⚠️ Est." if x == "estimated" else ("❌ Unverified" if x == "unverified" else "✓")
    )

    st.dataframe(metrics_df[[
        "name", "rbi_layer", "sector", "period", "loan_book_cr", "total_assets_cr",
        "gnpa_pct", "credit_loss_rate_pct", "roa_pct", "roe_pct", "⚠️",
    ]].rename(columns={
        "name": "Company", "rbi_layer": "Layer", "sector": "Sector", "period": "Period",
        "loan_book_cr": "Loan Book (₹ Cr)", "total_assets_cr": "Assets (₹ Cr)",
        "gnpa_pct": "GNPA %", "credit_loss_rate_pct": "Credit Loss %",
        "roa_pct": "ROA %", "roe_pct": "ROE %",
    }), use_container_width=True, hide_index=True)
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
    if search:
        raw = raw[raw["name"].str.contains(search, case=False, na=False)]
    st.dataframe(raw.drop(columns=["id", "nbfc_id"], errors="ignore"),
                 use_container_width=True, hide_index=True)
    st.caption("Raw quarterly rows (Q1, Q2, Q3) are excluded. Only annual (FY2021–FY2025) and annualised 9MFY26 rows shown.")
