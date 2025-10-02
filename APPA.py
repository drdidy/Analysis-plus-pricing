from __future__ import annotations
import numpy as np
import pandas as pd
import pytz
import streamlit as st
from dataclasses import dataclass
from typing import List, Dict, Optional

CT = pytz.timezone("America/Chicago")

st.set_page_config(page_title="Springboard Tables", layout="wide")
st.title("Springboard Tables — Manual Anchors → Projected RTH")

@dataclass
class AppCfg:
    slope_down: float = -0.25
    slope_up: float = 0.25
    rth_start: str = "08:30"
    rth_end: str = "15:00"
    maintenance_start: str = "16:00"
    maintenance_end: str = "17:00"
    yf_ticker: str = "^GSPC"
    yf_on: bool = False

CFG = AppCfg()

def to_ct(ts: pd.Timestamp) -> pd.Timestamp:
    if ts.tzinfo is None:
        ts = ts.tz_localize(CT)
    else:
        ts = ts.tz_convert(CT)
    return ts

def make_dt(date: pd.Timestamp, hm: str) -> pd.Timestamp:
    h, m = map(int, hm.split(":"))
    return to_ct(pd.Timestamp(year=date.year, month=date.month, day=date.day, hour=h, minute=m, tz=CT))

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

@st.cache_data(show_spinner=False)
def yf_fetch(ticker: str, day: pd.Timestamp) -> pd.DataFrame:
    try:
        import yfinance as yf
    except Exception:
        return pd.DataFrame()
    day = to_ct(pd.Timestamp(day.date(), tz=CT))
    prev = day - pd.Timedelta(days=2)
    nxt = day + pd.Timedelta(days=1)
    df = yf.download(ticker, interval="30m", start=prev.tz_convert("UTC").to_pydatetime(), end=nxt.tz_convert("UTC").to_pydatetime(), progress=False)
    if df.empty:
        return df
    df = df.rename(columns={"Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"})
    df["datetime"] = pd.to_datetime(df.index, utc=True).tz_convert(CT)
    df = df.sort_values("datetime").reset_index(drop=True)
    start_ct = day + pd.Timedelta(hours=8, minutes=30)
    end_ct = day + pd.Timedelta(hours=15, minutes=0)
    m = (df["datetime"] >= start_ct) & (df["datetime"] < end_ct)
    return df.loc[m, ["datetime","open","high","low","close","volume"]].reset_index(drop=True)

with st.sidebar:
    st.subheader("Settings")
    proj_date = st.date_input("Projected RTH date (CT)", value=pd.Timestamp.today(tz=CT).date())
    prior_date = st.date_input("Anchor day (CT, prior RTH)", value=(pd.Timestamp(proj_date) - pd.Timedelta(days=1)).date())
    CFG.slope_down = st.number_input("Slope per 30m (descending)", value=CFG.slope_down, step=0.05, format="%.2f")
    CFG.slope_up = st.number_input("Slope per 30m (ascending)", value=CFG.slope_up, step=0.05, format="%.2f")
    CFG.yf_on = st.toggle("Attach Yahoo Finance O/H/L/C to tables", value=False)
    CFG.yf_ticker = st.text_input("Yahoo Finance ticker (if ON)", value=CFG.yf_ticker)

st.markdown("#### Anchors (manual) — add/edit rows")
sample = pd.DataFrame([
    {"label":"A1","time_hhmm":"10:30","price":6721.80},
    {"label":"A2","time_hhmm":"12:00","price":6732.40},
])
data = st.data_editor(sample, num_rows="dynamic", use_container_width=True, key="anchors_editor")

data = data.dropna(subset=["label","time_hhmm","price"])
if data.empty:
    st.stop()

proj_day_ts = to_ct(pd.Timestamp(proj_date, tz=CT))
prior_day_ts = to_ct(pd.Timestamp(prior_date, tz=CT))
slots = rth_slots(proj_day_ts, CFG.rth_start, CFG.rth_end)

yf_df: Optional[pd.DataFrame] = None
if CFG.yf_on:
    with st.spinner("Fetching Yahoo Finance..."):
        yf_df = yf_fetch(CFG.yf_ticker, proj_day_ts)

tabs = st.tabs(list(data["label"]))
for tab_label in data["label"]:
    row = data.loc[data["label"] == tab_label].iloc[0]
    anchor_ts = make_dt(prior_day_ts, row["time_hhmm"])
    H = float(row["price"])
    rows = []
    for t in slots:
        b = blocks_between(anchor_ts, t, CFG.maintenance_start, CFG.maintenance_end)
        desc = H + CFG.slope_down * b
        asc = H + CFG.slope_up * b
        rec_entry = desc
        rec_exit = asc
        rec = {"Time": t, "Blocks": b, "Descending": round(desc, 2), "Ascending": round(asc, 2), "Entry(desc)": round(rec_entry, 2), "Exit(asc)": round(rec_exit, 2)}
        if CFG.yf_on and yf_df is not None and not yf_df.empty:
            m = yf_df["datetime"] == t
            if m.any():
                bar = yf_df.loc[m].iloc[0]
                rec.update({"Open": float(bar["open"]), "High": float(bar["high"]), "Low": float(bar["low"]), "Close": float(bar["close"])})
        rows.append(rec)
    out = pd.DataFrame(rows)
    with tabs[list(data["label"]).index(tab_label)]:
        st.markdown(f"**{tab_label}** — anchor {prior_date} {row['time_hhmm']} CT @ {H:.2f}")
        st.dataframe(out, use_container_width=True, hide_index=True)
        st.download_button(
            f"Download {tab_label} table",
            out.to_csv(index=False).encode("utf-8"),
            file_name=f"{tab_label}_{proj_date}_tables.csv",
            mime="text/csv",
        )

st.caption("Tables compute descending (entry) and ascending (exit) lines from each manual anchor across the projected RTH (08:30–15:00 CT). Maintenance 16:00–17:00 excluded from block counts.")
