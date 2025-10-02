from __future__ import annotations
import numpy as np
import pandas as pd
import pytz
import streamlit as st
import plotly.graph_objects as go
from dataclasses import dataclass
from typing import List, Dict

CT = pytz.timezone("America/Chicago")
REQ_COLS = ["datetime", "open", "high", "low", "close"]

def parse_dt_col(s: pd.Series) -> pd.Series:
    dt = pd.to_datetime(s, errors="coerce", utc=True)
    return dt.dt.tz_convert(CT)

@st.cache_data(show_spinner=False)
def load_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    missing = [c for c in REQ_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    df = df.copy()
    df["datetime"] = parse_dt_col(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)
    return df

def rth_mask(dt: pd.Series, start="08:30", end="15:00") -> pd.Series:
    idx = dt.dt.tz_convert(CT)
    sh, sm = map(int, start.split(":"))
    eh, em = map(int, end.split(":"))
    after = (idx.dt.hour > sh) | ((idx.dt.hour == sh) & (idx.dt.minute >= sm))
    before = (idx.dt.hour < eh) | ((idx.dt.hour == eh) & (idx.dt.minute < em))
    return after & before

def blocks_between(start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> int:
    if end_ts <= start_ts:
        return 0
    s = start_ts.tz_convert(CT).ceil("30min")
    e = end_ts.tz_convert(CT)
    rng = pd.date_range(s, e, freq="30min", inclusive="left", tz=CT)
    mask = ~(((rng.hour == 16) & (rng.minute == 0)) | ((rng.hour == 16) & (rng.minute == 30)))
    return int(mask.sum())

def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()

@dataclass
class AppCfg:
    ema_len: int = 8
    n_min: int = 1
    n_max: int = 3
    m_min: int = 1
    m_max: int = 3
    slope_per_block: float = -0.25
    touch_tolerance: float = 0.5
    rearm_after: int = 2
    allow_reuse: bool = True
    short_requires_below_all: bool = True

CFG = AppCfg()

@dataclass
class Anchor:
    label: str
    time: pd.Timestamp
    price: float
    n_used: int
    m_used: int
    confirm_time: pd.Timestamp

@dataclass
class GuideLine:
    anchor_label: str
    anchor_time: pd.Timestamp
    anchor_price: float
    slope_per_block: float

@dataclass
class ProjectionRow:
    time: pd.Timestamp
    L: float
    o: float
    h: float
    l: float
    c: float
    touch: str
    close_rel: str
    signal: str
    note: str = ""

def detect_anchors(prior_rth: pd.DataFrame, cfg: AppCfg) -> List[Anchor]:
    df = prior_rth.copy()
    df["ema8"] = ema(df["close"], cfg.ema_len)
    anchors: List[Anchor] = []
    for i in range(1, len(df) - 1):
        if not (df.loc[i, "high"] >= df.loc[i - 1, "high"] and df.loc[i, "high"] >= df.loc[i + 1, "high"]):
            continue
        H_i = i
        H_time = df.loc[H_i, "datetime"]
        H_price = float(df.loc[H_i, "high"])
        for N in range(cfg.n_min, cfg.n_max + 1):
            if H_i + N >= len(df):
                break
            segN = df.iloc[H_i + 1: H_i + 1 + N]
            okN = np.all((segN["close"] < segN["open"]) & (segN["close"] > segN["ema8"]))
            if not okN:
                continue
            for M in range(cfg.m_min, cfg.m_max + 1):
                end_i = H_i + 1 + N + M - 1
                if end_i >= len(df):
                    continue
                segM = df.iloc[H_i + 1 + N: H_i + 1 + N + M]
                if np.any(segM["close"] > H_price):
                    confirm_time = segM.loc[segM["close"] > H_price, "datetime"].iloc[0]
                    anchors.append(Anchor(
                        label=f"A{len(anchors) + 1}",
                        time=H_time,
                        price=H_price,
                        n_used=N,
                        m_used=M,
                        confirm_time=confirm_time
                    ))
                    break
            else:
                continue
            break
    return anchors

def line_value(gl: GuideLine, t: pd.Timestamp, cfg: AppCfg) -> float:
    blocks = blocks_between(gl.anchor_time, t)
    return gl.anchor_price + cfg.slope_per_block * blocks

def evaluate_line(gl: GuideLine, rth_bars: pd.DataFrame, below_all_flag: bool, cfg: AppCfg) -> List[ProjectionRow]:
    rows: List[ProjectionRow] = []
    for _, bar in rth_bars.iterrows():
        t = bar["datetime"]
        L = line_value(gl, t, cfg)
        o, h, l, c = map(float, (bar["open"], bar["high"], bar["low"], bar["close"]))
        touch = "no"
        if (l - cfg.touch_tolerance) <= L <= (h + cfg.touch_tolerance):
            body_low, body_high = (min(o, c), max(o, c))
            touch = "body" if (body_low - cfg.touch_tolerance) <= L <= (body_high + cfg.touch_tolerance) else "wick"
        close_rel = "above" if c > L else ("below" if c < L else "equal")
        state = "idle"
        note = ""
        is_bearish = c < o
        is_bullish = c > o
        if is_bearish and touch != "no" and close_rel == "above":
            state = "armed-long"
            note = "Bearish touch & close > line"
        elif cfg.short_requires_below_all and below_all_flag and is_bullish and touch != "no" and close_rel == "below":
            state = "armed-short"
            note = "Bullish touch & close < line"
        rows.append(ProjectionRow(t, L, o, h, l, c, touch, close_rel, state, note))
    for i in range(len(rows) - 1):
        cur, nxt = rows[i], rows[i + 1]
        if cur.signal == "armed-long":
            nxt.signal = "triggered-long"
            nxt.note = (nxt.note + "; " if nxt.note else "") + f"LONG trigger ~{nxt.o:.2f}; stop < {cur.l - 0.8:.2f}"
        elif cur.signal == "armed-short":
            nxt.signal = "triggered-short"
            nxt.note = (nxt.note + "; " if nxt.note else "") + f"SHORT trigger ~{nxt.o:.2f}; stop > {cur.h + 0.8:.2f}"
    return rows

def overnight_below_all(lines: List[GuideLine], overnight: pd.DataFrame, cfg: AppCfg) -> bool:
    if overnight is None or overnight.empty or not lines:
        return False
    for _, bar in overnight.iterrows():
        t = bar["datetime"]
        Ls = [line_value(gl, t, cfg) for gl in lines]
        if float(bar["low"]) < min(Ls):
            return True
    return False

st.set_page_config(page_title="SPX Springboard Analytics", layout="wide")
st.title("SPX Springboard Analytics")

with st.sidebar:
    st.subheader("Controls")
    CFG.ema_len = st.number_input("EMA length", 2, 100, value=CFG.ema_len)
    CFG.n_min, CFG.n_max = st.slider("N bearish bars (range)", 1, 5, (CFG.n_min, CFG.n_max))
    CFG.m_min, CFG.m_max = st.slider("M bars to close > H (range)", 1, 5, (CFG.m_min, CFG.m_max))
    CFG.slope_per_block = st.number_input("Slope per 30m (pts)", value=CFG.slope_per_block, step=0.05, format="%.2f")
    CFG.touch_tolerance = st.number_input("Touch tolerance (pts)", value=CFG.touch_tolerance, step=0.1)
    CFG.allow_reuse = st.toggle("Allow re-use", value=CFG.allow_reuse)
    CFG.rearm_after = st.number_input("Re-arm after K bars", 1, 10, value=CFG.rearm_after)
    CFG.short_requires_below_all = st.toggle("Shorts only if overnight below all lines", value=CFG.short_requires_below_all)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Upload PRIOR RTH")
    f_prior = st.file_uploader("CSV for PRIOR RTH", type=["csv"], key="prior")
with col2:
    st.subheader("Upload PROJECTED DAY")
    f_proj = st.file_uploader("CSV for PROJECTED DAY", type=["csv"], key="proj")

if not f_prior or not f_proj:
    st.stop()

prior_all = load_csv(f_prior)
proj_all = load_csv(f_proj)
prior_rth = prior_all.loc[rth_mask(prior_all["datetime"])].copy().reset_index(drop=True)
proj_rth = proj_all.loc[rth_mask(proj_all["datetime"])].copy().reset_index(drop=True)
proj_date = proj_rth.loc[0, "datetime"].astimezone(CT).date()
prev_day = pd.Timestamp(proj_date, tz=CT) - pd.Timedelta(days=1)
over_start = prev_day + pd.Timedelta(hours=15)
over_end = pd.Timestamp(proj_date, tz=CT) + pd.Timedelta(hours=8, minutes=30)
over_mask = (proj_all["datetime"] >= over_start) & (proj_all["datetime"] < over_end)
overnight = proj_all.loc[over_mask].copy().reset_index(drop=True)

anchors = detect_anchors(prior_rth, CFG)
if not anchors:
    st.stop()
anc_df = pd.DataFrame([{ "Label": a.label, "Time": a.time, "High(H)": a.price, "N": a.n_used, "M": a.m_used, "Confirm": a.confirm_time } for a in anchors])
st.dataframe(anc_df, use_container_width=True)

sel = st.multiselect("Select anchors", [a.label for a in anchors], default=[a.label for a in anchors])
sel_anchors = [a for a in anchors if a.label in sel]
if not sel_anchors:
    st.stop()

gls: List[GuideLine] = [GuideLine(a.label, a.time, a.price, CFG.slope_per_block) for a in sel_anchors]
below_all_flag = overnight_below_all(gls, overnight, CFG)

tabs = st.tabs([g.anchor_label for g in gls])
plot_rows: Dict[str, List[ProjectionRow]] = {}

for tab, gl in zip(tabs, gls):
    with tab:
        rows = evaluate_line(gl, proj_rth, below_all_flag, CFG)
        plot_rows[gl.anchor_label] = rows
        df_rows = pd.DataFrame([
            {"Time": r.time, "Line L": round(r.L, 2), "Open": r.o, "High": r.h, "Low": r.l, "Close": r.c,
             "Touch": r.touch, "Close vs L": r.close_rel, "Signal": r.signal, "Note": r.note}
            for r in rows
        ])
        st.dataframe(df_rows, use_container_width=True)
        st.download_button(
            f"Download {gl.anchor_label} projections",
            df_rows.to_csv(index=False).encode("utf-8"),
            file_name=f"projections_{gl.anchor_label}.csv",
            mime="text/csv",
        )

st.subheader("Chart")
fig = go.Figure()
fig.add_candlestick(
    x=proj_rth["datetime"],
    open=proj_rth["open"], high=proj_rth["high"], low=proj_rth["low"], close=proj_rth["close"],
    name="30m"
)
proj_rth = proj_rth.copy()
proj_rth["ema8"] = ema(proj_rth["close"], CFG.ema_len)
fig.add_scatter(x=proj_rth["datetime"], y=proj_rth["ema8"], mode="lines", name="EMA8")
for gl in gls:
    xs, ys = [], []
    for t in proj_rth["datetime"]:
        xs.append(t)
        ys.append(line_value(gl, t, CFG))
    fig.add_scatter(x=xs, y=ys, mode="lines", name=f"Line {gl.anchor_label}")
for label, rows in plot_rows.items():
    for r in rows:
        if r.signal in ("armed-long", "triggered-long", "armed-short", "triggered-short"):
            symbol = {
                "armed-long": "triangle-up",
                "triggered-long": "star",
                "armed-short": "triangle-down",
                "triggered-short": "x"
            }[r.signal]
            fig.add_scatter(x=[r.time], y=[r.c], mode="markers", marker_symbol=symbol, marker_size=10, name=f"{label} {r.signal}")
fig.update_layout(height=700, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
