import streamlit as st
from datetime import datetime, time, timedelta
import pandas as pd
import numpy as np
import math

# --- SLOPE SETTINGS ---
SLOPES = {
    "SPX_HIGH": -0.2792,
    "SPX_CLOSE": -0.2792,
    "SPX_LOW": -0.2792,
    "TSLA": -0.2583,
    "NVDA": -0.0871,
    "AAPL": -0.1775,
    "AMZN": -0.1714,
    "GOOGL": -0.2091,
}

# --- BLACK-SCHOLES via erf (no scipy) ---
def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def black_scholes_call(S, K, T, r, sigma):
    if T <= 0 or K <= 0 or S <= 0:
        return 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)

# --- TIME BLOCK & SLOPE HELPERS ---
def generate_time_blocks():
    base = datetime.strptime("08:30", "%H:%M")
    return [(base + timedelta(minutes=30 * i)).strftime("%H:%M") for i in range(13)]

def calculate_spx_blocks(a, t):
    dt, blocks = a, 0
    while dt < t:
        if dt.hour != 16:
            blocks += 1
        dt += timedelta(minutes=30)
    return blocks

def calculate_stock_blocks(a, t):
    prev_close = a.replace(hour=15, minute=0)
    bp = max(0, int((prev_close - a).total_seconds() // 1800))
    next_open  = datetime.combine(t.date(), time(8,30))
    next_close = datetime.combine(t.date(), time(15,0))
    bn = 0 if t <= next_open else int((min(t,next_close) - next_open).total_seconds() // 1800)
    return bp + bn

# --- FORECAST TABLE GENERATORS (only Entry Call columns) ---
def generate_spx(price, slope, anchor_dt, fd, r, vol):
    expiries = [0, 3, 7, 30]
    rows = []
    for slot in generate_time_blocks():
        h, m = map(int, slot.split(":"))
        tgt   = datetime.combine(fd, time(h, m))
        b     = calculate_spx_blocks(anchor_dt, tgt)
        entry = price + slope * b
        exit_ = price - slope * b

        K_e = int(round(entry / 10.0)) * 10

        row = {
            "Time": slot,
            "Entry Underlying": round(entry, 2),
            "Exit Underlying":  round(exit_, 2),
            "Strike Entry":     K_e,
        }

        for d in expiries:
            T = d / 252
            if K_e > 0 and entry > 0:
                c = black_scholes_call(entry, K_e, T, r, vol)
                row[f"Entry Call {d}d"] = round(c, 2)
            else:
                row[f"Entry Call {d}d"] = None

        rows.append(row)
    return pd.DataFrame(rows)

def generate_stock(price, slope, anchor_dt, fd, r, vol, invert=False):
    expiries = [0, 3, 7, 30]
    rows = []
    for slot in generate_time_blocks():
        h, m = map(int, slot.split(":"))
        tgt    = datetime.combine(fd, time(h, m))
        b      = calculate_stock_blocks(anchor_dt, tgt)
        entry  = (price - slope * b) if invert else (price + slope * b)
        exit_  = (price + slope * b) if invert else (price - slope * b)

        K_e = int(round(entry / 10.0)) * 10

        row = {
            "Time": slot,
            "Entry Underlying": round(entry, 2),
            "Exit Underlying":  round(exit_, 2),
            "Strike Entry":     K_e,
        }

        for d in expiries:
            T = d / 252
            if K_e > 0 and entry > 0:
                c = black_scholes_call(entry, K_e, T, r, vol)
                row[f"Entry Call {d}d"] = round(c, 2)
            else:
                row[f"Entry Call {d}d"] = None

        rows.append(row)
    return pd.DataFrame(rows)

# --- STREAMLIT SETUP ---
st.set_page_config(page_title="Dr Didy Forecast", page_icon="📈", layout="wide")

# --- GLOBAL CSS & CONTAINER WIDTH ---
st.markdown("""
<style>
.main-container {max-width:1200px; margin:0 auto; padding:0 1rem;}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 style='text-align:center;'>📊 Dr Didy Forecast</h1><hr>", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Settings")
    forecast_date = st.date_input("Forecast Date", datetime.now().date() + timedelta(days=1))

    st.subheader("Slopes")
    for k in SLOPES:
        SLOPES[k] = st.number_input(k.replace("_", " "), SLOPES[k], format="%.4f")

    st.divider()
    r = st.number_input("Risk-free Rate", value=0.01, format="%.3f")

    st.subheader("Volatilities (σ)")
    VOL = {}
    for sym in ["SPX", "TSLA", "NVDA", "AAPL", "AMZN", "GOOGL"]:
        VOL[sym] = st.slider(sym, 0.05, 1.0, 0.2, step=0.01)

# --- TABS ---
tabs = st.tabs(["🧭 SPX", "🚗 TSLA", "🧠 NVDA", "🍎 AAPL", "📦 AMZN", "🔍 GOOGL"])

# --- SPX TAB ---
with tabs[0]:
    st.subheader("🧭 SPX Forecast")
    c1, c2, c3 = st.columns(3)
    hp = c1.number_input("🔼 High Price", min_value=0.01, value=6185.8, format="%.2f", key="spx_hp")
    ht = c1.time_input("🕒 High Time", datetime(2025,1,1,11,30).time(), step=1800, key="spx_ht")
    cp = c2.number_input("⏹️ Close Price", min_value=0.01, value=6170.2, format="%.2f", key="spx_cp")
    ct = c2.time_input("🕒 Close Time", datetime(2025,1,1,15,0).time(), step=1800, key="spx_ct")
    lp = c3.number_input("🔽 Low Price", min_value=0.01, value=6130.4, format="%.2f", key="spx_lp")
    lt = c3.time_input("🕒 Low Time", datetime(2025,1,1,13,30).time(), step=1800, key="spx_lt")

    if st.button("🔮 Generate SPX"):
        ah = datetime.combine(forecast_date - timedelta(days=1), ht)
        ac = datetime.combine(forecast_date - timedelta(days=1), ct)
        al = datetime.combine(forecast_date - timedelta(days=1), lt)

        dfh = generate_spx(hp, SLOPES["SPX_HIGH"], ah, forecast_date, r, VOL["SPX"])
        dfc = generate_spx(cp, SLOPES["SPX_CLOSE"], ac, forecast_date, r, VOL["SPX"])
        dfl = generate_spx(lp, SLOPES["SPX_LOW"], al, forecast_date, r, VOL["SPX"])

        st.markdown("### 🔼 High Anchor Table")
        st.dataframe(dfh, use_container_width=True)
        st.markdown("### ⏹️ Close Anchor Table")
        st.dataframe(dfc, use_container_width=True)
        st.markdown("### 🔽 Low Anchor Table")
        st.dataframe(dfl, use_container_width=True)

# --- STOCK TABS ---
icons = {"TSLA":"🚗","NVDA":"🧠","AAPL":"🍎","AMZN":"📦","GOOGL":"🔍"}
for i, sym in enumerate(["TSLA","NVDA","AAPL","AMZN","GOOGL"], start=1):
    with tabs[i]:
        st.subheader(f"{icons[sym]} {sym} Forecast")
        col1, col2 = st.columns(2)
        lp = col1.number_input("🔽 Prev-Day Low Price", min_value=0.01, value=100.0, format="%.2f", key=f"{sym}_lp")
        lt = col1.time_input("🕒 Prev-Day Low Time", datetime(2025,1,1,8,30).time(), step=1800, key=f"{sym}_lt")
        hp = col2.number_input("🔼 Prev-Day High Price", min_value=0.01, value=110.0, format="%.2f", key=f"{sym}_hp")
        ht = col2.time_input("🕒 Prev-Day High Time", datetime(2025,1,1,8,30).time(), step=1800, key=f"{sym}_ht")

        if st.button(f"🔮 Generate {sym}"):
            a_low  = datetime.combine(forecast_date - timedelta(days=1), lt)
            a_high = datetime.combine(forecast_date - timedelta(days=1), ht)

            dflow  = generate_stock(lp, SLOPES[sym], a_low, forecast_date, r, VOL[sym], invert=True)
            dfhigh = generate_stock(hp, SLOPES[sym], a_high, forecast_date, r, VOL[sym], invert=False)

            st.markdown("### 🔻 Low Anchor Table")
            st.dataframe(dflow, use_container_width=True)
            st.markdown("### 🔺 High Anchor Table")
            st.dataframe(dfhigh, use_container_width=True)

# --- CLOSE CONTAINER ---
st.markdown('</div>', unsafe_allow_html=True)
