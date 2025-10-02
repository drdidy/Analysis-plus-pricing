app.py — SPX Springboard Analytics (Streamlit)

--------------------------------------------------------------

Purpose: Trading analytics (NOT execution). Implements the user's

springboard-high anchored, down-sloping guide lines and

evaluates high-probability entry/exit advisories.



Key Concepts encoded from product spec:

- Instrument: SPX / index-level series (raw points)

- Timeframe: 30-minute bars; RTH = 08:30–15:00 America/Chicago (CT)

- EMA: 8-period on 30m closes (for anchor validation only)

- Anchors ("springboard highs") come from the PRIOR RTH day:

H = local high bar such that after H there are N (1..3) bearish bars

that each CLOSE ABOVE the 8-EMA (no need to touch EMA). Within the next

M (1..3) bars, price closes above H. Anchor = H.high at H.end_time.

- For each anchor H, project a down-sloping line into the NEXT RTH day

with slope = −0.25 points per 30-min block (configurable).

- Long advisory (next day): if a BEARISH bar’s wick touches the line and

the bar CLOSES ABOVE the line → "armed-long"; next bar open → "triggered-long".

If the touching bar is bullish, ignore for longs.

- Short advisory (ONLY if overnight traded below ALL lines): a BULLISH bar

that touches the line and CLOSES BELOW → "armed-short"; next bar open →

"triggered-short". If that bullish touch closes above → invalid for short.

- Lines may be reused within the day. Optionally re-arm after K bars.

- Maintenance block should be ignored (we treat it as excluded from counts).



Data Sources (enterprise-ready options):

1) CSV Upload (recommended): two files — PRIOR RTH (for anchor scan)

and PROJECTED DAY (incl. overnight, for signal evaluation). Schema:

datetime, open, high, low, close, volume. datetime must be in ISO8601,

ideally tz-aware in America/Chicago; otherwise we interpret as CT.

2) Folder of Parquet/CSV with DuckDB connector (optional toggle below).

3) Placeholder adapter for external market data APIs (Polygon, Nasdaq,

Tiingo, etc.) — provide API keys via env vars and implement fetchers.



Tech Stack:

- streamlit, pandas, numpy, plotly, pytz, pydantic (for config validation)



Security/Enterprise Notes:

- No broker/execution code.

- All computations are client-initiated; no background tasks.

- Input validation and schema checks are included.

- Timezone handling standardized to America/Chicago.

--------------------------------------------------------------

from future import annotations import os from dataclasses import dataclass from typing import List, Optional, Tuple, Dict

import numpy as np import pandas as pd import pytz import streamlit as st import plotly.graph_objects as go from plotly.subplots import make_subplots

CT = pytz.timezone("America/Chicago")

----------------------- Utilities & Config -----------------------

def parse_dt(s: pd.Series) -> pd.Series: """Parse datetime strings/objects to tz-aware America/Chicago pandas Timestamps.""" dt = pd.to_datetime(s, errors="coerce", utc=True) # If "s" had no tz info, dt is assumed UTC; convert to CT dt = dt.dt.tz_convert(CT) return dt

@dataclass class AppConfig: ema_len: int = 8 n_min: int = 1 n_max: int = 3 m_min: int = 1 m_max: int = 3 slope_per_block: float = -0.25  # points per 30-min block rth_start: str = "08:30" rth_end: str = "15:00" maintenance_start: str = "16:00"  # ignored in projections/counts maintenance_end: str = "17:00" touch_tolerance: float = 0.5 reuse_rearm_after_bars: int = 2 allow_reuse: bool = True short_requires_below_all_overnight: bool = True

CFG = AppConfig()

----------------------- Data Adapters -----------------------

REQUIRED_COLS = ["datetime", "open", "high", "low", "close"]

@st.cache_data(show_spinner=False) def load_csv(file) -> pd.DataFrame: df = pd.read_csv(file) missing = [c for c in REQUIRED_COLS if c not in df.columns] if missing: raise ValueError(f"CSV missing columns: {missing}") df = df.copy() df["datetime"] = parse_dt(df["datetime"])  # to CT df = df.sort_values("datetime").reset_index(drop=True) # enforce 30-min cadence check (soft) return df

Optional: DuckDB/parquet adapter skeleton (enterprise extension point)

try: import duckdb  # type: ignore DUCKDB_AVAILABLE = True except Exception: DUCKDB_AVAILABLE = False

@st.cache_data(show_spinner=False) def load_from_duckdb(db_path: str, table: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame: if not DUCKDB_AVAILABLE: raise RuntimeError("duckdb not installed") con = duckdb.connect(db_path, read_only=True) q = f""" SELECT datetime, open, high, low, close, volume FROM {table} WHERE datetime >= ? AND datetime < ? ORDER BY datetime """ df = con.execute(q, [start.tz_convert("UTC").to_pydatetime(), end.tz_convert("UTC").to_pydatetime()]).df() df["datetime"] = parse_dt(df["datetime"])  # to CT return df

----------------------- Core Finance Helpers -----------------------

def ema(series: pd.Series, length: int) -> pd.Series: return series.ewm(span=length, adjust=False).mean()

@dataclass class Anchor: label: str time: pd.Timestamp price: float  # H.high n_used: int m_used: int confirm_time: pd.Timestamp

@dataclass class GuideLine: anchor_label: str anchor_time: pd.Timestamp anchor_price: float slope_per_block: float  # points per 30m block

----------------------- Time Logic -----------------------

def rth_mask_index(dt_idx: pd.DatetimeIndex, start: str, end: str) -> pd.Series: """Return boolean mask for RTH within America/Chicago hours [start, end).""" local = dt_idx.tz_convert(CT) start_h, start_m = map(int, start.split(":")) end_h, end_m = map(int, end.split(":")) times = local.time return ((local.hour > start_h) | ((local.hour == start_h) & (local.minute >= start_m))) & 
((local.hour < end_h) | ((local.hour == end_h) & (local.minute < end_m)))

def maintenance_mask_index(dt_idx: pd.DatetimeIndex, start: str, end: str) -> pd.Series: local = dt_idx.tz_convert(CT) s_h, s_m = map(int, start.split(":")) e_h, e_m = map(int, end.split(":")) return ((local.hour > s_h) | ((local.hour == s_h) & (local.minute >= s_m))) & 
((local.hour < e_h) | ((local.hour == e_h) & (local.minute < e_m)))

def generate_rth_slots(day: pd.Timestamp, start: str, end: str) -> pd.DatetimeIndex: """Generate 30-min bar end-times within RTH for a given day (CT).""" day_ct = day.tz_localize(CT).normalize() start_h, start_m = map(int, start.split(":")) end_h, end_m = map(int, end.split(":")) t0 = day_ct + pd.Timedelta(hours=start_h, minutes=start_m) t1 = day_ct + pd.Timedelta(hours=end_h, minutes=end_m) # 30-min bars: include [t0, t1) ends at t0+30m ... t1-30m slots = pd.date_range(t0, t1, freq="30min", inclusive="left", tz=CT) return slots

Count 30-min blocks between two timestamps, excluding the daily maintenance window.

We assume uniform 30-min steps; we exclude any blocks whose midpoint lies within maintenance.

def count_blocks_ex_maintenance(start_ts: pd.Timestamp, end_ts: pd.Timestamp, maint_start: str, maint_end: str) -> int: if end_ts <= start_ts: return 0 # Build half-hour grid from start to end (left-open on start) # Align to 30-min boundaries def align_up(ts: pd.Timestamp) -> pd.Timestamp: minute = (ts.minute // 30 + (1 if ts.minute % 30 else 0)) * 30 hour = ts.hour + (minute // 60) minute = minute % 60 aligned = ts.replace(minute=0, second=0, microsecond=0) + pd.Timedelta(hours=hour - ts.hour, minutes=minute - ts.minute) if ts.tzinfo is None: aligned = aligned.tz_localize(CT) return aligned

cur = start_ts.tz_convert(CT)
cur = align_up(cur)
end_ct = end_ts.tz_convert(CT)

s_h, s_m = map(int, maint_start.split(":"))
e_h, e_m = map(int, maint_end.split(":"))

blocks = 0
while cur < end_ct:
    mid = cur + pd.Timedelta(minutes=15)
    # exclude block if mid in maintenance window (local day of 'mid')
    in_maint = ((mid.hour > s_h) or (mid.hour == s_h and mid.minute >= s_m)) and \
               ((mid.hour < e_h) or (mid.hour == e_h and mid.minute < e_m))
    if not in_maint:
        blocks += 1
    cur += pd.Timedelta(minutes=30)
return blocks

----------------------- Anchor Detection -----------------------

def detect_anchors(prior_rth: pd.DataFrame, cfg: AppConfig) -> List[Anchor]: df = prior_rth.copy() df["ema8"] = ema(df["close"], cfg.ema_len)

anchors: List[Anchor] = []

# Local high detection: bar i is local high if its high >= highs of neighbors.
# We use a strict left/right neighbor check (window=3). Enterprise users can swap a swing algo.
for i in range(1, len(df) - 1):
    if not (df.loc[i, "high"] >= df.loc[i - 1, "high"] and df.loc[i, "high"] >= df.loc[i + 1, "high"]):
        continue
    H_idx = i
    H_time = df.loc[H_idx, "datetime"]
    H_price = float(df.loc[H_idx, "high"])

    # Try all N in [n_min, n_max]
    for N in range(cfg.n_min, cfg.n_max + 1):
        # Ensure we have N subsequent bars
        if H_idx + N >= len(df):
            break
        bars_N = df.iloc[H_idx + 1: H_idx + 1 + N]
        # Condition: bearish bars and close above EMA
        ok_N = np.all((bars_N["close"] < bars_N["open"]) & (bars_N["close"] > bars_N["ema8"]))
        if not ok_N:
            continue
        # Within next M bars, a close above H
        for M in range(cfg.m_min, cfg.m_max + 1):
            end_idx = H_idx + 1 + N + M - 1
            if end_idx >= len(df):
                continue
            window_M = df.iloc[H_idx + 1 + N: H_idx + 1 + N + M]
            if np.any(window_M["close"] > H_price):
                label = f"A{len(anchors) + 1}"
                confirm_time = window_M.loc[window_M["close"] > H_price, "datetime"].iloc[0]
                anchors.append(Anchor(label=label, time=H_time, price=H_price, n_used=N, m_used=M, confirm_time=confirm_time))
                # Avoid duplicating the same H across different (N,M) that are subsets; break after first success
                break
        else:
            continue
        break

return anchors

----------------------- Projection & Signals -----------------------

def project_line_value(anchor: Anchor | GuideLine, t: pd.Timestamp, cfg: AppConfig) -> float: """Compute L(t) = H - slope * blocks_between(anchor_time_end, t), excluding maintenance blocks.""" # Anchor bar is assumed to end at anchor.time (bar timestamp convention: bar end time) blocks = count_blocks_ex_maintenance(anchor.anchor_time if isinstance(anchor, GuideLine) else anchor.time, t, cfg.maintenance_start, cfg.maintenance_end) slope = cfg.slope_per_block if not isinstance(anchor, GuideLine) else anchor.slope_per_block return float((anchor.anchor_price if isinstance(anchor, GuideLine) else anchor.price) + slope * blocks)

@dataclass class ProjectionRow: time: pd.Timestamp L: float o: float h: float l: float c: float touch: str  # 'wick' | 'body' | 'no' close_rel: str  # 'above' | 'below' | 'equal' signal_state: str  # idle|armed-long|triggered-long|armed-short|triggered-short note: str = ""

def evaluate_signals_for_line(line: GuideLine, proj_day_bars: pd.DataFrame, overnight_bars: Optional[pd.DataFrame], cfg: AppConfig, below_all_overnight_flag: bool) -> List[ProjectionRow]: rows: List[ProjectionRow] = []

# We process each 30-min bar of projected RTH in chronological order.
armed_long = False
armed_short = False
rearm_countdown_long = 0
rearm_countdown_short = 0

for _, bar in proj_day_bars.iterrows():
    t = bar["datetime"]
    L = project_line_value(GuideLine(line.anchor_label, line.anchor_time, line.anchor_price, line.slope_per_block), t, cfg)
    o, h, l, c = map(float, (bar["open"], bar["high"], bar["low"], bar["close"]))

    # Determine touch type
    touch = "no"
    if (l - cfg.touch_tolerance) <= L <= (h + cfg.touch_tolerance):
        # if body contains L
        body_low, body_high = (min(o, c), max(o, c))
        if body_low - cfg.touch_tolerance <= L <= body_high + cfg.touch_tolerance:
            touch = "body"
        else:
            touch = "wick"

    # Close relation
    if c > L:
        close_rel = "above"
    elif c < L:
        close_rel = "below"
    else:
        close_rel = "equal"

    state = "idle"
    note = ""

    # Long arming rule: bar must be BEARISH, touch (wick/body), and close ABOVE L. If bar bullish → ignore.
    is_bearish = c < o
    is_bullish = c > o

    if cfg.allow_reuse:
        if rearm_countdown_long > 0:
            rearm_countdown_long -= 1
            if rearm_countdown_long == 0:
                armed_long = False
        if rearm_countdown_short > 0:
            rearm_countdown_short -= 1
            if rearm_countdown_short == 0:
                armed_short = False

    # Evaluate arming
    if is_bearish and touch != "no" and close_rel == "above":
        armed_long = True
        rearm_countdown_long = cfg.reuse_rearm_after_bars
        state = "armed-long"
        note = "Bearish touch + close above"
    # Short arming rule (only if below-all-overnight is true)
    elif cfg.short_requires_below_all_overnight and below_all_overnight_flag and is_bullish and touch != "no" and close_rel == "below":
        armed_short = True
        rearm_countdown_short = cfg.reuse_rearm_after_bars
        state = "armed-short"
        note = "Bullish touch + close below (below-all ON)"
    else:
        # Triggering occurs at NEXT bar open; we cannot mark it now. We'll mark triggered on the next iteration.
        state = "idle"

    rows.append(ProjectionRow(time=t, L=L, o=o, h=h, l=l, c=c, touch=touch, close_rel=close_rel, signal_state=state, note=note))

# Mark triggers at next bar open after an armed bar.
# We scan rows list and update the NEXT row's state accordingly.
for i in range(len(rows) - 1):
    cur = rows[i]
    nxt = rows[i + 1]
    if cur.signal_state == "armed-long":
        nxt.signal_state = "triggered-long"
        if nxt.note:
            nxt.note += "; "
        nxt.note += f"Enter long at next open ~{nxt.o:.2f}; stop < {cur.l - 0.8:.2f}"
    elif cur.signal_state == "armed-short":
        nxt.signal_state = "triggered-short"
        if nxt.note:
            nxt.note += "; "
        nxt.note += f"Enter short at next open ~{nxt.o:.2f}; stop > {cur.h + 0.8:.2f}"

return rows

def check_below_all_overnight(lines: List[GuideLine], overnight_bars: Optional[pd.DataFrame], cfg: AppConfig) -> bool: """Return True if overnight price traded below ALL lines (any time overnight).""" if overnight_bars is None or overnight_bars.empty or not lines: return False # For each overnight bar, compute each line's L(t); if bar.low < min(Ls) at that time for every line, flag True. for _, bar in overnight_bars.iterrows(): t = bar["datetime"] Ls = [project_line_value(GuideLine(gl.anchor_label, gl.anchor_time, gl.anchor_price, gl.slope_per_block), t, cfg) for gl in lines] if float(bar["low"]) < min(Ls): return True return False

----------------------- Streamlit UI -----------------------

st.set_page_config(page_title="SPX Springboard Analytics", layout="wide")

st.title("SPX Springboard Analytics — 30m, 8EMA, Sloped Lines")

with st.sidebar: st.subheader("Controls") ema_len = st.number_input("EMA length", min_value=2, max_value=100, value=CFG.ema_len) n_min, n_max = st.slider("N bearish bars (min..max)", 1, 5, (CFG.n_min, CFG.n_max)) m_min, m_max = st.slider("M bars to close > H (min..max)", 1, 5, (CFG.m_min, CFG.m_max)) slope_per_block = st.number_input("Slope per 30m (points)", value=CFG.slope_per_block, step=0.05, format="%.2f") touch_tol = st.number_input("Touch tolerance (pts)", value=CFG.touch_tolerance, step=0.1, format="%.1f") allow_reuse = st.toggle("Allow re-use / re-arm lines", value=CFG.allow_reuse) rearm_after = st.number_input("Re-arm after K bars", min_value=1, max_value=10, value=CFG.reuse_rearm_after_bars) short_requires_below_all = st.toggle("Enable shorts only if overnight fell below ALL lines", value=CFG.short_requires_below_all_overnight)

st.markdown("---")
st.caption("RTH window is fixed to 08:30–15:00 CT. Maintenance (16:00–17:00) excluded from block counts.")

Data Inputs

col1, col2 = st.columns(2) with col1: st.subheader("Prior RTH (for anchor scan)") prior_file = st.file_uploader("Upload CSV for PRIOR RTH (30m bars)", type=["csv"], key="prior") prior_df = None if prior_file is not None: try: prior_df = load_csv(prior_file) except Exception as e: st.error(f"Failed to load prior RTH CSV: {e}")

with col2: st.subheader("Projected Day (incl. overnight)") proj_file = st.file_uploader("Upload CSV for PROJECTED DAY (30m bars, include overnight up to 15:00 CT)", type=["csv"], key="proj") proj_df = None if proj_file is not None: try: proj_df = load_csv(proj_file) except Exception as e: st.error(f"Failed to load projected day CSV: {e}")

Validate we have both datasets

if prior_df is None or proj_df is None: st.info("Upload both CSVs to proceed. Required columns: datetime, open, high, low, close, (volume optional). Timezone will be interpreted as America/Chicago.") st.stop()

Filter frames for RTH boundaries

PRIOR: We only need its RTH (08:30–15:00)

mask_prior_rth = rth_mask_index(prior_df["datetime"], CFG.rth_start, CFG.rth_end) prior_rth = prior_df.loc[mask_prior_rth].copy().reset_index(drop=True)

PROJECTED DAY: build overnight subset (prev 15:00 → current 08:30) and proj RTH subset (08:30–15:00)

proj_day = proj_df.copy() proj_day["date_ct"] = proj_day["datetime"].dt.tz_convert(CT).dt.date

infer projected RTH date as the most frequent date appearing between 08:30–15:00

mask_proj_rth = rth_mask_index(proj_day["datetime"], CFG.rth_start, CFG.rth_end) proj_rth = proj_day.loc[mask_proj_rth].copy().reset_index(drop=True) if proj_rth.empty: st.error("Projected day CSV contains no bars within 08:30–15:00 CT.") st.stop()

proj_date = proj_rth["datetime"].dt.tz_convert(CT).dt.date.iloc[0]

Overnight bars = those from previous calendar day 15:00 (inclusive) to this day 08:30 (exclusive)

prev_day = pd.Timestamp(proj_date, tz=CT) - pd.Timedelta(days=1) overnight_start = prev_day + pd.Timedelta(hours=15) overnight_end = pd.Timestamp(proj_date, tz=CT) + pd.Timedelta(hours=8, minutes=30) overnight_mask = (proj_day["datetime"] >= overnight_start) & (proj_day["datetime"] < overnight_end) overnight_bars = proj_day.loc[overnight_mask].copy().reset_index(drop=True)

----------------------- Anchor Detection View -----------------------

CFG.ema_len = int(ema_len) CFG.n_min, CFG.n_max = int(n_min), int(n_max) CFG.m_min, CFG.m_max = int(m_min), int(m_max) CFG.slope_per_block = float(slope_per_block) CFG.touch_tolerance = float(touch_tol) CFG.allow_reuse = bool(allow_reuse) CFG.reuse_rearm_after_bars = int(rearm_after) CFG.short_requires_below_all_overnight = bool(short_requires_below_all)

st.subheader("Anchors — detected from PRIOR RTH") anchors = detect_anchors(prior_rth, CFG) if not anchors: st.warning("No anchors detected under current N/M rules.") else: # Table of anchors anc_df = pd.DataFrame([{ "Label": a.label, "Time": a.time, "High(H)": a.price, "N": a.n_used, "M": a.m_used, "Confirm": a.confirm_time } for a in anchors]) st.dataframe(anc_df, use_container_width=True)

Anchor selection

selected_labels = st.multiselect("Select anchors to project", [a.label for a in anchors], default=[a.label for a in anchors]) selected_anchors = [a for a in anchors if a.label in selected_labels]

if not selected_anchors: st.info("Select at least one anchor to project.") st.stop()

Build GuideLines and compute overnight flag

guide_lines: List[GuideLine] = [GuideLine(anchor_label=a.label, anchor_time=a.time, anchor_price=a.price, slope_per_block=CFG.slope_per_block) for a in selected_anchors]

below_all_flag = check_below_all_overnight(guide_lines, overnight_bars, CFG) if CFG.short_requires_below_all_overnight: st.caption(f"Short logic below-all-lines overnight flag: {below_all_flag}")

----------------------- Projection Tables & Signals -----------------------

st.subheader("Projection & Signals — per selected anchor (Projected RTH)")

For plotting, collect all rows per line

plot_series: Dict[str, List[ProjectionRow]] = {}

Build per-line tabs

tabs = st.tabs([gl.anchor_label for gl in guide_lines]) for tab, gl in zip(tabs, guide_lines): with tab: # Extract only RTH bars for projected day gl_proj = proj_rth.copy() # Evaluate rows & signals rows = evaluate_signals_for_line(gl, gl_proj, overnight_bars, CFG, below_all_flag) plot_series[gl.anchor_label] = rows

# Show table
    rows_df = pd.DataFrame([{ 
        "Time": r.time, "Line L": round(r.L, 2), "Open": r.o, "High": r.h, "Low": r.l, "Close": r.c,
        "Touch": r.touch, "Close vs L": r.close_rel, "Signal": r.signal_state, "Note": r.note
    } for r in rows])
    st.dataframe(rows_df, use_container_width=True)

    # Export CSV
    st.download_button(
        label=f"Download {gl.anchor_label} Projections CSV",
        data=rows_df.to_csv(index=False).encode("utf-8"),
        file_name=f"projections_{gl.anchor_label}.csv",
        mime="text/csv",
    )

----------------------- Chart -----------------------

st.subheader("Chart — Projected RTH with Lines & Signals") fig = go.Figure()

Candles

fig.add_trace(go.Candlestick( x=proj_rth["datetime"], open=proj_rth["open"], high=proj_rth["high"], low=proj_rth["low"], close=proj_rth["close"], name="30m" ))

8-EMA on projected RTH (for context only)

proj_rth = proj_rth.copy() proj_rth["ema8"] = ema(proj_rth["close"], CFG.ema_len) fig.add_trace(go.Scatter(x=proj_rth["datetime"], y=proj_rth["ema8"], mode="lines", name="EMA8"))

Lines

for gl in guide_lines: xs = [] ys = [] labels_times = [] for _, bar in proj_rth.iterrows(): t = bar["datetime"] L = project_line_value(gl, t, CFG) xs.append(t) ys.append(L) labels_times.append(t) fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=f"Line {gl.anchor_label}"))

Mark armed/triggered states

for label, rows in plot_series.items(): for r in rows: if r.signal_state in ("armed-long", "armed-short", "triggered-long", "triggered-short"): marker_symbol = { "armed-long": "triangle-up", "triggered-long": "star", "armed-short": "triangle-down", "triggered-short": "x" }[r.signal_state] fig.add_trace(go.Scatter(x=[r.time], y=[r.c], mode="markers", marker_symbol=marker_symbol, marker_size=10, name=f"{label} {r.signal_state}", showlegend=False))

fig.update_layout(height=640, xaxis_rangeslider_visible=False) st.plotly_chart(fig, use_container_width=True)

----------------------- Session Summary -----------------------

st.subheader("Session Summary") summary_rows = [] for label, rows in plot_series.items(): touches = sum(1 for r in rows if r.touch != "no") armed_l = sum(1 for r in rows if r.signal_state == "armed-long") trig_l = sum(1 for r in rows if r.signal_state == "triggered-long") armed_s = sum(1 for r in rows if r.signal_state == "armed-short") trig_s = sum(1 for r in rows if r.signal_state == "triggered-short") mfe = 0.0 mae = 0.0 # Simple MFE/MAE approximation per line (optional) if rows: closes = np.array([r.c for r in rows]) mfe = float(np.max(closes) - closes[0]) mae = float(np.min(closes) - closes[0]) summary_rows.append({ "Line": label, "Touches": touches, "Armed Long": armed_l, "Triggered Long": trig_l, "Armed Short": armed_s, "Triggered Short": trig_s, "MFE (to close)": round(mfe, 2), "MAE (to close)": round(mae, 2) })

st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

----------------------- Footer -----------------------

st.caption( "This app provides analytics and decision support only. It does not execute trades. " "Ensure your data timestamps are 30-minute bar end-times in America/Chicago." )

