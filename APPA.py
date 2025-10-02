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

st.set_page_config(page_title="Springboard Planner", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
}

.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2.5rem;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    margin-bottom: 2rem;
}

.main-header h1 {
    color: white;
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
}

.main-header p {
    color: rgba(255,255,255,0.9);
    font-size: 1.1rem;
    margin: 0.5rem 0 0 0;
    font-weight: 400;
}

.config-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
    border: 1px solid rgba(0,0,0,0.05);
}

.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.icon {
    font-size: 1.8rem;
}

.anchor-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
    border: 1px solid rgba(0,0,0,0.05);
}

.anchor-list-header {
    display: grid;
    grid-template-columns: 1.2fr 1.2fr 1fr 1fr 0.5fr;
    gap: 1rem;
    padding: 1rem;
    background: #f7fafc;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #4a5568;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.anchor-list-row {
    display: grid;
    grid-template-columns: 1.2fr 1.2fr 1fr 1fr 0.5fr;
    gap: 1rem;
    padding: 1rem;
    background: white;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    border: 1px solid #e2e8f0;
    align-items: center;
    transition: all 0.2s;
}

.anchor-list-row:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-color: #cbd5e0;
}

.plan-cards-section {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
    border: 1px solid rgba(0,0,0,0.05);
}

.current-time-badge {
    display: inline-block;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 0.5rem 1.25rem;
    border-radius: 20px;
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

.plan-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-top: 1rem;
}

.plan-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    border-radius: 16px;
    padding: 1.75rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    border: 2px solid #e9ecef;
    transition: all 0.3s;
}

.plan-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    border-color: #667eea;
}

.plan-card-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.plan-card-value {
    font-size: 2.25rem;
    font-weight: 800;
    color: #667eea;
    margin: 0.75rem 0;
    letter-spacing: -1px;
}

.plan-card-label {
    font-size: 0.9rem;
    color: #718096;
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.plan-card-mirror {
    font-size: 1.1rem;
    color: #48bb78;
    font-weight: 700;
    margin-top: 0.5rem;
}

.plan-card-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    margin: 1rem 0;
}

.plan-card-meta {
    font-size: 0.85rem;
    color: #a0aec0;
    margin-top: 0.25rem;
}

.tables-section {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 2rem;
    border: 1px solid rgba(0,0,0,0.05);
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
}

.footer-note {
    background: #f7fafc;
    border-left: 4px solid #667eea;
    padding: 1.25rem 1.5rem;
    border-radius: 8px;
    color: #4a5568;
    font-size: 0.95rem;
    line-height: 1.6;
    margin-top: 1rem;
}

div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input,
div[data-testid="stTimeInput"] input,
div[data-testid="stSelectbox"] select {
    border-radius: 10px;
    border: 2px solid #e2e8f0;
    padding: 0.75rem;
    font-size: 1rem;
    transition: all 0.2s;
}

div[data-testid="stNumberInput"] input:focus,
div[data-testid="stDateInput"] input:focus,
div[data-testid="stTimeInput"] input:focus,
div[data-testid="stSelectbox"] select:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.stButton button {
    border-radius: 10px;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    transition: all 0.2s;
    border: none;
}

.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stButton button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: #f7fafc;
    padding: 0.5rem;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.2s;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.stDownloadButton button {
    background: #48bb78;
    color: white;
    border-radius: 10px;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    transition: all 0.2s;
}

.stDownloadButton button:hover {
    background: #38a169;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(72, 187, 120, 0.3);
}

div[data-testid="stCheckbox"] {
    background: #f7fafc;
    padding: 0.75rem 1rem;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>📊 Springboard Planner</h1>
    <p>Manual anchors → projected RTH tables, time-aware entries</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="config-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title"><span class="icon">⚙️</span> Configuration</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns([1.3,1,1,1])
with c1:
    proj_date = st.date_input("Projected RTH Date (CT)", value=pd.Timestamp.today(tz=CT).date())
with c2:
    slope_down = st.number_input("Descending slope /30m", value=CFG.slope_down, step=0.05, format="%.2f")
with c3:
    slope_up = st.number_input("Ascending slope /30m", value=CFG.slope_up, step=0.05, format="%.2f")
with c4:
    show_blocks = st.toggle("Show blocks column", value=False)
st.markdown('</div>', unsafe_allow_html=True)

CFG.slope_down = float(slope_down)
CFG.slope_up = float(slope_up)

st.markdown('<div class="anchor-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title"><span class="icon">⚓</span> Add Anchor</div>', unsafe_allow_html=True)
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
    add_clicked = st.button("➕ Add to list", use_container_width=True, key="add_anchor", type="primary")

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
    st.markdown('<div style="margin-top: 2rem;">', unsafe_allow_html=True)
    st.markdown("""
    <div class="anchor-list-header">
        <div>Name</div>
        <div>Timestamp (CT)</div>
        <div>Price (H)</div>
        <div>Slopes (↓/↑)</div>
        <div>Action</div>
    </div>
    """, unsafe_allow_html=True)
    
    del_idx = None
    for i, a in enumerate(st.session_state.anchors):
        col1, col2, col3, col4, col5 = st.columns([1.2,1.2,1,1,0.5])
        with col1:
            st.markdown(f"**{a['label']}**")
        with col2:
            st.write(a["ts"].strftime("%Y-%m-%d %H:%M"))
        with col3:
            st.write(f"{a['price']:.2f}")
        with col4:
            st.write(f"{a['slope_down']:+.2f} / {a['slope_up']:+.2f}")
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

st.markdown('<div class="plan-cards-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title"><span class="icon">📈</span> Plan Cards</div>', unsafe_allow_html=True)
st.markdown(f'<div class="current-time-badge">🕐 Current CT: {now_ct.strftime("%Y-%m-%d %H:%M")}  •  Showing entries for: {plan_time.strftime("%H:%M")}</div>', unsafe_allow_html=True)

st.markdown('<div class="plan-grid">', unsafe_allow_html=True)
for a in st.session_state.anchors:
    b = blocks_between(a["ts"], plan_time, CFG.maint_start, CFG.maint_end)
    desc = a["price"] + a["slope_down"] * b
    asc = a["price"] + a["slope_up"] * b
    card = f"""
    <div class="plan-card">
        <div class="plan-card-header">🎯 {a['label']} — {plan_time.strftime('%H:%M')}</div>
        <div class="plan-card-label">Entry (descending)</div>
        <div class="plan-card-value">{desc:.2f}</div>
        <div class="plan-card-mirror">Exit mirror: {asc:.2f}</div>
        <div class="plan-card-divider"></div>
        <div class="plan-card-meta">📊 Blocks since anchor: {b}</div>
        <div class="plan-card-meta">⚓ Anchor @ {a['ts'].strftime('%Y-%m-%d %H:%M')} • H={a['price']:.2f}</div>
    </div>
    """
    st.markdown(card, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="tables-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title"><span class="icon">📋</span> Projection Tables (RTH)</div>', unsafe_allow_html=True)

if not st.session_state.anchors:
    st.info("💡 Add at least one anchor to generate tables.")
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
                f"⬇️ Download {a['label']} table",
                df_out.to_csv(index=False).encode("utf-8"),
                file_name=f"{a['label']}_{proj_ts.date()}_RTH.csv",
                mime="text/csv",
            )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="footer-note">
    ℹ️ Entries use descending line (−0.25/30m default). Exits use ascending line (+0.25/30m). Maintenance 16:00–17:00 excluded from block counts. Overnight anchors are supported.
</div>
""", unsafe_allow_html=True)
