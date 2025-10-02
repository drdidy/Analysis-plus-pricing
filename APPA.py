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
:root {
  --glass-bg: rgba(255,255,255,0.10);
  --glass-border: rgba(255,255,255,0.18);
  --glass-shadow: 0 8px 32px rgba(31,38,135,0.25);
}
.block-container {padding-top: 1.0rem;}
.glass {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 18px;
  box-shadow: var(--glass-shadow);
  padding: 1rem 1.2rem;
}
.header { font-size: 1.6rem; font-weight: 700; letter-spacing: .2px; }
.subtle {opacity: .75}
.plan-grid {
  display:grid; grid-template-columns: repeat(auto-fit,minmax(240px,1fr));
  gap: 14px; margin-top: .5rem;
}
.plan-card {
  background: rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.18);
  border-radius:14px; padding: 14px; box-shadow: var(--glass-shadow);
}
.plan-title { font-weight: 700; font-size: 1rem; display:flex; align-items:center; gap:.5rem}
.plan-kpi { font-size: 1.6rem; font-weight: 800; margin-top:.35rem;}
.kpi-sub { font-size:.8rem; opacity:.8}
hr.sep {border:0; height:1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,.25), transparent); margin: 14px 0 10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">Springboard Planner</div><span class="subtle">Manual anchors → projected RTH tables, time-aware entries</span>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([1.3,1,1,1])
with c1:
    proj_date = st.date_input("Projected RTH Date (CT)", value=pd.Timestamp.today(tz=CT).date())
with c2:
    slope_down = st.number_input("Descending slope /30m", value=CFG.slope_down, step=0.05, format="%.2f")
with c3:
    slope_up = st.number_input("Ascending slope /30m", value=CFG.slope_up, step=0.05, format="%.2f")
with c4:
    show_blocks = st.toggle("Show blocks column", value=False)

CFG.slope_down = float(slope_down)
CFG.slope_up = float(slope_up)

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('**Add Anchor**', unsafe_allow_html=True)
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
    add_clicked = st.button("Add to list", use_container_width=True, key="add_anchor")

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
    st.markdown("<hr class='sep'/>", unsafe_allow_html=True)
    v_cols = st.columns([1.2,1.2,1,1,0.5])
    with v_cols[0]:
        st.write("**Name**")
    with v_cols[1]:
        st.write("**Timestamp (CT)**")
    with v_cols[2]:
        st.write("**Price (H)**")
    with v_cols[3]:
        st.write("**Slopes (↓/↑)**")
    with v_cols[4]:
        st.write("**Del**")
    del_idx = None
    for i, a in enumerate(st.session_state.anchors):
        v1, v2, v3, v4, v5 = st.columns([1.2,1.2,1,1,0.5])
        with v1:
            st.write(a['label'])
        with v2:
            st.write(a["ts"].strftime("%Y-%m-%d %H:%M"))
        with v3:
            st.write(f"{a['price']:.2f}")
        with v4:
            st.write(f"{a['slope_down']:+.2f} / {a['slope_up']:+.2f}")
        with v5:
            if st.button("✖", key=f"del_{i}"):
                del_idx = i
    if del_idx is not None:
        st.session_state.anchors.pop(del_idx)
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

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('**Plan Cards**', unsafe_allow_html=True)
st.caption(f"Current CT: {now_ct.strftime('%Y-%m-%d %H:%M')}  •  showing entries for: **{plan_time.strftime('%H:%M')}**")

st.markdown('<div class="plan-grid">', unsafe_allow_html=True)
for a in st.session_state.anchors:
    b = blocks_between(a["ts"], plan_time, CFG.maint_start, CFG.maint_end)
    desc = a["price"] + a["slope_down"] * b
    asc = a["price"] + a["slope_up"] * b
    card = f"""
    <div class="plan-card">
      <div class="plan-title">{a['label']} — {plan_time.strftime('%H:%M')}</div>
      <div class="plan-kpi">{desc:.2f}</div>
      <div class="kpi-sub">Entry (descending) • Exit mirror: {asc:.2f}</div>
      <hr class="sep"/>
      <div class="subtle">Blocks since anchor: {b}</div>
      <div class="subtle">Anchor @ {a['ts'].strftime('%Y-%m-%d %H:%M')} • H={a['price']:.2f}</div>
    </div>
    """
    st.markdown(card, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('**Projection Tables (RTH)**', unsafe_allow_html=True)

if not st.session_state.anchors:
    st.info("Add at least one anchor to generate tables.")
else:
    tabs = st.tabs([a["label"] for a in st.session_state.anchors])
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
                f"Download {a['label']} table",
                df_out.to_csv(index=False).encode("utf-8"),
                file_name=f"{a['label']}_{proj_ts.date()}_RTH.csv",
                mime="text/csv",
            )
st.markdown('</div>', unsafe_allow_html=True)

st.caption("Entries use descending line (−0.25/30m default). Exits use ascending line (+0.25/30m). Maintenance 16:00–17:00 excluded from block counts. Overnight anchors are supported.")
