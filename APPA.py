from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import pytz
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime as pydt

CT = pytz.timezone("America/Chicago")

@dataclass
class AppCfg:
    slope_down: float = -0.25
    slope_up: float = 0.25
    rth_start: str = "08:30"
    rth_end: str = "15:00"
    maint_start: str = "16:00"
    maint_end: str = "17:00"

CFG = AppCfg()

def to_ct(ts: pd.Timestamp) -> pd.Timestamp:
    if ts.tzinfo is None:
        return ts.tz_localize(CT)
    return ts.tz_convert(CT)

def rth_slots(day: pd.Timestamp, start="08:30", end="15:00") -> pd.DatetimeIndex:
    day = to_ct(pd.Timestamp(day.date(), tz=CT))
    sh, sm = map(int, start.split(":"))
    eh, em = map(int, end.split(":"))
    t0 = day + pd.Timedelta(hours=sh, minutes=sm)
    t1 = day + pd.Timedelta(hours=eh, minutes=em)
    return pd.date_range(t0, t1, freq="30min", inclusive="left", tz=CT)

def blocks_between(start_ts: pd.Timestamp, end_ts: pd.Timestamp, maint_start="16:00", maint_end="17:00") -> int:
    if end_ts <= start_ts:
        return 0
    s = to_ct(start_ts).ceil("30min")
    e = to_ct(end_ts)
    rng = pd.date_range(s, e, freq="30min", inclusive="left", tz=CT)
    mask = ~(((rng.hour == 16) & (rng.minute == 0)) | ((rng.hour == 16) & (rng.minute == 30)))
    return int(mask.sum())

def round_to_nearest_30m(now_ct: pd.Timestamp) -> pd.Timestamp:
    now_ct = to_ct(now_ct)
    minute = now_ct.minute
    base = now_ct.replace(second=0, microsecond=0)
    if minute % 30 == 0:
        return base
    if (minute % 30) < 15:
        return base - pd.Timedelta(minutes=(minute % 30))
    else:
        return base + pd.Timedelta(minutes=30 - (minute % 30))

if "anchors" not in st.session_state:
    st.session_state.anchors = []

COOL_NAMES = [
    "Comet", "Nebula", "Aurora", "Quasar", "Pulsar", "Photon",
    "Zenith", "Halo", "Vortex", "Eclipse", "Nova", "Orbit"
]

def available_names():
    used = {a["label"] for a in st.session_state.anchors}
    return [n for n in COOL_NAMES if n not in used]

st.set_page_config(page_title="SPX Prophet", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    padding: 2rem 3rem;
    background: #f8f9fb;
    max-width: 1600px;
}

.main-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #2563eb 100%);
    padding: 3rem 3rem 3rem 3rem;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(30, 58, 138, 0.25);
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, transparent 0%, rgba(255,255,255,0.05) 100%);
    pointer-events: none;
}

.header-content {
    position: relative;
    z-index: 1;
}

.main-header h1 {
    color: #ffffff;
    font-size: 3rem;
    font-weight: 900;
    margin: 0;
    letter-spacing: -1px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.main-header p {
    color: #e0e7ff;
    font-size: 1.15rem;
    margin: 0.75rem 0 0 0;
    font-weight: 500;
    letter-spacing: 0.3px;
}

.section-container {
    background: #ffffff;
    border-radius: 16px;
    padding: 2.5rem;
    box-shadow: 0 2px 20px rgba(0,0,0,0.06);
    margin-bottom: 2rem;
    border: 1px solid #e5e7eb;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #f3f4f6;
}

.section-icon {
    font-size: 2rem;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.section-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #1f2937;
    margin: 0;
    letter-spacing: -0.3px;
}

.input-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.anchor-list {
    margin-top: 2rem;
}

.anchor-header {
    display: grid;
    grid-template-columns: 1.2fr 1.2fr 1fr 1fr 0.5fr;
    gap: 1.5rem;
    padding: 1rem 1.5rem;
    background: #f9fafb;
    border-radius: 12px;
    margin-bottom: 1rem;
}

.anchor-header-cell {
    font-weight: 700;
    color: #374151;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.anchor-row {
    display: grid;
    grid-template-columns: 1.2fr 1.2fr 1fr 1fr 0.5fr;
    gap: 1.5rem;
    padding: 1.25rem 1.5rem;
    background: #ffffff;
    border: 2px solid #f3f4f6;
    border-radius: 12px;
    margin-bottom: 0.75rem;
    align-items: center;
    transition: all 0.2s ease;
}

.anchor-row:hover {
    border-color: #2563eb;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.1);
    transform: translateY(-2px);
}

.anchor-name {
    font-weight: 700;
    color: #1f2937;
    font-size: 1.05rem;
}

.anchor-data {
    color: #4b5563;
    font-size: 0.95rem;
    font-weight: 500;
}

.status-badge {
    display: inline-block;
    background: #dbeafe;
    color: #1e40af;
    padding: 0.5rem 1.25rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 2rem;
    box-shadow: 0 2px 8px rgba(30, 64, 175, 0.15);
}

.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2rem;
    margin-top: 1.5rem;
}

.metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
    border: 2px solid #e5e7eb;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
}

.metric-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 32px rgba(37, 99, 235, 0.15);
    border-color: #2563eb;
}

.metric-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.25rem;
}

.metric-name {
    font-size: 1.2rem;
    font-weight: 800;
    color: #1f2937;
}

.metric-time {
    font-size: 0.85rem;
    color: #6b7280;
    font-weight: 600;
}

.metric-value-section {
    margin: 1.5rem 0;
}

.metric-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #6b7280;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 900;
    color: #2563eb;
    letter-spacing: -1.5px;
    margin: 0.5rem 0;
}

.metric-exit {
    font-size: 1.15rem;
    color: #059669;
    font-weight: 700;
    margin-top: 0.75rem;
}

.metric-divider {
    height: 1px;
    background: #e5e7eb;
    margin: 1.5rem 0;
}

.metric-meta {
    font-size: 0.85rem;
    color: #6b7280;
    margin-top: 0.5rem;
    font-weight: 500;
}

.info-banner {
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    border-left: 4px solid #2563eb;
    padding: 1.5rem 2rem;
    border-radius: 12px;
    color: #1e40af;
    font-size: 0.95rem;
    line-height: 1.7;
    margin-top: 1.5rem;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
}

div[data-testid="stNumberInput"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stTimeInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label {
    font-weight: 700;
    color: #374151;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input,
div[data-testid="stTimeInput"] input,
div[data-testid="stSelectbox"] select,
div[data-testid="stTextInput"] input {
    border-radius: 10px;
    border: 2px solid #d1d5db;
    padding: 0.75rem 1rem;
    font-size: 0.95rem;
    font-weight: 500;
    color: #1f2937;
    transition: all 0.2s ease;
    background: #ffffff;
}

div[data-testid="stNumberInput"] input:focus,
div[data-testid="stDateInput"] input:focus,
div[data-testid="stTimeInput"] input:focus,
div[data-testid="stSelectbox"] select:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    outline: none;
}

.stButton button {
    border-radius: 10px;
    font-weight: 700;
    padding: 0.85rem 2rem;
    transition: all 0.2s ease;
    border: none;
    font-size: 0.95rem;
}

.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.stButton button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
}

.stButton button:not([kind="primary"]) {
    background: #ef4444;
    color: white;
}

.stButton button:not([kind="primary"]):hover {
    background: #dc2626;
    transform: scale(1.05);
}

div[data-testid="stCheckbox"] {
    background: #f9fafb;
    padding: 1rem 1.25rem;
    border-radius: 10px;
    border: 2px solid #e5e7eb;
}

div[data-testid="stCheckbox"] label {
    font-weight: 600;
    color: #374151;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.75rem;
    background: #f9fafb;
    padding: 0.75rem;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.85rem 1.75rem;
    font-weight: 700;
    color: #4b5563;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 2px solid #e5e7eb;
}

.stDataFrame [data-testid="stDataFrameResizable"] {
    font-weight: 500;
    color: #374151;
}

.stDownloadButton button {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    color: white;
    border-radius: 10px;
    font-weight: 700;
    padding: 0.85rem 2rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
}

.stDownloadButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(5, 150, 105, 0.4);
}

.stAlert {
    border-radius: 12px;
    border: 2px solid #3b82f6;
    background: #eff6ff;
    padding: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <div class="header-content">
        <h1>📈 SPX Prophet</h1>
        <p>Predicting The Future of SPX500</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="section-icon">⚙️</span>
    <h2 class="section-title">Configuration Settings</h2>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([1.3,1,1,1])
with c1:
    proj_date = st.date_input("Projected RTH Date (CT)", value=pd.Timestamp.today(tz=CT).date())
with c2:
    slope_down = st.number_input("Descending slope /30m", value=CFG.slope_down, step=0.05, format="%.2f")
with c3:
    slope_up = st.number_input("Ascending slope /30m", value=CFG.slope_up, step=0.05, format="%.2f")
with c4:
    st.markdown("<br>", unsafe_allow_html=True)
    show_blocks = st.toggle("Show blocks column", value=False)

st.markdown('</div>', unsafe_allow_html=True)

CFG.slope_down = float(slope_down)
CFG.slope_up = float(slope_up)

st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="section-icon">⚓</span>
    <h2 class="section-title">Anchor Management</h2>
</div>
""", unsafe_allow_html=True)

ca1, ca2, ca3, ca4, ca5 = st.columns([1.1,1.1,1,1,1.1])
with ca1:
    opts = available_names()
    if opts:
        a_label = st.selectbox("Anchor name", opts, index=0, key="anchor_name_select")
    else:
        a_label = st.text_input("Anchor name", value=f"Anchor{len(st.session_state.anchors)+1}", key="anchor_name_text")
with ca2:
    a_date = st.date_input("Anchor date (CT)", value=(pd.Timestamp(proj_date) - pd.Timedelta(days=1)).date(), key="anchor_date")
with ca3:
    a_time = st.time_input("Anchor time (CT)", value=pd.Timestamp("1900-01-01 10:30").time(), key="anchor_time")
with ca4:
    a_price = st.number_input("Anchor price (H)", min_value=0.0, value=6721.80, step=0.1, format="%.2f", key="anchor_price")
with ca5:
    st.markdown("<br>", unsafe_allow_html=True)
    add_clicked = st.button("➕ Add Anchor", use_container_width=True, key="add_anchor", type="primary")

if add_clicked:
    label_val = (a_label if opts else (a_label.strip() or f"Anchor{len(st.session_state.anchors)+1}"))
    naive_dt = pydt.combine(a_date, a_time)
    ts = CT.localize(naive_dt)
    st.session_state.anchors.append({
        "label": label_val,
        "ts": pd.Timestamp(ts),
        "price": float(a_price),
        "slope_down": CFG.slope_down,
        "slope_up": CFG.slope_up
    })

if st.session_state.anchors:
    st.markdown('<div class="anchor-list">', unsafe_allow_html=True)
    st.markdown("""
    <div class="anchor-header">
        <div class="anchor-header-cell">Name</div>
        <div class="anchor-header-cell">Timestamp (CT)</div>
        <div class="anchor-header-cell">Price (H)</div>
        <div class="anchor-header-cell">Slopes (↓/↑)</div>
        <div class="anchor-header-cell">Action</div>
    </div>
    """, unsafe_allow_html=True)
    
    del_idx = None
    for i, a in enumerate(st.session_state.anchors):
        col1, col2, col3, col4, col5 = st.columns([1.2,1.2,1,1,0.5])
        with col1:
            st.markdown(f'<div class="anchor-name">{a["label"]}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="anchor-data">{a["ts"].strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="anchor-data">{a["price"]:.2f}</div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="anchor-data">{a["slope_down"]:+.2f} / {a["slope_up"]:+.2f}</div>', unsafe_allow_html=True)
        with col5:
            if st.button("🗑️", key=f"del_{i}"):
                del_idx = i
    
    if del_idx is not None:
        st.session_state.anchors.pop(del_idx)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

proj_ts = to_ct(pd.Timestamp(proj_date, tz=CT))
slots = rth_slots(proj_ts, CFG.rth_start, CFG.rth_end)
now_ct = to_ct(pd.Timestamp.now(tz=CT))
rounded = round_to_nearest_30m(now_ct)
if rounded < slots[0]:
    plan_time = slots[0]
elif rounded >= slots[-1]:
    plan_time = slots[-1]
else:
    plan_time = min(slots, key=lambda s: abs((s - rounded).total_seconds()))

st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="section-icon">📊</span>
    <h2 class="section-title">Live Trading Metrics</h2>
</div>
""", unsafe_allow_html=True)

st.markdown(f'<div class="status-badge">🕐 Current CT: {now_ct.strftime("%Y-%m-%d %H:%M")} • Showing entries for: {plan_time.strftime("%H:%M")}</div>', unsafe_allow_html=True)

st.markdown('<div class="cards-grid">', unsafe_allow_html=True)
for a in st.session_state.anchors:
    b = blocks_between(a["ts"], plan_time, CFG.maint_start, CFG.maint_end)
    desc = a["price"] + a["slope_down"] * b
    asc = a["price"] + a["slope_up"] * b
    card = f"""
    <div class="metric-card">
        <div class="metric-header">
            <div class="metric-name">{a['label']}</div>
            <div class="metric-time">{plan_time.strftime('%H:%M')}</div>
        </div>
        <div class="metric-value-section">
            <div class="metric-label">Entry (Descending)</div>
            <div class="metric-value">{desc:.2f}</div>
            <div class="metric-exit">Exit Mirror: {asc:.2f}</div>
        </div>
        <div class="metric-divider"></div>
        <div class="metric-meta">📊 Blocks since anchor: {b}</div>
        <div class="metric-meta">⚓ Anchor @ {a['ts'].strftime('%Y-%m-%d %H:%M')} • H={a['price']:.2f}</div>
    </div>
    """
    st.markdown(card, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="section-icon">📋</span>
    <h2 class="section-title">Projection Tables (RTH)</h2>
</div>
""", unsafe_allow_html=True)

if not st.session_state.anchors:
    st.info("💡 Add at least one anchor to generate projection tables.")
else:
    tabs = st.tabs([f"📊 {a['label']}" for a in st.session_state.anchors])
    for tab, a in zip(tabs, st.session_state.anchors):
        with tab:
            rows = []
            for t in slots:
                b = blocks_between(a["ts"], t, CFG.maint_start, CFG.maint_end)
                desc = a["price"] + a["slope_down"] * b
                asc = a["price"] + a["slope_up"] * b
                entry_time_str = to_ct(t).strftime("%Y-%m-%d %H:%M")
                rows.append({
                    "Entry Time (CT)": entry_time_str,
                    "Blocks": b,
                    "Entry (Descending)": round(desc, 2),
                    "Exit (Ascending)": round(asc, 2)
                })
            df_out = pd.DataFrame(rows)
            if not show_blocks:
                df_out = df_out[["Entry Time (CT)", "Entry (Descending)", "Exit (Ascending)"]]
            st.dataframe(df_out, use_container_width=True, hide_index=True)
            st.download_button(
                f"⬇️ Download {a['label']} CSV",
                df_out.to_csv(index=False).encode("utf-8"),
                file_name=f"{a['label']}_{proj_ts.date()}_RTH.csv",
                mime="text/csv",
            )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-banner">
    <strong>ℹ️ Trading Parameters:</strong> Entries use descending line (−0.25/30m default). Exits use ascending line (+0.25/30m). Maintenance window 16:00–17:00 excluded from block counts. Overnight anchors are supported.
</div>
""", unsafe_allow_html=True)
