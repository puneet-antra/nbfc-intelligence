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

st.set_page_config(
    page_title="NBFC Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #f7f8fa !important;
}

/* ── Remove default Streamlit padding ── */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1460px !important;
}

/* ── Page title ── */
h1 {
    font-family: 'Fraunces', serif !important;
    font-weight: 600 !important;
    font-size: 2rem !important;
    letter-spacing: -0.03em !important;
    color: #0f1f0f !important;
    line-height: 1.1 !important;
    margin-bottom: 0 !important;
}

/* ── Metric values ── */
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    color: #0f1f0f !important;
    opacity: 1 !important;
    font-weight: 500 !important;
    font-size: 1.2rem !important;
    letter-spacing: -0.01em !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Sans', sans-serif !important;
    color: #52725a !important;
    opacity: 1 !important;
    font-weight: 600 !important;
    font-size: 0.74rem !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    white-space: normal !important;
    overflow: visible !important;
    line-height: 1.5 !important;
}
[data-testid="stMetricDelta"] { opacity: 1 !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #ffffff !important;
    border: 1px solid #e4ede6 !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.4rem 1.1rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03) !important;
    transition: box-shadow 0.2s ease, transform 0.2s ease !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="metric-container"]::after {
    content: '' !important;
    position: absolute !important;
    top: 0 !important; left: 0 !important; right: 0 !important;
    height: 3px !important;
    background: linear-gradient(90deg, #2d6a2d, #4a9e4a) !important;
    border-radius: 12px 12px 0 0 !important;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0 8px 24px rgba(45,106,45,0.12), 0 2px 8px rgba(0,0,0,0.04) !important;
    transform: translateY(-2px) !important;
}

/* ── Section headers ── */
.section-header {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #52725a;
    margin: 2.5rem 0 1.1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid #e0ebe2;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e4ede6 !important;
}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] label {
    font-family: 'DM Sans', sans-serif !important;
    color: #1e3a22 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    text-transform: uppercase !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] {
    border-bottom: 1px solid #e4ede6 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    color: #7a9e82 !important;
    padding: 0.65rem 1rem !important;
    border-radius: 0 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #1e3a22 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #2d6a2d !important;
}

/* ── Dataframes ── */
[data-testid="stDataFrame"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    border-radius: 10px !important;
    border: 1px solid #e4ede6 !important;
    overflow: hidden !important;
}

/* ── Chart containers ── */
[data-testid="stPlotlyChart"] > div {
    border-radius: 12px !important;
    border: 1px solid #e8ede9 !important;
    overflow: hidden !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    background: #ffffff !important;
}

/* ── Badges ── */
.unverified-badge {
    background: #fff5ed; color: #9a3412;
    padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    border: 1px solid #fed7aa;
}
.estimated-badge {
    background: #f0fdf4; color: #15803d;
    padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 500;
    font-family: 'DM Sans', sans-serif;
    border: 1px solid #bbf7d0;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.84rem !important;
    border: none !important;
}

/* ── Captions ── */
.stCaption, [data-testid="stCaptionContainer"] {
    font-size: 0.75rem !important;
    color: #7a9e82 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Selectbox / inputs ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border: 1px solid #d4e4d6 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #c8dfc4; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

COLOR = {
    "primary": "#236b35",       # rich forest green
    "success": "#1a5c2a",       # deep success green
    "danger": "#c0392b",        # clean red
    "warning": "#d97706",       # amber
    "text": "#0f1f0f",          # near-black
    "text_secondary": "#52725a",# medium green-grey
    "card_bg": "#ffffff",       # pure white cards
    "border": "#e4ede6",        # soft green border
    "chart_bg": "#ffffff",      # white chart background
}

PERIOD_ORDER = ["FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "9MFY26 (Ann.)"]
PERIOD_SHORT = {
    "FY2021": "FY21", "FY2022": "FY22", "FY2023": "FY23",
    "FY2024": "FY24", "FY2025": "FY25", "9MFY26 (Ann.)": "9MFY26",
}

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


def annualise_9m(df):
    """
    Build annualised 9MFY26 rows from FY2026-Q3 data.
    Flow metrics (NII, PAT, credit_losses_cr) are multiplied ×4/3.
    Stock/ratio metrics use Q3 point-in-time value as-is.
    """
    FLOW = ["net_interest_income_cr", "pat_cr", "credit_losses_cr"]
    q3 = df[df["period"] == "FY2026-Q3"].copy()
    if q3.empty:
        return pd.DataFrame()
    ann = q3.copy()
    ann["period"] = "9MFY26 (Ann.)"
    for col in FLOW:
        if col in ann.columns:
            ann[col] = ann[col] * (4 / 3)
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
    Per company: use 9MFY26 (Ann.) if FY2026-Q3 exists, else FY2025.
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
    return "FY25 / 9MFY26 (Ann.)" if "FY2026-Q3" in df["period"].values else "FY25"


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
      - If 9MFY26 (Ann.) exists → (9MFY26 Ann. − FY2025) / FY2025
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
        merged["growth_pct"] = (merged["recent"] / merged["fy25"] - 1) * 100
        merged["period_label"] = "9MFY26 Ann. vs FY25"
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


CHART_FONT = "DM Sans"
CHART_MONO = "DM Mono"
CHART_BG = "#ffffff"
CHART_GRID = "#f0f4f1"


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


def make_hbar(df, x_col, y_col, color, title, height=None):
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
            font=dict(color=COLOR["text"], size=14, family=CHART_FONT, weight="bold"),
            x=0, xanchor="left", xref="paper",
            pad=dict(t=6, b=10),
        ),
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT, size=12),
        yaxis=dict(autorange="reversed", tickfont=dict(family=CHART_FONT, size=12),
                   showgrid=False, tickcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=True, gridcolor=CHART_GRID, tickfont=dict(family=CHART_MONO, size=11),
                   range=x_range, zeroline=False, tickcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=130, t=82, b=20),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e4ede6",
                        font=dict(family=CHART_FONT, size=12)),
    )
    return fig


def chart_layout(fig, title=None):
    existing = ""
    if fig.layout.title and fig.layout.title.text:
        existing = fig.layout.title.text
    t = wrap_title(title) if title else (wrap_title(existing) if existing else "")
    fig.update_layout(
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT, size=12),
        title=dict(
            text=t,
            font=dict(color=COLOR["text"], size=14, family=CHART_FONT, weight="bold"),
            x=0, xanchor="left", xref="paper",
            pad=dict(t=6, b=10),
        ),
        xaxis=dict(gridcolor=CHART_GRID, tickfont=dict(family=CHART_MONO, size=11),
                   showgrid=True, zeroline=False, tickcolor="rgba(0,0,0,0)",
                   linecolor="rgba(0,0,0,0)", title="",
                   tickvals=list(PERIOD_SHORT.keys()),
                   ticktext=list(PERIOD_SHORT.values())),
        yaxis=dict(gridcolor=CHART_GRID, tickfont=dict(family=CHART_FONT, size=12),
                   zeroline=False, tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)",
                   title=""),
        margin=dict(t=82, b=90, l=10, r=24),
        legend=dict(
            font=dict(family=CHART_FONT, size=11),
            bgcolor="rgba(255,255,255,0)",
            bordercolor="rgba(0,0,0,0)",
            borderwidth=0,
            orientation="h",
            yanchor="bottom", y=-0.32,
            xanchor="left", x=0,
            title_text="",
        ),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e4ede6",
                        font=dict(family=CHART_FONT, size=12)),
    )
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.markdown("""
<div style="padding: 0.3rem 0 1rem 0;">
  <div style="font-family:'Fraunces',serif; font-size:1.15rem; font-weight:600; color:#0f1f0f; letter-spacing:-0.02em;">NBFC Intelligence</div>
  <div style="font-family:'DM Sans',sans-serif; font-size:0.7rem; color:#52725a; letter-spacing:0.06em; text-transform:uppercase; margin-top:2px;">India · FY2021–9MFY26</div>
</div>
<hr style="border:none; border-top:1px solid #e4ede6; margin:0 0 1rem 0;">
""", unsafe_allow_html=True)

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
<div style="display:flex; align-items:baseline; gap:0.9rem; margin-bottom:0.2rem; padding-top:0.5rem;">
  <span style="font-family:'Fraunces',serif; font-weight:600; font-size:2rem; color:#0f1f0f; letter-spacing:-0.03em; line-height:1.2;">NBFC Intelligence</span>
  <span style="font-family:'DM Sans',sans-serif; font-size:0.78rem; font-weight:500; color:#ffffff; background:#236b35; padding:3px 10px; border-radius:20px; letter-spacing:0.04em;">INDIA</span>
</div>
<p style="font-family:'DM Sans',sans-serif; font-size:0.88rem; color:#52725a; margin:0 0 1.4rem 0; font-weight:400; letter-spacing:0.01em;">
  Non-Banking Financial Companies — Growth · Profitability · Asset Quality · Valuation
</p>
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
c2.metric("With Financial Data", f"{with_data:,}")
c3.metric("Combined Assets", f"₹{total_assets:.1f}L Cr", help="FY25")
c4.metric("Avg AUM Growth", f"{avg_growth:.1f}%", help="Latest 1Y")
c5.metric("Avg GNPA", f"{avg_gnpa:.2f}%", help="FY25")

# ── Tabs ──────────────────────────────────────────────────────────────────────

tabs = st.tabs([
    "📈 Growth", "💰 Profitability", "🏥 Asset Quality",
    "⚠️ Credit Losses", "📊 Trends", "🔍 Deep Dive",
    "💹 Valuation", "🌐 Universe", "🗃️ Data",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: GROWTH
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown('<div class="section-header">AUM Growth — Latest 1 Year (9MFY26 Ann. vs FY25 where available, else FY25 vs FY24)</div>',
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
                        COLOR["success"], f"Top {min(20, len(top_growers))} Fastest Growing")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = make_hbar(bottom_growers, "growth_pct", "display_name",
                        COLOR["danger"], "Slowest Growing / Contracting")
        st.plotly_chart(fig, use_container_width=True)

    st.caption("★ = estimated data. Where 9MFY26 data exists: growth vs FY25. Otherwise: FY25 vs FY24.")

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
            hover_name="name",
            labels={"growth_pct": "AUM Growth % (Latest 1Y)", "roa_pct": f"ROA % ({lbl})"},
            title=f"Growth vs Profitability — ROA as of {lbl} (bubble = loan book)",
            height=500,
        )
        fig.add_vline(x=median_growth, line_dash="dot", line_color=COLOR["text_secondary"],
                      annotation_text=f"Median: {median_growth:.1f}%")
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Growth by sector
    st.markdown('<div class="section-header">AUM Growth by Sector (Latest 1Y)</div>', unsafe_allow_html=True)
    sector_growth = growth_df.merge(
        fin_filtered[["name", "sector"]].drop_duplicates(), on="name", how="left"
    ).groupby("sector")["growth_pct"].mean().reset_index().sort_values("growth_pct", ascending=False)
    fig = make_hbar(sector_growth, "growth_pct", "sector", COLOR["primary"],
                    "Avg AUM Growth % by Sector")
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
                        f"Top {top_n} by ROA %")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        top_roe = latest_snap.nlargest(top_n, "roe_pct").sort_values("roe_pct", ascending=False)
        fig = make_hbar(top_roe, "roe_pct", "name", "#7c3aed",
                        f"Top {top_n} by ROE %")
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Where 9MFY26 data exists: 9MFY26 Ann. ROA/ROE used. Otherwise FY25. "
               f"★ = estimated data.")

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
                         marker_color="#7c3aed",
                         text=sector_avg["roe"].round(1), textposition="outside",
                         textfont=dict(family=CHART_MONO, size=10)))
    fig.update_layout(barmode="group", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                      title=dict(text=wrap_title(f"ROA & ROE by Sector ({lbl})"),
                                 font=dict(color=COLOR["text"], family=CHART_FONT, size=14, weight="bold"),
                                 x=0, xanchor="left", xref="paper",
                                 pad=dict(t=6, b=10)),
                      font=dict(color=COLOR["text_secondary"], family=CHART_FONT),
                      height=380,
                      margin=dict(t=82, b=70, l=10, r=24),
                      legend=dict(font=dict(family=CHART_FONT, size=11),
                                  bgcolor="rgba(255,255,255,0)", borderwidth=0,
                                  orientation="h", yanchor="bottom", y=-0.25,
                                  xanchor="left", x=0),
                      xaxis=dict(tickfont=dict(family=CHART_FONT, size=12), gridcolor=CHART_GRID,
                                 tickcolor="rgba(0,0,0,0)", linecolor="rgba(0,0,0,0)", title=""),
                      yaxis=dict(gridcolor=CHART_GRID, tickfont=dict(family=CHART_MONO, size=11),
                                 tickcolor="rgba(0,0,0,0)", title=""),
                      hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e4ede6",
                                      font=dict(family=CHART_FONT, size=12)),
                      uniformtext_minsize=8, uniformtext_mode="hide")
    st.plotly_chart(fig, use_container_width=True)

    # PAT trend — top 10
    st.markdown(f'<div class="section-header">PAT Trend — Top 10 Companies (incl. {lbl})</div>',
                unsafe_allow_html=True)
    top10_names = latest_snap.nlargest(10, "pat_cr")["name"].tolist()
    chart_df = get_chart_periods(fin_filtered)
    pat_trend = chart_df[chart_df["name"].isin(top10_names)][["name", "period", "pat_cr"]].dropna()

    fig = px.line(pat_trend, x="period", y="pat_cr", color="name",
                  labels={"pat_cr": "PAT (₹ Crore)", "period": "Period"},
                  title=f"Profit After Tax Trend — incl. {lbl} (₹ Crore)", height=460,
                  category_orders={"period": PERIOD_ORDER})
    chart_layout(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("9MFY26 (Ann.) = Q3 FY26 nine-month PAT annualised (×4/3).")

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
                        f"Lowest GNPA % ({lbl})")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        stressed = latest_snap.nlargest(20, "gnpa_pct").sort_values("gnpa_pct", ascending=False)
        fig = make_hbar(stressed, "gnpa_pct", "name", COLOR["danger"],
                        f"Highest GNPA % ({lbl})")
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"GNPA % is a stock/point-in-time metric — 9MFY26 (Ann.) uses Q3 value directly, no annualisation.")

    # Trend by sector
    st.markdown(f'<div class="section-header">GNPA Trend by Sector — FY2021 to {lbl}</div>',
                unsafe_allow_html=True)
    chart_df = get_chart_periods(fin_filtered)
    sector_gnpa = chart_df.groupby(["period", "sector"])["gnpa_pct"].mean().reset_index()
    fig = px.line(sector_gnpa, x="period", y="gnpa_pct", color="sector",
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
        colorscale=[[0, COLOR["success"]], [0.5, "#fbbf24"], [1, COLOR["danger"]]],
        text=[[f"{v:.1f}%" if not np.isnan(v) else "N/A" for v in row] for row in hm_df.values],
        texttemplate="%{text}",
        showscale=True,
    ))
    fig.update_layout(
        title=dict(text=wrap_title(f"GNPA % Heatmap (to {lbl})"),
                   font=dict(color=COLOR["text"], family=CHART_FONT, size=14, weight="bold"),
                   x=0, xanchor="left", xref="paper", pad=dict(t=6, b=8)),
        paper_bgcolor=CHART_BG,
        height=max(340, len(stressed_35) * 26),
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT, size=12),
        margin=dict(t=82, b=30, l=10, r=30),
        xaxis=dict(title=""),
        yaxis=dict(title=""),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e4ede6", font=dict(family=CHART_FONT, size=12)),
    )
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: CREDIT LOSSES
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.info("**Credit Loss Rate** = (Net Provisions + Write-offs − Recoveries) ÷ Loan Book. "
            "This is the actual P&L cost of defaults — different from GNPA which is a stock measure.")

    lbl = latest_period_label(fin_filtered)
    latest_snap = get_latest_period_data(fin_filtered).dropna(subset=["credit_loss_rate_pct"])

    col1, col2 = st.columns(2)
    with col1:
        lowest = latest_snap.nsmallest(20, "credit_loss_rate_pct").sort_values(
            "credit_loss_rate_pct", ascending=False)
        fig = make_hbar(lowest, "credit_loss_rate_pct", "name", COLOR["success"],
                        f"Lowest Credit Loss Rate ({lbl})")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        highest = latest_snap.nlargest(20, "credit_loss_rate_pct").sort_values(
            "credit_loss_rate_pct", ascending=False)
        fig = make_hbar(highest, "credit_loss_rate_pct", "name", COLOR["danger"],
                        f"Highest Credit Loss Rate ({lbl})")
        st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Credit loss rate % shown as of {lbl}. 9MFY26 (Ann.) uses Q3 ratio — not annualised.")

    # Trend for top stressed
    st.markdown(f'<div class="section-header">Credit Loss Rate Trend — FY2021 to {lbl}</div>',
                unsafe_allow_html=True)
    high12 = latest_snap.nlargest(12, "credit_loss_rate_pct")["name"].tolist()
    chart_df = get_chart_periods(fin_filtered)
    trend_df = chart_df[chart_df["name"].isin(high12)][
        ["name", "period", "credit_loss_rate_pct"]].dropna()

    fig = px.line(trend_df, x="period", y="credit_loss_rate_pct", color="name",
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
                         labels={"gnpa_pct": "GNPA %", "credit_loss_rate_pct": "Credit Loss Rate %"},
                         title=f"Credit Loss Rate vs GNPA — {lbl} (bubble = loan book)", height=520)
        chart_layout(fig)
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
                   x=0, xanchor="left", xref="paper", pad=dict(t=6, b=10)),
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT),
        height=bar_chart_height(len(wf)),
        xaxis=dict(title="", gridcolor=CHART_GRID,
                   tickfont=dict(family=CHART_MONO, size=11),
                   range=[-(wf_max * 1.5), wf_max * 1.5], zeroline=True,
                   zerolinecolor="#c8dfc4", zerolinewidth=1.5, tickcolor="rgba(0,0,0,0)"),
        yaxis=dict(tickfont=dict(family=CHART_FONT, size=12), showgrid=False,
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
        colorscale=[[0, COLOR["success"]], [0.5, "#fbbf24"], [1, COLOR["danger"]]],
        text=[[f"{v:.1f}%" if not np.isnan(v) else "N/A" for v in row] for row in hm_df.values],
        texttemplate="%{text}", showscale=True,
    ))
    fig.update_layout(
        title=dict(text=wrap_title(f"Credit Loss Rate % Heatmap (to {lbl})"),
                   font=dict(color=COLOR["text"], family=CHART_FONT, size=14, weight="bold"),
                   x=0, xanchor="left", xref="paper", pad=dict(t=6, b=8)),
        paper_bgcolor=CHART_BG, height=max(340, len(top40) * 26),
        font=dict(color=COLOR["text_secondary"], family=CHART_FONT, size=12),
        margin=dict(t=82, b=30, l=10, r=30),
        xaxis=dict(title=""),
        yaxis=dict(title=""),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e4ede6", font=dict(family=CHART_FONT, size=12)),
    )
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: TRENDS
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    lbl = latest_period_label(fin_filtered)
    latest_snap = get_latest_period_data(fin_filtered)
    top10 = latest_snap.nlargest(10, "loan_book_cr")["name"].tolist()
    chart_df = get_chart_periods(fin_filtered)

    # Stacked area — loan book (stock, Q3 as-is)
    st.markdown(f'<div class="section-header">Loan Book Growth — Top 10 (to {lbl})</div>',
                unsafe_allow_html=True)
    area_df = chart_df[chart_df["name"].isin(top10)][["name", "period", "loan_book_cr"]].dropna()
    fig = px.area(area_df, x="period", y="loan_book_cr", color="name",
                  title=f"Loan Book Growth — Top 10 NBFCs (₹ Crore, to {lbl})", height=460,
                  category_orders={"period": PERIOD_ORDER})
    chart_layout(fig)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("9MFY26 (Ann.) loan book = Q3 FY26 closing loan book (point-in-time, not annualised).")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="section-header">NII Trend (to {lbl})</div>', unsafe_allow_html=True)
        nii_df = chart_df[chart_df["name"].isin(top10)][
            ["name", "period", "net_interest_income_cr"]].dropna()
        fig = px.line(nii_df, x="period", y="net_interest_income_cr", color="name",
                      title=f"Net Interest Income (₹ Crore, to {lbl})", height=420,
                      category_orders={"period": PERIOD_ORDER})
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("9MFY26 (Ann.) NII = 9-month NII annualised (×4/3).")

    with col2:
        st.markdown(f'<div class="section-header">Industry Assets by RBI Layer (to {lbl})</div>',
                    unsafe_allow_html=True)
        layer_df = chart_df.groupby(["period", "rbi_layer"])["total_assets_cr"].sum().reset_index()
        fig = px.area(layer_df, x="period", y="total_assets_cr", color="rbi_layer",
                      title=f"Total Industry Assets by RBI Layer (₹ Crore, to {lbl})", height=420,
                      category_orders={"period": PERIOD_ORDER})
        chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("9MFY26 (Ann.) assets = Q3 FY26 closing total assets (point-in-time).")

    # ROA trend
    st.markdown(f'<div class="section-header">Return on Assets Trend (to {lbl})</div>',
                unsafe_allow_html=True)
    roa_df = chart_df[chart_df["name"].isin(top10)][["name", "period", "roa_pct"]].dropna()
    fig = px.line(roa_df, x="period", y="roa_pct", color="name",
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
    fig = make_hbar(top_pat, "cagr_pct", "name", "#7c3aed",
                    f"PAT CAGR % (FY21–25) — Top {top_n}")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: DEEP DIVE
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    companies_with_data = (
        fin_filtered[fin_filtered["has_financials"] == 1]["name"]
        .dropna().unique().tolist()
    )
    selected = st.selectbox("Select a company", sorted(companies_with_data))

    if selected:
        company_info_rows = nbfc_filtered[nbfc_filtered["name"] == selected]
        company_info = company_info_rows.iloc[0] if not company_info_rows.empty else None
        company_fin = fin_filtered[fin_filtered["name"] == selected].sort_values("period")

        # Badges
        if company_info is not None:
            layer_colors = {"Upper": "#4f46e5", "Middle": "#0891b2", "Base": "#64748b"}
            layer = company_info.get("rbi_layer", "Unknown")
            dq = company_info.get("data_quality", "")
            listed_val = company_info.get("listed", 0)
            badges = []
            badges.append(
                f'<span style="background:{layer_colors.get(layer,"#64748b")};'
                f'color:white;padding:3px 10px;border-radius:4px;font-size:12px;'
                f'font-weight:600">{layer} Layer</span>'
            )
            if dq == "estimated":
                badges.append('<span class="estimated-badge">⚠️ Estimated Data</span>')
            elif dq == "unverified":
                badges.append('<span class="unverified-badge">❌ Unverified</span>')
            if listed_val:
                badges.append(
                    '<span style="background:#dcfce7;color:#166534;padding:3px 10px;'
                    'border-radius:4px;font-size:12px;font-weight:600">Listed</span>'
                )
            st.markdown(" &nbsp; ".join(badges), unsafe_allow_html=True)
            st.markdown("")

        if company_info is not None and company_info.get("data_quality") in ["estimated", "unverified"]:
            st.warning("⚠️ This company's data includes estimated or unverified figures.")

        has_q3 = "FY2026-Q3" in company_fin["period"].values
        if has_q3:
            st.info("ℹ️ FY2026-Q3 data available. Charts show annualised 9MFY26 as latest period. "
                    "Annual averages use FY2021–FY2025 only.")

        # Check for Fibe Q2/Q3 gap
        if "Fibe" in selected or "EarlySalary" in selected:
            st.warning("ℹ️ Fibe (EarlySalary): FY2026 Q2 and Q3 data unavailable — showing FY2025 as latest.")

        # Key metrics
        lbl = latest_period_label(company_fin)
        latest_snap = get_latest_period_data(company_fin)
        if not latest_snap.empty:
            r = latest_snap.iloc[0]
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Total Assets", f"₹{r['total_assets_cr']:,.0f} Cr" if pd.notna(r.get("total_assets_cr")) else "N/A", help=lbl)
            m2.metric("Loan Book", f"₹{r['loan_book_cr']:,.0f} Cr" if pd.notna(r.get("loan_book_cr")) else "N/A", help=lbl)
            m3.metric("PAT", f"₹{r['pat_cr']:,.0f} Cr" if pd.notna(r.get("pat_cr")) else "N/A", help=lbl)
            m4.metric("GNPA %", f"{r['gnpa_pct']:.2f}%" if pd.notna(r.get("gnpa_pct")) else "N/A", help=lbl)
            m5.metric("ROA %", f"{r['roa_pct']:.2f}%" if pd.notna(r.get("roa_pct")) else "N/A", help=lbl)

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
                         title=f"Assets & Loan Book (₹ Crore, to {lbl})", height=400,
                         category_orders={"period": PERIOD_ORDER})
            fig.update_traces(textposition="outside", textfont=dict(family=CHART_MONO, size=11),
                              cliponaxis=False)
            chart_layout(fig)
            fig.update_layout(xaxis=dict(tickangle=-30), margin=DD_MARGIN, legend=DD_LEGEND)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            nii_pat = chart_df[["period", "net_interest_income_cr", "pat_cr"]].dropna().rename(
                columns={"net_interest_income_cr": "NII", "pat_cr": "PAT"})
            fig = px.line(nii_pat, x="period", y=["NII", "PAT"],
                          title=f"NII & PAT (₹ Crore, to {lbl})", height=400,
                          category_orders={"period": PERIOD_ORDER}, markers=True)
            chart_layout(fig)
            fig.update_layout(xaxis=dict(tickangle=-30), margin=DD_MARGIN, legend=DD_LEGEND)
            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            gnpa_df = chart_df[["period", "gnpa_pct"]].dropna()
            fig = px.line(gnpa_df, x="period", y="gnpa_pct",
                          title=f"GNPA % Trend (to {lbl})", markers=True, height=380,
                          category_orders={"period": PERIOD_ORDER})
            fig.update_traces(line_color=COLOR["danger"], marker_color=COLOR["danger"])
            chart_layout(fig)
            fig.update_layout(xaxis=dict(tickangle=-30), margin=DD_MARGIN, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with col4:
            ror_df = chart_df[["period", "roa_pct", "roe_pct"]].dropna().rename(
                columns={"roa_pct": "ROA %", "roe_pct": "ROE %"})
            fig = px.line(ror_df, x="period", y=["ROA %", "ROE %"],
                          title=f"ROA & ROE % (to {lbl})", markers=True, height=380,
                          category_orders={"period": PERIOD_ORDER})
            chart_layout(fig)
            fig.update_layout(xaxis=dict(tickangle=-30), margin=DD_MARGIN, legend=DD_LEGEND)
            st.plotly_chart(fig, use_container_width=True)

        cl_df = chart_df[["period", "credit_loss_rate_pct"]].dropna()
        fig = px.line(cl_df, x="period", y="credit_loss_rate_pct",
                      title=f"Credit Loss Rate % (to {lbl})", markers=True, height=380,
                      category_orders={"period": PERIOD_ORDER})
        fig.add_hline(y=2.0, line_dash="dot", line_color=COLOR["warning"],
                      annotation_text="2% reference")
        chart_layout(fig)
        fig.update_layout(xaxis=dict(tickangle=-30), margin=DD_MARGIN, showlegend=False)
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
            st.caption("9MFY26 (Ann.): flow metrics (NII, PAT) annualised ×4/3. "
                       "Stock/ratio metrics (assets, loan book, GNPA, ROA, ROE) shown as Q3 point-in-time.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7: VALUATION
# ─────────────────────────────────────────────────────────────────────────────
with tabs[6]:
    st.info("📡 Live data from Yahoo Finance. P/E is trailing twelve months. Refreshes every hour.")

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
            st.error("Could not fetch live data and no cached data available. Try again later.")
            st.stop()
    else:
        # Successful fetch — save to disk cache for next time
        save_val_cache(val_with_price)

    if using_cache:
        st.warning(f"⚠️ Live fetch failed (Yahoo Finance rate limit). Showing last cached data from **{cache_ts}**.")
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
                            height=bar_chart_height(len(pe_df)))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            pb_df = val_with_price.dropna(subset=["pb"]).sort_values("pb", ascending=False)
            fig = make_hbar(pb_df, "pb", "company", "#7c3aed", "P/B Ratio",
                            height=bar_chart_height(len(pb_df)))
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
                       x=0, xanchor="left", xref="paper", pad=dict(t=6, b=10)),
            paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            font=dict(color=COLOR["text_secondary"], family=CHART_FONT),
            height=bar_chart_height(len(chg_df)),
            yaxis=dict(autorange="reversed", tickfont=dict(family=CHART_FONT, size=12),
                       showgrid=False, tickcolor="rgba(0,0,0,0)", title=""),
            xaxis=dict(title="", gridcolor=CHART_GRID,
                       tickfont=dict(family=CHART_MONO, size=11),
                       range=[-(chg_max * 1.5), chg_max * 1.5],
                       zeroline=True, zerolinecolor="#c8dfc4", zerolinewidth=1.5,
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
# TAB 8: UNIVERSE
# ─────────────────────────────────────────────────────────────────────────────
with tabs[7]:
    lbl = latest_period_label(fin_filtered)

    st.markdown('<div class="section-header">RBI Layer Distribution (Full 9,359 Registry)</div>',
                unsafe_allow_html=True)
    layer_counts = pd.DataFrame({
        "Layer": ["Upper", "Middle", "Base"],
        "Count": [16, 100, 9243],
    })
    col1, col2 = st.columns([1, 2])
    with col1:
        fig = px.pie(layer_counts, values="Count", names="Layer", hole=0.5,
                     color_discrete_map={"Upper": COLOR["primary"], "Middle": "#0891b2", "Base": "#64748b"})
        fig.update_layout(
            paper_bgcolor=CHART_BG,
            font=dict(family=CHART_FONT, color=COLOR["text_secondary"]),
            title=dict(text="NBFCs by RBI Layer",
                       font=dict(color=COLOR["text"], family=CHART_FONT, size=14, weight="bold"),
                       x=0, xanchor="left", xref="paper", pad=dict(t=6, b=10)),
            margin=dict(t=82, b=20, l=10, r=10),
            legend=dict(font=dict(family=CHART_FONT, size=12),
                        bgcolor="rgba(255,255,255,0)", borderwidth=0),
            hoverlabel=dict(bgcolor="#ffffff", bordercolor="#e4ede6",
                            font=dict(family=CHART_FONT, size=12)),
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.dataframe(layer_counts, hide_index=True, use_container_width=True)

    # Sector coverage
    st.markdown('<div class="section-header">Financial Data Coverage by Sector</div>',
                unsafe_allow_html=True)
    sector_counts = (
        nbfc_filtered[nbfc_filtered["has_financials"] == 1]
        .groupby("sector").size().reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    fig = make_hbar(sector_counts, "count", "sector", COLOR["primary"],
                    "Companies with Financial Data by Sector")
    st.plotly_chart(fig, use_container_width=True)

    # Full sortable table
    st.markdown(f'<div class="section-header">All Companies — Key Metrics as of {lbl}</div>',
                unsafe_allow_html=True)
    latest_snap = get_latest_period_data(fin_filtered)[
        ["name", "total_assets_cr", "loan_book_cr", "gnpa_pct", "roa_pct", "roe_pct", "data_quality"]
    ]
    universe_table = nbfc_filtered.merge(latest_snap, on="name", how="left",
                                         suffixes=("", "_fin"))

    dq_col = "data_quality_fin" if "data_quality_fin" in universe_table.columns else "data_quality"
    universe_table["⚠️"] = universe_table[dq_col].apply(
        lambda x: "⚠️ Est." if x == "estimated" else ("❌ Unverified" if x == "unverified" else "✓")
    )
    universe_table = universe_table.sort_values("total_assets_cr", ascending=False, na_position="last")

    st.dataframe(universe_table[[
        "name", "rbi_layer", "sector", "listed", "total_assets_cr",
        "loan_book_cr", "gnpa_pct", "roa_pct", "roe_pct", "⚠️",
    ]].rename(columns={
        "name": "Company", "rbi_layer": "Layer", "sector": "Sector",
        "listed": "Listed", "total_assets_cr": f"Assets (₹ Cr, {lbl})",
        "loan_book_cr": f"Loan Book (₹ Cr, {lbl})", "gnpa_pct": f"GNPA % ({lbl})",
        "roa_pct": f"ROA % ({lbl})", "roe_pct": f"ROE % ({lbl})",
    }), use_container_width=True, hide_index=True)
    st.caption(f"Metrics as of {lbl}. 9MFY26 (Ann.): flow metrics annualised ×4/3; ratios/stock metrics are Q3 point-in-time.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 9: DATA
# ─────────────────────────────────────────────────────────────────────────────
with tabs[8]:
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
        f"Where FY2026-Q3 data exists, 9MFY26 (Ann.) is shown. "
        f"Flow metrics annualised ×4/3. Ratios/stock metrics are Q3 point-in-time."
    )

    # CSV download
    csv = metrics_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "nbfc_metrics.csv", "text/csv")

    # Full history
    st.markdown('<div class="section-header">Full Financial History (Annual + 9MFY26 Ann.)</div>',
                unsafe_allow_html=True)
    raw = get_chart_periods(fin_filtered).copy()
    if search:
        raw = raw[raw["name"].str.contains(search, case=False, na=False)]
    st.dataframe(raw.drop(columns=["id", "nbfc_id"], errors="ignore"),
                 use_container_width=True, hide_index=True)
    st.caption("Raw quarterly rows (Q1, Q2, Q3) are excluded. Only annual (FY2021–FY2025) and annualised 9MFY26 rows shown.")
