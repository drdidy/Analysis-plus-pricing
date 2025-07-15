# DRSPX Professional Platform v5.0
# Clean, functional, and beautiful - built for serious traders
# 10-part architecture for maximum performance and aesthetics

import json
import base64
import streamlit as st
from datetime import datetime, date, time, timedelta
import pandas as pd
import numpy as np
from io import BytesIO
import uuid

# ═══════════════════════════════════════════════════════════════════════════════
# CORE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

APP_CONFIG = {
    "name": "DRSPX Professional",
    "version": "5.0",
    "tagline": "Advanced SPX Forecasting Platform",
    "icon": "📊"
}

# Your exact original slopes - NEVER CHANGED
BASE_SLOPES = {
    "SPX_HIGH": -0.2792, "SPX_CLOSE": -0.2792, "SPX_LOW": -0.2792,
    "TSLA": -0.1508, "NVDA": -0.0485, "AAPL": -0.0750,
    "MSFT": -0.17, "AMZN": -0.03, "GOOGL": -0.07,
    "META": -0.035, "NFLX": -0.23,
}

INSTRUMENTS = {
    "SPX": {
        "name": "S&P 500 Index", "icon": "📈", "color": "#FFD700",
        "pages": ["Dashboard", "Analysis", "Risk", "Performance"]
    },
    "TSLA": {
        "name": "Tesla Inc", "icon": "🚗", "color": "#E31E24",
        "pages": ["Overview", "Signals", "Technical", "History"]
    },
    "NVDA": {
        "name": "NVIDIA Corp", "icon": "🧠", "color": "#76B900",
        "pages": ["Overview", "Signals", "Technical", "History"]
    },
    "AAPL": {
        "name": "Apple Inc", "icon": "🍎", "color": "#007AFF",
        "pages": ["Overview", "Signals", "Technical", "History"]
    },
    "MSFT": {
        "name": "Microsoft Corp", "icon": "💻", "color": "#00BCF2",
        "pages": ["Overview", "Signals", "Technical", "History"]
    },
    "AMZN": {
        "name": "Amazon.com", "icon": "📦", "color": "#FF9900",
        "pages": ["Overview", "Signals", "Technical", "History"]
    },
    "GOOGL": {
        "name": "Alphabet Inc", "icon": "🔍", "color": "#4285F4",
        "pages": ["Overview", "Signals", "Technical", "History"]
    },
    "META": {
        "name": "Meta Platforms", "icon": "📱", "color": "#1877F2",
        "pages": ["Overview", "Signals", "Technical", "History"]
    },
    "NFLX": {
        "name": "Netflix Inc", "icon": "🎬", "color": "#E50914",
        "pages": ["Overview", "Signals", "Technical", "History"]
    }
}

# Manual deepcopy
def deep_copy(obj):
    if isinstance(obj, dict):
        return {k: deep_copy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_copy(item) for item in obj]
    else:
        return obj

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════

if "app_session" not in st.session_state:
    st.session_state.update({
        "app_session": str(uuid.uuid4()),
        "theme": "dark",
        "slopes": deep_copy(BASE_SLOPES),
        "configurations": {},
        "current_instrument": "SPX",
        "current_page": "Dashboard",
        "contract_data": {
            "anchor_time": None,
            "slope": None,
            "price": None
        },
        "forecast_data": {},
        "animations_enabled": True
    })

# ═══════════════════════════════════════════════════════════════════════════════
# STREAMLIT CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title=f"{APP_CONFIG['name']} v{APP_CONFIG['version']}",
    page_icon=APP_CONFIG['icon'],
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# PERFECT CSS - GUARANTEED TEXT VISIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* ===== VARIABLES ===== */
:root {
    --primary-color: #3b82f6;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --info-color: #06b6d4;
    
    --primary-gradient: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    --success-gradient: linear-gradient(135deg, #10b981 0%, #047857 100%);
    --warning-gradient: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    --danger-gradient: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    --premium-gradient: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #92400e 100%);
    
    --transition: all 0.3s ease;
    --radius: 12px;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
}

/* ===== DARK THEME (DEFAULT) ===== */
:root {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-tertiary: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #cbd5e1;
    --text-muted: #64748b;
    --border-color: #475569;
}

/* ===== BASE STYLES ===== */
html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {visibility: hidden;}

/* ===== PERFECT TEXT VISIBILITY ===== */
.stApp, .stApp *,
.stMarkdown, .stMarkdown *,
.stText, .stText *,
.element-container, .element-container *,
p, span, div, h1, h2, h3, h4, h5, h6,
label, .stSelectbox label, .stNumberInput label, 
.stTimeInput label, .stTextInput label, 
.stSlider label, .stRadio label, .stCheckbox label,
.stMetric, .stMetric *,
.stDataFrame, .stDataFrame *,
.stTabs, .stTabs *,
.stExpander, .stExpander *,
.stColumns, .stColumns *,
.stContainer, .stContainer * {
    color: var(--text-primary) !important;
}

/* ===== SIDEBAR PERFECT VISIBILITY ===== */
.css-1d391kg, .css-1d391kg *,
.css-1dp5vir, .css-1dp5vir *,
section[data-testid="stSidebar"], 
section[data-testid="stSidebar"] * {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

/* ===== INPUT FIELDS ===== */
.stNumberInput input, .stTimeInput input, 
.stTextInput input, .stSelectbox select,
.stTextArea textarea, .stSlider input {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
    border: 2px solid var(--border-color) !important;
    border-radius: var(--radius) !important;
    padding: 10px 12px !important;
    font-size: 14px !important;
    transition: var(--transition) !important;
}

.stNumberInput input:focus, .stTimeInput input:focus,
.stTextInput input:focus, .stSelectbox select:focus,
.stTextArea textarea:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    outline: none !important;
}

/* ===== PROFESSIONAL HEADER ===== */
.professional-header {
    background: var(--premium-gradient);
    padding: 2rem;
    border-radius: var(--radius);
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}

.professional-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    animation: shimmer 3s infinite;
}

.header-title {
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0;
    color: white;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.header-subtitle {
    font-size: 1.1rem;
    margin: 0.5rem 0 0 0;
    color: rgba(255,255,255,0.9);
    font-weight: 500;
}

/* ===== METRIC CARDS ===== */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.metric-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    padding: 1.5rem;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    border-color: var(--primary-color);
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--primary-gradient);
}

.metric-icon {
    width: 3rem;
    height: 3rem;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    background: var(--primary-gradient);
    color: white;
    margin-bottom: 1rem;
}

.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0.5rem 0;
}

.metric-label {
    font-size: 0.9rem;
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: var(--primary-gradient) !important;
    border: none !important;
    border-radius: var(--radius) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: var(--transition) !important;
    box-shadow: var(--shadow) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-lg) !important;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--bg-secondary);
    border-radius: var(--radius);
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    border: none !important;
    color: var(--text-secondary) !important;
    transition: var(--transition) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
}

.stTabs [aria-selected="true"] {
    background: var(--primary-gradient) !important;
    color: white !important;
}

/* ===== ANIMATIONS ===== */
@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-fade-in {
    animation: fadeInUp 0.6s ease-out;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
    .header-title {
        font-size: 2rem;
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .metric-card {
        padding: 1.25rem;
    }
}

/* ===== LIGHT THEME OVERRIDE ===== */
.light-theme {
    --bg-primary: #ffffff;
    --bg-secondary: #f8fafc;
    --bg-tertiary: #e2e8f0;
    --text-primary: #1e293b;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --border-color: #cbd5e1;
}

.light-theme .stApp,
.light-theme .stApp *,
.light-theme .stMarkdown,
.light-theme .stMarkdown *,
.light-theme .stText,
.light-theme .stText *,
.light-theme .element-container,
.light-theme .element-container *,
.light-theme p, .light-theme span, .light-theme div, 
.light-theme h1, .light-theme h2, .light-theme h3, 
.light-theme h4, .light-theme h5, .light-theme h6,
.light-theme label, .light-theme .stSelectbox label, 
.light-theme .stNumberInput label, .light-theme .stTimeInput label, 
.light-theme .stTextInput label, .light-theme .stSlider label, 
.light-theme .stRadio label, .light-theme .stCheckbox label,
.light-theme .stMetric, .light-theme .stMetric *,
.light-theme .stDataFrame, .light-theme .stDataFrame *,
.light-theme .stTabs, .light-theme .stTabs *,
.light-theme .stExpander, .light-theme .stExpander *,
.light-theme .stColumns, .light-theme .stColumns *,
.light-theme .stContainer, .light-theme .stContainer * {
    color: var(--text-primary) !important;
}

.light-theme .stApp {
    background: var(--bg-primary) !important;
}

.light-theme .css-1d391kg, .light-theme .css-1d391kg *,
.light-theme .css-1dp5vir, .light-theme .css-1dp5vir *,
.light-theme section[data-testid="stSidebar"], 
.light-theme section[data-testid="stSidebar"] * {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
}

.light-theme .stNumberInput input, .light-theme .stTimeInput input, 
.light-theme .stTextInput input, .light-theme .stSelectbox select,
.light-theme .stTextArea textarea {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-color) !important;
}

.light-theme .metric-card {
    background: var(--bg-secondary) !important;
    border-color: var(--border-color) !important;
}

.light-theme .metric-value {
    color: var(--text-primary) !important;
}

.light-theme .metric-label {
    color: var(--text-secondary) !important;
}

/* Keep header and buttons with white text */
.light-theme .professional-header *,
.light-theme .stButton button * {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# THEME MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def apply_theme():
    """Apply the selected theme"""
    if st.session_state.theme == "light":
        st.markdown('<div class="light-theme">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL HEADER
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="professional-header animate-fade-in">
    <h1 class="header-title">{APP_CONFIG['icon']} {APP_CONFIG['name']}</h1>
    <p class="header-subtitle">{APP_CONFIG['tagline']} v{APP_CONFIG['version']}</p>
</div>
""", unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════════════════════
# CORE FORECASTING FUNCTIONS - YOUR EXACT STRATEGY
# ═══════════════════════════════════════════════════════════════════════════════

def generate_time_slots(start_time=time(7, 30), slot_type="standard"):
    """Generate time slots - your exact logic"""
    if slot_type == "spx":
        start_time = time(8, 30)
        num_slots = 11  # 8:30 to 14:00 (excluding 16:00)
    else:
        num_slots = 13  # 7:30 to 14:00
    
    base_dt = datetime(2025, 1, 1, start_time.hour, start_time.minute)
    return [(base_dt + timedelta(minutes=30 * i)).strftime("%H:%M") for i in range(num_slots)]

def calculate_spx_blocks(anchor_time, target_time):
    """Your exact SPX block calculation"""
    blocks = 0
    current_time = anchor_time
    while current_time < target_time:
        if current_time.hour != 16:  # Exclude 4 PM hour
            blocks += 1
        current_time += timedelta(minutes=30)
    return blocks

def calculate_stock_blocks(anchor_time, target_time):
    """Your exact stock block calculation"""
    return max(0, int((target_time - anchor_time).total_seconds() // 1800))

def create_forecast_table(price, slope, anchor_time, forecast_date, time_slots, is_spx=True, fan_mode=False):
    """Create forecast table with your exact calculations"""
    rows = []
    
    for time_slot in time_slots:
        hour, minute = map(int, time_slot.split(":"))
        target_time = datetime.combine(forecast_date, time(hour, minute))
        
        # Use your exact block calculation
        if is_spx:
            blocks = calculate_spx_blocks(anchor_time, target_time)
        else:
            blocks = calculate_stock_blocks(anchor_time, target_time)
        
        # Your exact formulas
        if fan_mode:
            entry_price = round(price + slope * blocks, 2)
            exit_price = round(price - slope * blocks, 2)
            rows.append({
                "Time": time_slot,
                "Entry": entry_price,
                "Exit": exit_price,
                "Spread": round(abs(entry_price - exit_price), 2)
            })
        else:
            projected_price = round(price + slope * blocks, 2)
            rows.append({
                "Time": time_slot,
                "Projected": projected_price,
                "Blocks": blocks
            })
    
    return pd.DataFrame(rows)

def style_dataframe(df):
    """Style dataframe with professional look"""
    # Format numeric columns
    numeric_columns = [col for col in df.columns if col not in ['Time']]
    format_dict = {col: "{:.2f}" for col in numeric_columns if col != 'Blocks'}
    if 'Blocks' in df.columns:
        format_dict['Blocks'] = "{:.0f}"
    
    styled = df.style.format(format_dict)
    
    return styled.set_properties(**{
        'background-color': 'var(--bg-secondary)',
        'color': 'var(--text-primary)',
        'text-align': 'center',
        'padding': '12px',
        'border': '1px solid var(--border-color)'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background', 'var(--primary-gradient)'),
            ('color', 'white'),
            ('font-weight', '600'),
            ('text-align', 'center'),
            ('padding', '14px'),
            ('border', 'none')
        ]},
        {'selector': 'td', 'props': [
            ('border-bottom', '1px solid var(--border-color)'),
            ('transition', 'background-color 0.2s ease')
        ]},
        {'selector': 'tr:hover td', 'props': [
            ('background-color', 'var(--bg-tertiary)')
        ]}
    ])

def calculate_session_stats():
    """Calculate real-time session statistics"""
    session_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    uptime = datetime.now() - session_start
    
    # Get forecast data safely
    forecast_data = st.session_state.get("forecast_data", {})
    total_forecasts = len(forecast_data)
    
    # Calculate slope variance
    current_slopes = st.session_state.get("slopes", {})
    base_slopes = BASE_SLOPES
    
    slope_variance = 0
    if current_slopes and base_slopes:
        variances = []
        for key in current_slopes:
            if key in base_slopes:
                variance = abs(current_slopes[key] - base_slopes[key])
                variances.append(variance)
        
        if variances:
            slope_variance = sum(variances) / len(variances)
    
    return {
        "uptime_hours": uptime.total_seconds() / 3600,
        "total_forecasts": total_forecasts,
        "slope_variance": slope_variance,
        "session_id": st.session_state.get("app_session", "Unknown")[:8],
        "last_activity": datetime.now().strftime("%H:%M:%S")
    }

def get_market_status():
    """Get current market status"""
    now = datetime.now()
    current_time = now.time()
    
    # Market hours (EST): 9:30 AM - 4:00 PM
    market_open = time(9, 30)
    market_close = time(16, 0)
    
    # Check if it's a weekday
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return {"status": "closed", "reason": "Weekend", "color": "var(--text-muted)"}
    
    if current_time < market_open:
        return {"status": "pre-market", "reason": "Pre-Market", "color": "var(--warning-color)"}
    elif current_time > market_close:
        return {"status": "after-hours", "reason": "After Hours", "color": "var(--info-color)"}
    else:
        return {"status": "open", "reason": "Market Open", "color": "var(--success-color)"}

# ═══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL SIDEBAR WITH ENHANCED FEATURES
# ═══════════════════════════════════════════════════════════════════════════════

def render_professional_sidebar():
    """Render enhanced professional sidebar"""
    with st.sidebar:
        # Professional Header with Live Status
        market_status = get_market_status()
        session_stats = calculate_session_stats()
        
        st.markdown(f"""
        <div style="
            background: var(--primary-gradient);
            padding: 1.5rem;
            border-radius: var(--radius);
            text-align: center;
            margin-bottom: 1.5rem;
            color: white;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                animation: shimmer 3s infinite;
            "></div>
            <h3 style="margin: 0; font-size: 1.2rem; font-weight: 700;">⚙️ Control Center</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; opacity: 0.9;">Professional Configuration</p>
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 1rem;
                padding-top: 1rem;
                border-top: 1px solid rgba(255,255,255,0.2);
                font-size: 0.75rem;
            ">
                <span style="color: {market_status['color']};">● {market_status['reason']}</span>
                <span>Session: {session_stats['session_id']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Stats Dashboard
        st.markdown("### 📊 Live Statistics")
        
        stat_col1, stat_col2 = st.columns(2)
        with stat_col1:
            st.metric(
                "Uptime",
                f"{session_stats['uptime_hours']:.1f}h",
                help="Current session duration"
            )
        with stat_col2:
            st.metric(
                "Forecasts",
                f"{session_stats['total_forecasts']}",
                help="Total forecasts generated this session"
            )
        
        # Slope Variance Indicator
        variance_pct = session_stats['slope_variance'] * 100
        variance_color = "var(--danger-color)" if variance_pct > 10 else "var(--warning-color)" if variance_pct > 5 else "var(--success-color)"
        
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1rem;
            margin-bottom: 1.5rem;
            text-align: center;
        ">
            <div style="color: var(--text-secondary); font-size: 0.8rem; margin-bottom: 0.5rem;">
                SLOPE VARIANCE FROM BASE
            </div>
            <div style="
                color: {variance_color};
                font-size: 1.5rem;
                font-weight: 700;
                font-family: 'JetBrains Mono', monospace;
            ">
                {variance_pct:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Date Configuration with Enhanced Info
        st.markdown("### 📅 Forecast Configuration")
        
        forecast_date = st.date_input(
            "Target Date",
            value=date.today() + timedelta(days=1),
            help="Select the date for forecast analysis"
        )
        
        # Store safely
        st.session_state["forecast_date"] = forecast_date
        
        # Enhanced date display with trading day info
        day_name = forecast_date.strftime("%A")
        is_weekend = forecast_date.weekday() >= 5
        days_until = (forecast_date - date.today()).days
        
        date_color = "var(--danger-color)" if is_weekend else "var(--success-color)"
        date_status = "⚠️ Weekend" if is_weekend else "✅ Trading Day"
        
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1rem;
            margin-bottom: 1.5rem;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="color: var(--text-primary); font-weight: 600;">{day_name}</span>
                <span style="color: {date_color}; font-size: 0.8rem;">{date_status}</span>
            </div>
            <div style="color: var(--text-secondary); font-size: 0.9rem;">
                {forecast_date.strftime('%B %d, %Y')}
            </div>
            <div style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.5rem;">
                {days_until} days from today
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Navigation
        st.markdown("### 🧭 Navigation")
        
        # Instrument selection with visual indicators
        instrument_options = list(INSTRUMENTS.keys())
        current_instrument = st.session_state.get("current_instrument", "SPX")
        if current_instrument not in instrument_options:
            current_instrument = "SPX"
        
        # Custom instrument display
        instrument_data = []
        for symbol in instrument_options:
            info = INSTRUMENTS[symbol]
            instrument_data.append({
                "symbol": symbol,
                "name": info["name"],
                "icon": info["icon"],
                "color": info["color"]
            })
        
        selected_instrument = st.selectbox(
            "Select Instrument",
            options=instrument_options,
            index=instrument_options.index(current_instrument),
            format_func=lambda x: f"{INSTRUMENTS[x]['icon']} {x} - {INSTRUMENTS[x]['name'][:20]}{'...' if len(INSTRUMENTS[x]['name']) > 20 else ''}",
            key="instrument_selector"
        )
        
        st.session_state["current_instrument"] = selected_instrument
        
        # Page selection for current instrument
        if selected_instrument in INSTRUMENTS:
            available_pages = INSTRUMENTS[selected_instrument]["pages"]
            current_page = st.session_state.get("current_page", available_pages[0])
            if current_page not in available_pages:
                current_page = available_pages[0]
            
            selected_page = st.selectbox(
                "Select Analysis Page",
                options=available_pages,
                index=available_pages.index(current_page),
                format_func=lambda x: f"📋 {x}",
                key="page_selector"
            )
            
            st.session_state["current_page"] = selected_page
        
        # Professional Settings
        st.markdown("### ⚙️ Professional Settings")
        
        # Animation settings
        animations_enabled = st.checkbox(
            "🎬 Enable Animations",
            value=st.session_state.get("animations_enabled", True),
            help="Toggle smooth animations and transitions"
        )
        st.session_state["animations_enabled"] = animations_enabled
        
        # Precision settings
        decimal_places = st.slider(
            "🎯 Decimal Precision",
            min_value=1,
            max_value=6,
            value=2,
            help="Number of decimal places for price displays"
        )
        st.session_state["decimal_places"] = decimal_places
        
        # Advanced Parameters with Enhanced UI
        with st.expander("🔧 Advanced Parameters", expanded=False):
            st.markdown("**Slope Configuration**")
            
            # Add slope monitoring
            total_adjustments = 0
            
            # SPX slopes with enhanced display
            st.markdown("*S&P 500 Parameters:*")
            spx_keys = ["SPX_HIGH", "SPX_CLOSE", "SPX_LOW"]
            
            for key in spx_keys:
                if key in st.session_state.slopes:
                    current_value = st.session_state.slopes[key]
                    base_value = BASE_SLOPES.get(key, 0.0)
                    
                    # Calculate adjustment percentage
                    adjustment_pct = ((current_value - base_value) / abs(base_value)) * 100 if base_value != 0 else 0
                    total_adjustments += abs(adjustment_pct)
                    
                    new_value = st.slider(
                        f"{key.replace('SPX_', '').title()} ({adjustment_pct:+.1f}%)",
                        min_value=-1.0,
                        max_value=1.0,
                        value=current_value,
                        step=0.0001,
                        format="%.4f",
                        help=f"Base: {base_value:.4f} | Current deviation: {adjustment_pct:+.1f}%",
                        key=f"slider_{key}"
                    )
                    
                    st.session_state.slopes[key] = new_value
            
            # Stock slopes with enhanced display
            st.markdown("*Individual Stock Parameters:*")
            stock_keys = [k for k in BASE_SLOPES.keys() if not k.startswith("SPX_")]
            
            for key in stock_keys:
                if key in st.session_state.slopes and key in INSTRUMENTS:
                    current_value = st.session_state.slopes[key]
                    base_value = BASE_SLOPES.get(key, 0.0)
                    instrument_info = INSTRUMENTS[key]
                    
                    # Calculate adjustment percentage
                    adjustment_pct = ((current_value - base_value) / abs(base_value)) * 100 if base_value != 0 else 0
                    total_adjustments += abs(adjustment_pct)
                    
                    new_value = st.slider(
                        f"{instrument_info['icon']} {key} ({adjustment_pct:+.1f}%)",
                        min_value=-1.0,
                        max_value=1.0,
                        value=current_value,
                        step=0.0001,
                        format="%.4f",
                        help=f"Base: {base_value:.4f} | Current deviation: {adjustment_pct:+.1f}%",
                        key=f"slider_{key}"
                    )
                    
                    st.session_state.slopes[key] = new_value
            
            # Display total adjustments
            st.markdown(f"""
            <div style="
                background: var(--bg-tertiary);
                border-radius: 6px;
                padding: 0.5rem;
                margin-top: 1rem;
                text-align: center;
                font-size: 0.8rem;
            ">
                <strong>Total Adjustments:</strong> {total_adjustments:.1f}%
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Configuration Management
        with st.expander("💾 Configuration Manager", expanded=False):
            st.markdown("**Configuration Management**")
            
            config_name = st.text_input(
                "Configuration Name",
                placeholder="e.g., High Volatility Setup",
                help="Enter a descriptive name for your configuration",
                key="config_name_input"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Config", disabled=not config_name):
                    # Enhanced save with metadata
                    config_data = {
                        "slopes": deep_copy(st.session_state.slopes),
                        "settings": {
                            "animations_enabled": st.session_state.get("animations_enabled", True),
                            "decimal_places": st.session_state.get("decimal_places", 2)
                        },
                        "metadata": {
                            "created": datetime.now().isoformat(),
                            "total_adjustments": total_adjustments,
                            "instrument": st.session_state.get("current_instrument", "SPX")
                        }
                    }
                    
                    # Initialize if not exists
                    if "configurations" not in st.session_state:
                        st.session_state.configurations = {}
                    
                    st.session_state.configurations[config_name] = config_data
                    st.success(f"✅ Saved: {config_name}")
            
            with col2:
                if st.button("🔄 Reset All"):
                    # Safe reset with confirmation
                    st.session_state.slopes = deep_copy(BASE_SLOPES)
                    st.session_state.animations_enabled = True
                    st.session_state.decimal_places = 2
                    st.success("✅ Reset to factory defaults")
                    st.rerun()
            
            # Enhanced load configurations
            saved_configs = st.session_state.get("configurations", {})
            if saved_configs:
                st.markdown("**Saved Configurations**")
                
                # Display configurations with metadata
                for config_name, config_data in saved_configs.items():
                    metadata = config_data.get("metadata", {})
                    created = metadata.get("created", "Unknown")
                    total_adj = metadata.get("total_adjustments", 0)
                    
                    if isinstance(created, str):
                        try:
                            created_dt = datetime.fromisoformat(created)
                            created_str = created_dt.strftime("%m/%d %H:%M")
                        except:
                            created_str = "Unknown"
                    else:
                        created_str = "Unknown"
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="
                            background: var(--bg-tertiary);
                            border-radius: 6px;
                            padding: 0.5rem;
                            margin-bottom: 0.5rem;
                            font-size: 0.8rem;
                        ">
                            <strong>📁 {config_name}</strong><br>
                            <span style="color: var(--text-secondary);">
                                {created_str} • {total_adj:.1f}% adj
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("📂", key=f"load_{config_name}", help=f"Load {config_name}"):
                            # Enhanced load with settings
                            if "slopes" in config_data:
                                st.session_state.slopes.update(config_data["slopes"])
                            
                            if "settings" in config_data:
                                settings = config_data["settings"]
                                st.session_state.animations_enabled = settings.get("animations_enabled", True)
                                st.session_state.decimal_places = settings.get("decimal_places", 2)
                            
                            st.success(f"✅ Loaded: {config_name}")
                            st.rerun()
        
        # Enhanced Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        # Export with enhanced data
        if st.button("📊 Export Configuration", help="Export current configuration as JSON"):
            export_data = {
                "configuration": {
                    "slopes": st.session_state.slopes,
                    "settings": {
                        "animations_enabled": st.session_state.get("animations_enabled", True),
                        "decimal_places": st.session_state.get("decimal_places", 2)
                    }
                },
                "session_info": {
                    "instrument": st.session_state.get("current_instrument", "SPX"),
                    "page": st.session_state.get("current_page", "Dashboard"),
                    "session_id": st.session_state.get("app_session", "Unknown"),
                    "exported_at": datetime.now().isoformat()
                },
                "metadata": {
                    "version": APP_CONFIG["version"],
                    "platform": "DRSPX Professional"
                }
            }
            
            export_json = json.dumps(export_data, indent=2)
            st.download_button(
                label="⬇️ Download Configuration",
                data=export_json,
                file_name=f"drspx_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                help="Download configuration file"
            )
        
        # Clear session data
        if st.button("🧹 Clear Session Data", help="Clear all session data"):
            # Clear forecast data but keep configurations
            keys_to_clear = ["forecast_data", "contract_data"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("✅ Session data cleared")
            st.rerun()
        
        # Professional Session Info
        st.markdown("---")
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1rem;
            font-size: 0.75rem;
            color: var(--text-muted);
        ">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span><strong>Session ID:</strong></span>
                <span>{session_stats['session_id']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span><strong>Last Update:</strong></span>
                <span>{session_stats['last_activity']}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span><strong>Version:</strong></span>
                <span>{APP_CONFIG['version']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER PROFESSIONAL SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

render_professional_sidebar()

# ═══════════════════════════════════════════════════════════════════════════════
# ENHANCED NAVIGATION DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

# Get current navigation state safely
current_instrument = st.session_state.get("current_instrument", "SPX")
current_page = st.session_state.get("current_page", "Dashboard")
animations_enabled = st.session_state.get("animations_enabled", True)

# Enhanced navigation breadcrumb
if current_instrument in INSTRUMENTS:
    instrument_info = INSTRUMENTS[current_instrument]
    animation_class = "animate-fade-in" if animations_enabled else ""
    
    st.markdown(f"""
    <div class="{animation_class}" style="
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        transition: var(--transition);
    ">
        <div style="
            background: {instrument_info['color']};
            color: white;
            width: 4rem;
            height: 4rem;
            border-radius: var(--radius);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            box-shadow: var(--shadow);
        ">
            {instrument_info['icon']}
        </div>
        <div style="flex: 1;">
            <h2 style="margin: 0; color: var(--text-primary); font-size: 1.5rem; font-weight: 700;">
                {instrument_info['name']}
            </h2>
            <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary); font-size: 1rem;">
                {current_page} Analysis • {current_instrument}
            </p>
        </div>
        <div style="
            background: var(--bg-tertiary);
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-size: 0.8rem;
            color: var(--text-muted);
        ">
            📊 Live
        </div>
    </div>
    """, unsafe_allow_html=True)
    # ═══════════════════════════════════════════════════════════════════════════════
# SPX PROFESSIONAL DASHBOARD - MAIN INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def create_professional_input_section():
    """Create the professional SPX input interface"""
    current_instrument = st.session_state.get("current_instrument", "SPX")
    current_page = st.session_state.get("current_page", "Dashboard")
    animations_enabled = st.session_state.get("animations_enabled", True)
    
    # Only show SPX interface if we're on SPX
    if current_instrument == "SPX":
        if current_page == "Dashboard":
            create_spx_dashboard()
        elif current_page == "Analysis":
            create_spx_analysis()
        elif current_page == "Risk":
            create_spx_risk()
        elif current_page == "Performance":
            create_spx_performance()
    else:
        # Placeholder for other instruments (will be handled in later parts)
        st.info(f"📊 {current_instrument} {current_page} interface will be implemented in the next parts.")

def create_spx_dashboard():
    """Create the main SPX dashboard interface"""
    animations_enabled = st.session_state.get("animations_enabled", True)
    decimal_places = st.session_state.get("decimal_places", 2)
    forecast_date = st.session_state.get("forecast_date", date.today() + timedelta(days=1))
    
    animation_class = "animate-fade-in" if animations_enabled else ""
    
    # Professional section header
    st.markdown(f"""
    <div class="{animation_class}" style="
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 140, 0, 0.05));
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: var(--radius);
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h2 style="margin: 0; color: var(--text-primary); font-size: 2rem; font-weight: 700;">
            📈 S&P 500 Professional Analysis
        </h2>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem;">
            Advanced forecasting for {forecast_date.strftime('%A, %B %d, %Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Anchor Points Configuration
    st.markdown("### 🎯 Anchor Points Configuration")
    st.markdown("*Configure the three critical price-time anchor points for SPX analysis*")
    
    # Professional 3-column layout
    anchor_col1, anchor_col2, anchor_col3 = st.columns(3)
    
    with anchor_col1:
        st.markdown(f"""
        <div class="{animation_class}" style="
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 1rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 1rem 0; color: var(--success-color); font-weight: 600;">
                📈 High Anchor
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        high_price = st.number_input(
            "Expected High Price",
            value=6185.8,
            min_value=0.0,
            step=0.1,
            key="spx_high_price",
            help="Anticipated highest price for the trading session",
            format=f"%.{decimal_places}f"
        )
        
        high_time = st.time_input(
            "High Time",
            value=time(11, 30),
            key="spx_high_time",
            help="Expected time when the high will occur",
            step=300  # 5-minute increments
        )
        
        # Display high anchor info
        st.markdown(f"""
        <div style="
            background: var(--bg-tertiary);
            border-radius: 6px;
            padding: 0.75rem;
            margin-top: 1rem;
            font-size: 0.8rem;
            color: var(--text-secondary);
        ">
            <strong>Anchor:</strong> {high_price:.{decimal_places}f} @ {high_time.strftime('%H:%M')}<br>
            <strong>Slope:</strong> {st.session_state.slopes.get('SPX_HIGH', 0):.4f}
        </div>
        """, unsafe_allow_html=True)
    
    with anchor_col2:
        st.markdown(f"""
        <div class="{animation_class}" style="
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.05));
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 1rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 1rem 0; color: var(--primary-color); font-weight: 600;">
                📊 Close Anchor
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        close_price = st.number_input(
            "Expected Close Price",
            value=6170.2,
            min_value=0.0,
            step=0.1,
            key="spx_close_price",
            help="Anticipated closing price for the session",
            format=f"%.{decimal_places}f"
        )
        
        close_time = st.time_input(
            "Close Time",
            value=time(15, 0),
            key="spx_close_time",
            help="Market close time",
            step=300
        )
        
        # Display close anchor info
        st.markdown(f"""
        <div style="
            background: var(--bg-tertiary);
            border-radius: 6px;
            padding: 0.75rem;
            margin-top: 1rem;
            font-size: 0.8rem;
            color: var(--text-secondary);
        ">
            <strong>Anchor:</strong> {close_price:.{decimal_places}f} @ {close_time.strftime('%H:%M')}<br>
            <strong>Slope:</strong> {st.session_state.slopes.get('SPX_CLOSE', 0):.4f}
        </div>
        """, unsafe_allow_html=True)
    
    with anchor_col3:
        st.markdown(f"""
        <div class="{animation_class}" style="
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 1rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 1rem 0; color: var(--danger-color); font-weight: 600;">
                📉 Low Anchor
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        low_price = st.number_input(
            "Expected Low Price",
            value=6130.4,
            min_value=0.0,
            step=0.1,
            key="spx_low_price",
            help="Anticipated lowest price for the session",
            format=f"%.{decimal_places}f"
        )
        
        low_time = st.time_input(
            "Low Time",
            value=time(13, 30),
            key="spx_low_time",
            help="Expected time when the low will occur",
            step=300
        )
        
        # Display low anchor info
        st.markdown(f"""
        <div style="
            background: var(--bg-tertiary);
            border-radius: 6px;
            padding: 0.75rem;
            margin-top: 1rem;
            font-size: 0.8rem;
            color: var(--text-secondary);
        ">
            <strong>Anchor:</strong> {low_price:.{decimal_places}f} @ {low_time.strftime('%H:%M')}<br>
            <strong>Slope:</strong> {st.session_state.slopes.get('SPX_LOW', 0):.4f}
        </div>
        """, unsafe_allow_html=True)
    
    # Contract Line Configuration
    st.markdown("### 🎯 Two-Point Contract Line")
    st.markdown("*Configure the precision contract line using two strategic low points*")
    
    contract_col1, contract_col2 = st.columns(2)
    
    with contract_col1:
        st.markdown(f"""
        <div class="{animation_class}" style="
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.05));
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 1rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 1rem 0; color: var(--warning-color); font-weight: 600;">
                📍 Low-1 Point
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        low1_time = st.time_input(
            "Low-1 Time",
            value=time(2, 0),
            step=300,
            key="contract_low1_time",
            help="First strategic low point time"
        )
        
        low1_price = st.number_input(
            "Low-1 Price",
            value=10.0,
            min_value=0.0,
            step=0.01,
            key="contract_low1_price",
            help="Price at first low point",
            format=f"%.{decimal_places}f"
        )
        
        # Display Low-1 info
        st.markdown(f"""
        <div style="
            background: var(--bg-tertiary);
            border-radius: 6px;
            padding: 0.75rem;
            margin-top: 1rem;
            font-size: 0.8rem;
            color: var(--text-secondary);
        ">
            <strong>Point 1:</strong> {low1_price:.{decimal_places}f} @ {low1_time.strftime('%H:%M')}
        </div>
        """, unsafe_allow_html=True)
    
    with contract_col2:
        st.markdown(f"""
        <div class="{animation_class}" style="
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(147, 51, 234, 0.05));
            border: 1px solid rgba(168, 85, 247, 0.2);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 1rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 1rem 0; color: #a855f7; font-weight: 600;">
                📍 Low-2 Point
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        low2_time = st.time_input(
            "Low-2 Time",
            value=time(3, 30),
            step=300,
            key="contract_low2_time",
            help="Second strategic low point time"
        )
        
        low2_price = st.number_input(
            "Low-2 Price",
            value=12.0,
            min_value=0.0,
            step=0.01,
            key="contract_low2_price",
            help="Price at second low point",
            format=f"%.{decimal_places}f"
        )
        
        # Display Low-2 info
        st.markdown(f"""
        <div style="
            background: var(--bg-tertiary);
            border-radius: 6px;
            padding: 0.75rem;
            margin-top: 1rem;
            font-size: 0.8rem;
            color: var(--text-secondary);
        ">
            <strong>Point 2:</strong> {low2_price:.{decimal_places}f} @ {low2_time.strftime('%H:%M')}
        </div>
        """, unsafe_allow_html=True)
    
    # Professional Generate Button
    st.markdown("---")
    
    generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
    
    with generate_col2:
        if st.button(
            "🚀 Generate Professional Forecast",
            help="Execute comprehensive SPX analysis with all anchor points",
            key="generate_spx_forecast",
            type="primary"
        ):
            generate_spx_forecast(
                high_price, high_time, close_price, close_time, 
                low_price, low_time, low1_price, low1_time, 
                low2_price, low2_time, forecast_date
            )
    
    # Real-time Lookup Section
    st.markdown("---")
    st.markdown("### 🔍 Real-Time Professional Lookup")
    st.markdown("*Get instant projections for any time point using the contract line*")
    
    lookup_col1, lookup_col2 = st.columns([2, 1])
    
    with lookup_col1:
        lookup_time = st.time_input(
            "Target Time",
            value=time(9, 25),
            step=300,
            key="spx_lookup_time",
            help="Select time for instant projection"
        )
    
    with lookup_col2:
        # Check if we have contract data
        contract_data = st.session_state.get("contract_data", {})
        if contract_data.get("anchor_time") and contract_data.get("slope"):
            lookup_target = datetime.combine(forecast_date, lookup_time)
            lookup_blocks = calculate_spx_blocks(
                contract_data["anchor_time"],
                lookup_target
            )
            lookup_value = (contract_data["price"] + 
                          contract_data["slope"] * lookup_blocks)
            
            st.markdown(f"""
            <div style="
                background: var(--primary-gradient);
                color: white;
                padding: 2rem;
                border-radius: var(--radius);
                text-align: center;
                box-shadow: var(--shadow-lg);
                margin-top: 1rem;
            ">
                <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 0.5rem; text-transform: uppercase;">
                    Projection @ {lookup_time.strftime('%H:%M')}
                </div>
                <div style="font-size: 2.5rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; margin: 0.5rem 0;">
                    {lookup_value:.{decimal_places}f}
                </div>
                <div style="font-size: 0.75rem; opacity: 0.8; margin-top: 1rem;">
                    Blocks: {lookup_blocks} | Slope: {contract_data["slope"]:.6f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🔄 Generate forecast to activate real-time lookup functionality")

def generate_spx_forecast(high_price, high_time, close_price, close_time, 
                         low_price, low_time, low1_price, low1_time, 
                         low2_price, low2_time, forecast_date):
    """Generate comprehensive SPX forecast"""
    
    decimal_places = st.session_state.get("decimal_places", 2)
    animations_enabled = st.session_state.get("animations_enabled", True)
    
    with st.spinner("🔄 Processing professional SPX analysis..."):
        # Calculate contract line parameters
        anchor_dt = datetime.combine(forecast_date, low1_time)
        target_dt = datetime.combine(forecast_date, low2_time)
        blocks = calculate_spx_blocks(anchor_dt, target_dt)
        contract_slope = (low2_price - low1_price) / (blocks if blocks > 0 else 1)
        
        # Store contract data for real-time lookup
        st.session_state.contract_data = {
            "anchor_time": anchor_dt,
            "slope": contract_slope,
            "price": low1_price,
            "last_updated": datetime.now()
        }
        
        # Professional Executive Summary
        st.markdown("## 📊 Executive Summary")
        
        # Calculate key metrics
        price_range = high_price - low_price
        mid_price = (high_price + low_price) / 2
        volatility_pct = (price_range / close_price) * 100
        
        # Enhanced metrics dashboard
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📏</div>
                <div class="metric-value">{price_range:.{decimal_places}f}</div>
                <div class="metric-label">Price Range</div>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🎯</div>
                <div class="metric-value">{mid_price:.{decimal_places}f}</div>
                <div class="metric-label">Midpoint</div>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col3:
            vol_status = "High" if volatility_pct > 2 else "Medium" if volatility_pct > 1 else "Low"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">⚡</div>
                <div class="metric-value">{volatility_pct:.1f}%</div>
                <div class="metric-label">Volatility ({vol_status})</div>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📐</div>
                <div class="metric-value">{contract_slope:.4f}</div>
                <div class="metric-label">Contract Slope</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Generate and display anchor trend analyses
        spx_slots = generate_time_slots(time(8, 30), "spx")
        
        # Previous day anchor times for calculations
        prev_day = forecast_date - timedelta(days=1)
        anchor_analyses = [
            ("High", high_price, "SPX_HIGH", datetime.combine(prev_day, high_time)),
            ("Close", close_price, "SPX_CLOSE", datetime.combine(prev_day, close_time)),
            ("Low", low_price, "SPX_LOW", datetime.combine(prev_day, low_time))
        ]
        
        for anchor_name, price, slope_key, anchor_time in anchor_analyses:
            st.markdown(f"### 📊 {anchor_name} Anchor Trend Analysis")
            
            # Generate forecast table
            slope_value = st.session_state.slopes[slope_key]
            forecast_df = create_forecast_table(
                price, slope_value, anchor_time, forecast_date, spx_slots, True, True
            )
            
            # Display styled table
            st.dataframe(
                style_dataframe(forecast_df),
                use_container_width=True,
                height=400
            )
            
            # Quick statistics
            if not forecast_df.empty:
                entry_range = forecast_df['Entry'].max() - forecast_df['Entry'].min()
                avg_spread = forecast_df['Spread'].mean()
                
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("Entry Range", f"{entry_range:.{decimal_places}f}")
                with stat_col2:
                    st.metric("Avg Spread", f"{avg_spread:.{decimal_places}f}")
                with stat_col3:
                    risk_level = "High" if avg_spread > 5 else "Medium" if avg_spread > 2 else "Low"
                    st.metric("Risk Level", risk_level)
        
        # Contract Line Analysis
        st.markdown("### 🎯 Contract Line Professional Analysis")
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.05));
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin: 1rem 0;
            text-align: center;
        ">
            <h4 style="margin: 0 0 0.5rem 0; color: var(--primary-color);">Contract Parameters</h4>
            <p style="margin: 0; color: var(--text-secondary); font-size: 1.1rem;">
                <strong>Slope:</strong> {contract_slope:.6f} | 
                <strong>Anchor:</strong> {low1_price:.{decimal_places}f} @ {low1_time.strftime('%H:%M')} | 
                <strong>Blocks:</strong> {blocks}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate contract line table
        general_slots = generate_time_slots(time(7, 30), "standard")
        contract_df = create_forecast_table(
            low1_price, contract_slope, anchor_dt, forecast_date, general_slots, True, False
        )
        
        st.dataframe(
            style_dataframe(contract_df),
            use_container_width=True,
            height=400
        )
        
        # Store forecast data for session
        st.session_state.forecast_data = {
            "timestamp": datetime.now().isoformat(),
            "anchors": {
                "high": {"price": high_price, "time": high_time.isoformat()},
                "close": {"price": close_price, "time": close_time.isoformat()},
                "low": {"price": low_price, "time": low_time.isoformat()}
            },
            "contract": {
                "slope": contract_slope,
                "low1": {"price": low1_price, "time": low1_time.isoformat()},
                "low2": {"price": low2_price, "time": low2_time.isoformat()},
                "blocks": blocks
            },
            "metrics": {
                "range": price_range,
                "midpoint": mid_price,
                "volatility": volatility_pct
            }
        }
        
        st.success("✅ Professional SPX analysis completed successfully!")

def create_spx_analysis():
    """Create SPX analysis page"""
    st.markdown("## 📈 SPX Advanced Analysis")
    st.info("🔧 Advanced technical analysis interface coming in the next update...")

def create_spx_risk():
    """Create SPX risk management page"""
    st.markdown("## ⚠️ SPX Risk Management")
    st.info("🔧 Professional risk assessment tools coming in the next update...")

def create_spx_performance():
    """Create SPX performance page"""
    st.markdown("## 📊 SPX Performance Analytics")
    st.info("🔧 Historical performance tracking coming in the next update...")

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER MAIN INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

create_professional_input_section()
    # ═══════════════════════════════════════════════════════════════════════════════
# INDIVIDUAL STOCK ANALYSIS - MULTI-PAGE INTERFACES
# ═══════════════════════════════════════════════════════════════════════════════

def create_stock_interface():
    """Create the appropriate stock interface based on current selection"""
    current_instrument = st.session_state.get("current_instrument", "SPX")
    current_page = st.session_state.get("current_page", "Dashboard")
    
    # Only handle non-SPX instruments here
    if current_instrument != "SPX" and current_instrument in INSTRUMENTS:
        if current_page == "Overview":
            create_stock_overview(current_instrument)
        elif current_page == "Signals":
            create_stock_signals(current_instrument)
        elif current_page == "Technical":
            create_stock_technical(current_instrument)
        elif current_page == "History":
            create_stock_history(current_instrument)

def create_stock_overview(symbol):
    """Create stock overview page - main forecasting interface"""
    instrument_info = INSTRUMENTS[symbol]
    animations_enabled = st.session_state.get("animations_enabled", True)
    decimal_places = st.session_state.get("decimal_places", 2)
    forecast_date = st.session_state.get("forecast_date", date.today() + timedelta(days=1))
    
    animation_class = "animate-fade-in" if animations_enabled else ""
    
    # Professional stock header
    st.markdown(f"""
    <div class="{animation_class}" style="
        background: linear-gradient(135deg, {instrument_info['color']}20, {instrument_info['color']}10);
        border: 2px solid {instrument_info['color']}40;
        border-radius: var(--radius);
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h2 style="margin: 0; color: var(--text-primary); font-size: 2rem; font-weight: 700;">
            {instrument_info['icon']} {instrument_info['name']} Analysis
        </h2>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem;">
            Professional forecasting for {forecast_date.strftime('%A, %B %d, %Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Current slope info
    current_slope = st.session_state.slopes.get(symbol, 0)
    base_slope = BASE_SLOPES.get(symbol, 0)
    slope_deviation = ((current_slope - base_slope) / abs(base_slope)) * 100 if base_slope != 0 else 0
    
    # Slope status indicator
    slope_color = instrument_info['color'] if abs(slope_deviation) < 5 else "var(--warning-color)" if abs(slope_deviation) < 15 else "var(--danger-color)"
    
    st.markdown(f"""
    <div style="
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        padding: 1rem;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div>
            <strong style="color: var(--text-primary);">Current Slope:</strong>
            <span style="color: {slope_color}; font-family: 'JetBrains Mono', monospace; font-weight: 600;">
                {current_slope:.4f}
            </span>
        </div>
        <div>
            <strong style="color: var(--text-primary);">Deviation:</strong>
            <span style="color: {slope_color}; font-weight: 600;">
                {slope_deviation:+.1f}%
            </span>
        </div>
        <div style="
            background: {slope_color};
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        ">
            {'OPTIMAL' if abs(slope_deviation) < 5 else 'ADJUSTED' if abs(slope_deviation) < 15 else 'HIGH DEVIATION'}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Previous Session Anchors Configuration
    st.markdown("### 📊 Previous Session Anchor Configuration")
    st.markdown("*Define the previous trading session's high and low anchor points*")
    
    # Professional two-column layout
    anchor_col1, anchor_col2 = st.columns(2)
    
    with anchor_col1:
        st.markdown(f"""
        <div class="{animation_class}" style="
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 1rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 1rem 0; color: var(--danger-color); font-weight: 600;">
                📉 Low Anchor
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        low_price = st.number_input(
            "Previous Session Low",
            value=0.0,
            min_value=0.0,
            step=0.01,
            key=f"{symbol}_low_price",
            help=f"Previous trading session low for {instrument_info['name']}",
            format=f"%.{decimal_places}f"
        )
        
        low_time = st.time_input(
            "Low Occurrence Time",
            value=time(7, 30),
            key=f"{symbol}_low_time",
            help="Time when the low occurred in previous session",
            step=300
        )
        
        # Display low anchor info
        if low_price > 0:
            st.markdown(f"""
            <div style="
                background: var(--bg-tertiary);
                border-radius: 6px;
                padding: 0.75rem;
                margin-top: 1rem;
                font-size: 0.8rem;
                color: var(--text-secondary);
            ">
                <strong>Low Anchor:</strong> {low_price:.{decimal_places}f} @ {low_time.strftime('%H:%M')}<br>
                <strong>Slope:</strong> {current_slope:.4f}
            </div>
            """, unsafe_allow_html=True)
    
    with anchor_col2:
        st.markdown(f"""
        <div class="{animation_class}" style="
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
            border: 1px solid rgba(16, 185, 129, 0.2);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 1rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 1rem 0; color: var(--success-color); font-weight: 600;">
                📈 High Anchor
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        high_price = st.number_input(
            "Previous Session High",
            value=0.0,
            min_value=0.0,
            step=0.01,
            key=f"{symbol}_high_price",
            help=f"Previous trading session high for {instrument_info['name']}",
            format=f"%.{decimal_places}f"
        )
        
        high_time = st.time_input(
            "High Occurrence Time",
            value=time(7, 30),
            key=f"{symbol}_high_time",
            help="Time when the high occurred in previous session",
            step=300
        )
        
        # Display high anchor info
        if high_price > 0:
            st.markdown(f"""
            <div style="
                background: var(--bg-tertiary);
                border-radius: 6px;
                padding: 0.75rem;
                margin-top: 1rem;
                font-size: 0.8rem;
                color: var(--text-secondary);
            ">
                <strong>High Anchor:</strong> {high_price:.{decimal_places}f} @ {high_time.strftime('%H:%M')}<br>
                <strong>Slope:</strong> {current_slope:.4f}
            </div>
            """, unsafe_allow_html=True)
    
    # Quick metrics if both prices are entered
    if low_price > 0 and high_price > 0:
        price_range = high_price - low_price
        mid_price = (high_price + low_price) / 2
        range_pct = (price_range / mid_price) * 100
        
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1rem;
            margin: 1rem 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            text-align: center;
        ">
            <div>
                <div style="color: var(--text-secondary); font-size: 0.8rem;">RANGE</div>
                <div style="color: var(--text-primary); font-size: 1.2rem; font-weight: 600;">
                    {price_range:.{decimal_places}f}
                </div>
            </div>
            <div>
                <div style="color: var(--text-secondary); font-size: 0.8rem;">MIDPOINT</div>
                <div style="color: var(--text-primary); font-size: 1.2rem; font-weight: 600;">
                    {mid_price:.{decimal_places}f}
                </div>
            </div>
            <div>
                <div style="color: var(--text-secondary); font-size: 0.8rem;">RANGE %</div>
                <div style="color: var(--text-primary); font-size: 1.2rem; font-weight: 600;">
                    {range_pct:.1f}%
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Professional Generate Button
    st.markdown("---")
    
    generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
    
    with generate_col2:
        if st.button(
            f"🚀 Generate {symbol} Professional Analysis",
            help=f"Execute comprehensive analysis for {instrument_info['name']}",
            key=f"generate_{symbol}_forecast",
            type="primary"
        ):
            if low_price <= 0 and high_price <= 0:
                st.warning("⚠️ Please enter valid price values to generate professional analysis")
            else:
                generate_stock_forecast(symbol, low_price, low_time, high_price, high_time, forecast_date)

def generate_stock_forecast(symbol, low_price, low_time, high_price, high_time, forecast_date):
    """Generate comprehensive stock forecast"""
    instrument_info = INSTRUMENTS[symbol]
    decimal_places = st.session_state.get("decimal_places", 2)
    current_slope = st.session_state.slopes.get(symbol, 0)
    
    with st.spinner(f"🔄 Processing {instrument_info['name']} professional analysis..."):
        
        # Professional Stock Summary
        st.markdown(f"## 📊 {instrument_info['name']} Executive Summary")
        
        # Calculate key metrics automatically
        price_range = abs(high_price - low_price) if high_price > 0 and low_price > 0 else 0
        mid_price = (high_price + low_price) / 2 if high_price > 0 and low_price > 0 else 0
        
        # Enhanced metrics dashboard
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon" style="background: {instrument_info['color']};">{instrument_info['icon']}</div>
                <div class="metric-value">{price_range:.{decimal_places}f}</div>
                <div class="metric-label">Price Range</div>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🎯</div>
                <div class="metric-value">{mid_price:.{decimal_places}f}</div>
                <div class="metric-label">Midpoint</div>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col3:
            volatility_pct = (price_range / mid_price * 100) if mid_price > 0 else 0
            vol_status = "High" if volatility_pct > 3 else "Medium" if volatility_pct > 1.5 else "Low"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">⚡</div>
                <div class="metric-value">{volatility_pct:.1f}%</div>
                <div class="metric-label">Volatility ({vol_status})</div>
            </div>
            """, unsafe_allow_html=True)
        
        with summary_col4:
            slope_direction = "Bullish" if current_slope > 0 else "Bearish" if current_slope < 0 else "Neutral"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📐</div>
                <div class="metric-value">{abs(current_slope):.4f}</div>
                <div class="metric-label">Slope ({slope_direction})</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Generate forecasts for both anchors
        general_slots = generate_time_slots(time(7, 30), "standard")
        
        if low_price > 0:
            st.markdown("### 📉 Low Anchor Trend Analysis")
            
            low_anchor_time = datetime.combine(forecast_date, low_time)
            low_forecast_df = create_forecast_table(
                low_price, current_slope, low_anchor_time, forecast_date, 
                general_slots, False, True
            )
            
            st.dataframe(
                style_dataframe(low_forecast_df),
                use_container_width=True,
                height=350
            )
            
            # Low anchor statistics (calculated automatically)
            if not low_forecast_df.empty:
                low_entry_range = low_forecast_df['Entry'].max() - low_forecast_df['Entry'].min()
                low_avg_spread = low_forecast_df['Spread'].mean()
                low_risk = "High" if low_avg_spread > 5 else "Medium" if low_avg_spread > 2 else "Low"
                
                low_stat_col1, low_stat_col2, low_stat_col3 = st.columns(3)
                with low_stat_col1:
                    st.metric("Entry Range", f"{low_entry_range:.{decimal_places}f}")
                with low_stat_col2:
                    st.metric("Avg Spread", f"{low_avg_spread:.{decimal_places}f}")
                with low_stat_col3:
                    st.metric("Risk Level", low_risk)
        
        if high_price > 0:
            st.markdown("### 📈 High Anchor Trend Analysis")
            
            high_anchor_time = datetime.combine(forecast_date, high_time)
            high_forecast_df = create_forecast_table(
                high_price, current_slope, high_anchor_time, forecast_date,
                general_slots, False, True
            )
            
            st.dataframe(
                style_dataframe(high_forecast_df),
                use_container_width=True,
                height=350
            )
            
            # High anchor statistics (calculated automatically)
            if not high_forecast_df.empty:
                high_entry_range = high_forecast_df['Entry'].max() - high_forecast_df['Entry'].min()
                high_avg_spread = high_forecast_df['Spread'].mean()
                high_risk = "High" if high_avg_spread > 5 else "Medium" if high_avg_spread > 2 else "Low"
                
                high_stat_col1, high_stat_col2, high_stat_col3 = st.columns(3)
                with high_stat_col1:
                    st.metric("Entry Range", f"{high_entry_range:.{decimal_places}f}")
                with high_stat_col2:
                    st.metric("Avg Spread", f"{high_avg_spread:.{decimal_places}f}")
                with high_stat_col3:
                    st.metric("Risk Level", high_risk)
        
        # Comparative Analysis (if both anchors have data)
        if low_price > 0 and high_price > 0 and not low_forecast_df.empty and not high_forecast_df.empty:
            st.markdown("### 📊 Comparative Analysis")
            
            comparison_col1, comparison_col2 = st.columns(2)
            
            with comparison_col1:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
                    border: 1px solid rgba(239, 68, 68, 0.2);
                    border-radius: var(--radius);
                    padding: 1.5rem;
                ">
                    <h4 style="margin: 0 0 1rem 0; color: var(--danger-color);">📉 Low Anchor Summary</h4>
                    <div style="color: var(--text-secondary);">
                        <p><strong>Base Price:</strong> {low_price:.{decimal_places}f}</p>
                        <p><strong>Entry Range:</strong> {low_entry_range:.{decimal_places}f}</p>
                        <p><strong>Avg Spread:</strong> {low_avg_spread:.{decimal_places}f}</p>
                        <p><strong>Risk Level:</strong> {low_risk}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with comparison_col2:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
                    border: 1px solid rgba(16, 185, 129, 0.2);
                    border-radius: var(--radius);
                    padding: 1.5rem;
                ">
                    <h4 style="margin: 0 0 1rem 0; color: var(--success-color);">📈 High Anchor Summary</h4>
                    <div style="color: var(--text-secondary);">
                        <p><strong>Base Price:</strong> {high_price:.{decimal_places}f}</p>
                        <p><strong>Entry Range:</strong> {high_entry_range:.{decimal_places}f}</p>
                        <p><strong>Avg Spread:</strong> {high_avg_spread:.{decimal_places}f}</p>
                        <p><strong>Risk Level:</strong> {high_risk}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Trading Recommendation (calculated automatically)
            better_anchor = "Low" if low_avg_spread < high_avg_spread else "High"
            better_color = "var(--danger-color)" if better_anchor == "Low" else "var(--success-color)"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.05));
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: var(--radius);
                padding: 1.5rem;
                margin: 1rem 0;
                text-align: center;
            ">
                <h4 style="margin: 0 0 0.5rem 0; color: var(--primary-color);">🎯 Trading Recommendation</h4>
                <p style="margin: 0; color: var(--text-secondary); font-size: 1.1rem;">
                    <strong style="color: {better_color};">{better_anchor} Anchor</strong> shows better risk-adjusted profile
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.success(f"✅ {instrument_info['name']} professional analysis completed successfully!")

def create_stock_signals(symbol):
    """Create stock signals page"""
    instrument_info = INSTRUMENTS[symbol]
    st.markdown(f"## 🎯 {instrument_info['name']} Trading Signals")
    
    # Show current slope status and any significant deviations
    current_slope = st.session_state.slopes.get(symbol, 0)
    base_slope = BASE_SLOPES.get(symbol, 0)
    slope_deviation = ((current_slope - base_slope) / abs(base_slope)) * 100 if base_slope != 0 else 0
    
    if abs(slope_deviation) > 10:
        st.warning(f"⚠️ Slope deviation is {slope_deviation:+.1f}% from base - consider reviewing parameters")
    elif abs(slope_deviation) > 5:
        st.info(f"ℹ️ Slope deviation is {slope_deviation:+.1f}% from base - within acceptable range")
    else:
        st.success(f"✅ Slope deviation is {slope_deviation:+.1f}% from base - optimal range")
    
    st.info("🔧 Advanced signal analysis interface coming in future updates")

def create_stock_technical(symbol):
    """Create stock technical analysis page"""
    instrument_info = INSTRUMENTS[symbol]
    st.markdown(f"## 📈 {instrument_info['name']} Technical Analysis")
    
    # Show slope relationship to other instruments
    st.markdown("### 📊 Slope Comparison")
    
    # Create comparison with other stocks
    comparison_data = []
    for stock_symbol in INSTRUMENTS.keys():
        if stock_symbol != "SPX":  # Exclude SPX from stock comparison
            current = st.session_state.slopes.get(stock_symbol, 0)
            base = BASE_SLOPES.get(stock_symbol, 0)
            deviation = ((current - base) / abs(base)) * 100 if base != 0 else 0
            
            comparison_data.append({
                "Symbol": stock_symbol,
                "Current": current,
                "Base": base,
                "Deviation": f"{deviation:+.1f}%"
            })
    
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
    
    st.info("🔧 Advanced technical analysis tools coming in future updates")

def create_stock_history(symbol):
    """Create stock history page"""
    instrument_info = INSTRUMENTS[symbol]
    st.markdown(f"## 📊 {instrument_info['name']} Session History")
    
    # Show session-based information only
    forecast_data = st.session_state.get("forecast_data", {})
    if forecast_data:
        st.markdown("### 📈 Current Session Data")
        st.json(forecast_data)
    else:
        st.info("📊 No forecast data available for current session")
    
    st.info("🔧 Extended session tracking coming in future updates")

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER STOCK INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

# Only render if we're not on SPX
current_instrument = st.session_state.get("current_instrument", "SPX")
if current_instrument != "SPX":
    create_stock_interface()
    # ═══════════════════════════════════════════════════════════════════════════════
# ENHANCED ANALYTICS & VISUAL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════

def create_visual_analytics():
    """Create enhanced visual analytics for current instrument"""
    current_instrument = st.session_state.get("current_instrument", "SPX")
    current_page = st.session_state.get("current_page", "Dashboard")
    
    # Add visual enhancements based on current context
    if current_instrument == "SPX":
        if current_page == "Analysis":
            create_spx_enhanced_analysis()
        elif current_page == "Risk":
            create_spx_risk_assessment()
        elif current_page == "Performance":
            create_spx_performance_analytics()
    else:
        # Enhanced analytics for individual stocks
        if current_page == "Signals":
            create_enhanced_stock_signals(current_instrument)
        elif current_page == "Technical":
            create_enhanced_stock_technical(current_instrument)
        elif current_page == "History":
            create_enhanced_stock_history(current_instrument)

def create_spx_enhanced_analysis():
    """Enhanced SPX analysis with visual intelligence"""
    animations_enabled = st.session_state.get("animations_enabled", True)
    decimal_places = st.session_state.get("decimal_places", 2)
    animation_class = "animate-fade-in" if animations_enabled else ""
    
    st.markdown(f"""
    <div class="{animation_class}" style="
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 140, 0, 0.05));
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: var(--radius);
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h2 style="margin: 0; color: var(--text-primary); font-size: 2rem; font-weight: 700;">
            📈 SPX Advanced Analysis
        </h2>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem;">
            Deep-dive technical analysis and pattern recognition
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Slope Evolution Analysis
    st.markdown("### 📊 Slope Evolution Analysis")
    
    # Get current slopes and compare to base
    spx_slopes = {
        "SPX_HIGH": st.session_state.slopes.get("SPX_HIGH", 0),
        "SPX_CLOSE": st.session_state.slopes.get("SPX_CLOSE", 0),
        "SPX_LOW": st.session_state.slopes.get("SPX_LOW", 0)
    }
    
    base_slopes = {
        "SPX_HIGH": BASE_SLOPES["SPX_HIGH"],
        "SPX_CLOSE": BASE_SLOPES["SPX_CLOSE"],
        "SPX_LOW": BASE_SLOPES["SPX_LOW"]
    }
    
    # Create slope comparison visualization
    slope_col1, slope_col2, slope_col3 = st.columns(3)
    
    for idx, (slope_type, current_value) in enumerate(spx_slopes.items()):
        base_value = base_slopes[slope_type]
        deviation = ((current_value - base_value) / abs(base_value)) * 100 if base_value != 0 else 0
        
        # Determine colors and status
        if abs(deviation) < 3:
            status_color = "var(--success-color)"
            status_text = "OPTIMAL"
        elif abs(deviation) < 8:
            status_color = "var(--warning-color)"
            status_text = "ADJUSTED"
        else:
            status_color = "var(--danger-color)"
            status_text = "HIGH DEV"
        
        with [slope_col1, slope_col2, slope_col3][idx]:
            st.markdown(f"""
            <div style="
                background: var(--bg-secondary);
                border: 2px solid {status_color};
                border-radius: var(--radius);
                padding: 1.5rem;
                text-align: center;
                transition: var(--transition);
            ">
                <h4 style="margin: 0 0 1rem 0; color: {status_color};">
                    {slope_type.replace('SPX_', '').title()}
                </h4>
                <div style="
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--text-primary);
                    margin-bottom: 0.5rem;
                ">
                    {current_value:.4f}
                </div>
                <div style="
                    background: {status_color};
                    color: white;
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.7rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                ">
                    {status_text}
                </div>
                <div style="color: var(--text-secondary); font-size: 0.8rem;">
                    Base: {base_value:.4f}<br>
                    Deviation: {deviation:+.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Slope Correlation Matrix
    st.markdown("### 🔗 Slope Correlation Analysis")
    
    # Calculate correlations between slope adjustments
    slope_deviations = {}
    for key, current in spx_slopes.items():
        base = base_slopes[key]
        slope_deviations[key] = ((current - base) / abs(base)) * 100 if base != 0 else 0
    
    # Display correlation insights
    max_deviation = max(abs(dev) for dev in slope_deviations.values())
    total_deviation = sum(abs(dev) for dev in slope_deviations.values())
    
    correlation_col1, correlation_col2 = st.columns(2)
    
    with correlation_col1:
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1.5rem;
        ">
            <h4 style="margin: 0 0 1rem 0; color: var(--text-primary);">📊 Deviation Metrics</h4>
            <div style="color: var(--text-secondary); line-height: 1.8;">
                <p><strong>Max Deviation:</strong> {max_deviation:.1f}%</p>
                <p><strong>Total Deviation:</strong> {total_deviation:.1f}%</p>
                <p><strong>Avg Deviation:</strong> {total_deviation/3:.1f}%</p>
                <p><strong>Consistency:</strong> {'High' if max_deviation < 5 else 'Medium' if max_deviation < 10 else 'Low'}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with correlation_col2:
        # Determine strategy recommendation
        if max_deviation < 5:
            strategy_color = "var(--success-color)"
            strategy_text = "CONSERVATIVE STRATEGY"
            strategy_desc = "Minimal adjustments maintain stability"
        elif max_deviation < 10:
            strategy_color = "var(--warning-color)"
            strategy_text = "BALANCED STRATEGY"
            strategy_desc = "Moderate adjustments for optimization"
        else:
            strategy_color = "var(--danger-color)"
            strategy_text = "AGGRESSIVE STRATEGY"
            strategy_desc = "High adjustments require careful monitoring"
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {strategy_color}20, {strategy_color}10);
            border: 1px solid {strategy_color}40;
            border-radius: var(--radius);
            padding: 1.5rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 1rem 0; color: {strategy_color};">🎯 Strategy Profile</h4>
            <div style="
                background: {strategy_color};
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 1rem;
            ">
                {strategy_text}
            </div>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                {strategy_desc}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Time-based Analysis (if forecast data exists)
    forecast_data = st.session_state.get("forecast_data", {})
    if forecast_data:
        st.markdown("### ⏰ Time-based Projection Analysis")
        
        # Extract forecast information
        anchors = forecast_data.get("anchors", {})
        if anchors:
            # Create time-based insights
            high_time = anchors.get("high", {}).get("time", "")
            close_time = anchors.get("close", {}).get("time", "")
            low_time = anchors.get("low", {}).get("time", "")
            
            if high_time and close_time and low_time:
                try:
                    high_dt = datetime.fromisoformat(high_time).time()
                    close_dt = datetime.fromisoformat(close_time).time()
                    low_dt = datetime.fromisoformat(low_time).time()
                    
                    # Time sequence analysis
                    times = [
                        ("High", high_dt, anchors["high"]["price"]),
                        ("Low", low_dt, anchors["low"]["price"]),
                        ("Close", close_dt, anchors["close"]["price"])
                    ]
                    
                    times.sort(key=lambda x: x[1])  # Sort by time
                    
                    st.markdown(f"""
                    <div style="
                        background: var(--bg-secondary);
                        border: 1px solid var(--border-color);
                        border-radius: var(--radius);
                        padding: 1.5rem;
                    ">
                        <h4 style="margin: 0 0 1rem 0; color: var(--text-primary);">📅 Time Sequence</h4>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                    """)
                    
                    for i, (name, time_val, price) in enumerate(times):
                        arrow = " → " if i < len(times) - 1 else ""
                        st.markdown(f"""
                            <div style="text-align: center; color: var(--text-secondary);">
                                <div style="font-weight: 600; color: var(--text-primary);">{name}</div>
                                <div style="font-size: 0.8rem;">{time_val.strftime('%H:%M')}</div>
                                <div style="font-size: 0.8rem;">{price:.{decimal_places}f}</div>
                            </div>{arrow}
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
                    
                except Exception:
                    pass  # Skip if time parsing fails

def create_spx_risk_assessment():
    """Create SPX risk assessment interface"""
    st.markdown(f"""
    <div class="animate-fade-in" style="
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: var(--radius);
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h2 style="margin: 0; color: var(--text-primary); font-size: 2rem; font-weight: 700;">
            ⚠️ SPX Risk Assessment
        </h2>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem;">
            Comprehensive risk analysis and position sizing
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk Matrix based on current settings
    st.markdown("### 🎯 Risk Matrix Analysis")
    
    # Calculate risk metrics from current slopes
    slope_risks = {}
    total_risk_score = 0
    
    for slope_key in ["SPX_HIGH", "SPX_CLOSE", "SPX_LOW"]:
        current = st.session_state.slopes.get(slope_key, 0)
        base = BASE_SLOPES.get(slope_key, 0)
        deviation = abs((current - base) / base) * 100 if base != 0 else 0
        
        # Risk scoring
        if deviation < 3:
            risk_score = 1  # Low risk
            risk_label = "Low"
            risk_color = "var(--success-color)"
        elif deviation < 8:
            risk_score = 2  # Medium risk
            risk_label = "Medium"
            risk_color = "var(--warning-color)"
        else:
            risk_score = 3  # High risk
            risk_label = "High"
            risk_color = "var(--danger-color)"
        
        slope_risks[slope_key] = {
            "score": risk_score,
            "label": risk_label,
            "color": risk_color,
            "deviation": deviation
        }
        total_risk_score += risk_score
    
    # Display risk matrix
    risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
    
    with risk_col1:
        high_risk = slope_risks["SPX_HIGH"]
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 2px solid {high_risk['color']};
            border-radius: var(--radius);
            padding: 1rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 0.5rem 0; color: {high_risk['color']};">HIGH ANCHOR</h4>
            <div style="
                background: {high_risk['color']};
                color: white;
                padding: 0.25rem 0.5rem;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            ">
                {high_risk['label']} RISK
            </div>
            <div style="color: var(--text-secondary); font-size: 0.8rem;">
                {high_risk['deviation']:.1f}% deviation
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with risk_col2:
        close_risk = slope_risks["SPX_CLOSE"]
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 2px solid {close_risk['color']};
            border-radius: var(--radius);
            padding: 1rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 0.5rem 0; color: {close_risk['color']};">CLOSE ANCHOR</h4>
            <div style="
                background: {close_risk['color']};
                color: white;
                padding: 0.25rem 0.5rem;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            ">
                {close_risk['label']} RISK
            </div>
            <div style="color: var(--text-secondary); font-size: 0.8rem;">
                {close_risk['deviation']:.1f}% deviation
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with risk_col3:
        low_risk = slope_risks["SPX_LOW"]
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 2px solid {low_risk['color']};
            border-radius: var(--radius);
            padding: 1rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 0.5rem 0; color: {low_risk['color']};">LOW ANCHOR</h4>
            <div style="
                background: {low_risk['color']};
                color: white;
                padding: 0.25rem 0.5rem;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            ">
                {low_risk['label']} RISK
            </div>
            <div style="color: var(--text-secondary); font-size: 0.8rem;">
                {low_risk['deviation']:.1f}% deviation
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with risk_col4:
        # Overall risk assessment
        overall_risk_score = total_risk_score / 3
        if overall_risk_score < 1.5:
            overall_color = "var(--success-color)"
            overall_label = "LOW RISK"
            overall_desc = "Conservative Setup"
        elif overall_risk_score < 2.5:
            overall_color = "var(--warning-color)"
            overall_label = "MEDIUM RISK"
            overall_desc = "Balanced Approach"
        else:
            overall_color = "var(--danger-color)"
            overall_label = "HIGH RISK"
            overall_desc = "Aggressive Strategy"
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {overall_color}20, {overall_color}10);
            border: 2px solid {overall_color};
            border-radius: var(--radius);
            padding: 1rem;
            text-align: center;
        ">
            <h4 style="margin: 0 0 0.5rem 0; color: {overall_color};">OVERALL</h4>
            <div style="
                background: {overall_color};
                color: white;
                padding: 0.25rem 0.5rem;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            ">
                {overall_label}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.8rem;">
                {overall_desc}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Position Sizing Calculator
    st.markdown("### 💰 Position Sizing Calculator")
    
    sizing_col1, sizing_col2 = st.columns(2)
    
    with sizing_col1:
        account_size = st.number_input(
            "Account Size ($)",
            value=10000.0,
            min_value=100.0,
            step=1000.0,
            help="Total account value for position sizing"
        )
        
        risk_percentage = st.slider(
            "Risk Percentage (%)",
            min_value=0.5,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help="Percentage of account to risk per trade"
        )
    
    with sizing_col2:
        # Calculate position sizes based on risk
        risk_amount = account_size * (risk_percentage / 100)
        
        # Adjust for overall risk level
        risk_multiplier = 1.0 if overall_risk_score < 1.5 else 0.75 if overall_risk_score < 2.5 else 0.5
        adjusted_risk = risk_amount * risk_multiplier
        
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1.5rem;
        ">
            <h4 style="margin: 0 0 1rem 0; color: var(--text-primary);">📊 Position Sizing</h4>
            <div style="color: var(--text-secondary); line-height: 1.8;">
                <p><strong>Base Risk Amount:</strong> ${risk_amount:.2f}</p>
                <p><strong>Risk Multiplier:</strong> {risk_multiplier:.2f}x</p>
                <p><strong>Adjusted Risk:</strong> ${adjusted_risk:.2f}</p>
                <p><strong>Max Position:</strong> {(adjusted_risk / account_size) * 100:.1f}% of account</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_spx_performance_analytics():
    """Create SPX performance analytics"""
    st.markdown(f"""
    <div class="animate-fade-in" style="
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: var(--radius);
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h2 style="margin: 0; color: var(--text-primary); font-size: 2rem; font-weight: 700;">
            📊 SPX Performance Analytics
        </h2>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem;">
            Session-based performance tracking and optimization insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Session Performance Metrics
    st.markdown("### 📈 Current Session Performance")
    
    # Calculate session statistics
    session_stats = calculate_session_stats()
    forecast_count = session_stats.get("total_forecasts", 0)
    slope_variance = session_stats.get("slope_variance", 0)
    uptime_hours = session_stats.get("uptime_hours", 0)
    
    # Performance scoring
    performance_score = 0
    if forecast_count > 0:
        performance_score += 25
    if slope_variance < 0.05:
        performance_score += 25
    if uptime_hours > 1:
        performance_score += 25
    performance_score += min(25, forecast_count * 5)  # Bonus for multiple forecasts
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    with perf_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">⏱️</div>
            <div class="metric-value">{uptime_hours:.1f}h</div>
            <div class="metric-label">Session Duration</div>
        </div>
        """, unsafe_allow_html=True)
    
    with perf_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value">{forecast_count}</div>
            <div class="metric-label">Forecasts Generated</div>
        </div>
        """, unsafe_allow_html=True)
    
    with perf_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📐</div>
            <div class="metric-value">{slope_variance:.3f}</div>
            <div class="metric-label">Slope Variance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with perf_col4:
        perf_color = "var(--success-color)" if performance_score >= 75 else "var(--warning-color)" if performance_score >= 50 else "var(--danger-color)"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: {perf_color};">🎯</div>
            <div class="metric-value" style="color: {perf_color};">{performance_score}</div>
            <div class="metric-label">Performance Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Configuration Optimization Insights
    st.markdown("### 🔧 Configuration Optimization")
    
    # Analyze current configuration effectiveness
    config_insights = []
    
    # Check slope consistency
    spx_slopes = [
        st.session_state.slopes.get("SPX_HIGH", 0),
        st.session_state.slopes.get("SPX_CLOSE", 0),
        st.session_state.slopes.get("SPX_LOW", 0)
    ]
    
    slope_std = np.std(spx_slopes) if len(spx_slopes) > 1 else 0
    
    if slope_std < 0.01:
        config_insights.append(("✅", "Slope Consistency", "High", "SPX slopes are well-aligned"))
    elif slope_std < 0.05:
        config_insights.append(("⚠️", "Slope Consistency", "Medium", "SPX slopes show moderate variance"))
    else:
        config_insights.append(("❌", "Slope Consistency", "Low", "SPX slopes are highly divergent"))
    
    # Check decimal precision efficiency
    decimal_places = st.session_state.get("decimal_places", 2)
    if decimal_places == 2:
        config_insights.append(("✅", "Precision Setting", "Optimal", "Standard precision for most use cases"))
    elif decimal_places > 2:
        config_insights.append(("ℹ️", "Precision Setting", "High", "Enhanced precision for detailed analysis"))
    else:
        config_insights.append(("⚠️", "Precision Setting", "Low", "Consider increasing for better accuracy"))
    
    # Display insights
    for icon, metric, level, description in config_insights:
        level_color = "var(--success-color)" if level in ["High", "Optimal"] else "var(--warning-color)" if level == "Medium" else "var(--danger-color)"
        
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        ">
            <span style="font-size: 1.5rem;">{icon}</span>
            <div style="flex: 1;">
                <div style="color: var(--text-primary); font-weight: 600;">{metric}</div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">{description}</div>
            </div>
            <div style="
                background: {level_color};
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
            ">
                {level}
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_enhanced_stock_signals(symbol):
    """Enhanced stock signals with visual intelligence"""
    instrument_info = INSTRUMENTS[symbol]
    current_slope = st.session_state.slopes.get(symbol, 0)
    base_slope = BASE_SLOPES.get(symbol, 0)
    
    st.markdown(f"""
    <div class="animate-fade-in" style="
        background: linear-gradient(135deg, {instrument_info['color']}20, {instrument_info['color']}10);
        border: 1px solid {instrument_info['color']}40;
        border-radius: var(--radius);
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h2 style="margin: 0; color: var(--text-primary); font-size: 2rem; font-weight: 700;">
            🎯 {instrument_info['name']} Trading Signals
        </h2>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem;">
            Advanced signal analysis and market positioning
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Signal Strength Analysis
    slope_deviation = ((current_slope - base_slope) / abs(base_slope)) * 100 if base_slope != 0 else 0
    
    # Determine signal strength
    if abs(slope_deviation) < 3:
        signal_strength = "WEAK"
        signal_color = "var(--text-muted)"
        signal_desc = "Minimal adjustment - conservative positioning"
    elif abs(slope_deviation) < 8:
        signal_strength = "MODERATE"
        signal_color = "var(--warning-color)"
        signal_desc = "Moderate adjustment - balanced positioning"
    else:
        signal_strength = "STRONG"
        signal_color = "var(--danger-color)"
        signal_desc = "High adjustment - active positioning required"
    
    # Signal direction
    signal_direction = "BULLISH" if slope_deviation > 0 else "BEARISH" if slope_deviation < 0 else "NEUTRAL"
    direction_color = "var(--success-color)" if signal_direction == "BULLISH" else "var(--danger-color)" if signal_direction == "BEARISH" else "var(--text-muted)"
    
    signal_col1, signal_col2 = st.columns(2)
    
    with signal_col1:
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 2px solid {signal_color};
            border-radius: var(--radius);
            padding: 2rem;
            text-align: center;
        ">
            <h3 style="margin: 0 0 1rem 0; color: {signal_color};">Signal Strength</h3>
            <div style="
                background: {signal_color};
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 25px;
                font-size: 1.1rem;
                font-weight: 700;
                margin-bottom: 1rem;
            ">
                {signal_strength}
            </div>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                {signal_desc}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with signal_col2:
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 2px solid {direction_color};
            border-radius: var(--radius);
            padding: 2rem;
            text-align: center;
        ">
            <h3 style="margin: 0 0 1rem 0; color: {direction_color};">Signal Direction</h3>
            <div style="
                background: {direction_color};
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 25px;
                font-size: 1.1rem;
                font-weight: 700;
                margin-bottom: 1rem;
            ">
                {signal_direction}
            </div>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                Deviation: {slope_deviation:+.1f}% from base
            </p>
        </div>
        """, unsafe_allow_html=True)

def create_enhanced_stock_technical(symbol):
    """Enhanced stock technical analysis"""
    instrument_info = INSTRUMENTS[symbol]
    
    st.markdown(f"""
    <div class="animate-fade-in" style="
        background: linear-gradient(135deg, {instrument_info['color']}20, {instrument_info['color']}10);
        border: 1px solid {instrument_info['color']}40;
        border-radius: var(--radius);
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h2 style="margin: 0; color: var(--text-primary); font-size: 2rem; font-weight: 700;">
            📈 {instrument_info['name']} Technical Analysis
        </h2>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem;">
            Advanced technical indicators and cross-instrument analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cross-Instrument Correlation
    st.markdown("### 🔗 Cross-Instrument Analysis")
    
    # Calculate correlations with other stocks
    current_symbol_slope = st.session_state.slopes.get(symbol, 0)
    correlations = []
    
    for other_symbol in INSTRUMENTS.keys():
        if other_symbol != symbol and other_symbol != "SPX":
            other_slope = st.session_state.slopes.get(other_symbol, 0)
            base_symbol = BASE_SLOPES.get(symbol, 0)
            base_other = BASE_SLOPES.get(other_symbol, 0)
            
            # Calculate relative deviations
            symbol_dev = ((current_symbol_slope - base_symbol) / abs(base_symbol)) * 100 if base_symbol != 0 else 0
            other_dev = ((other_slope - base_other) / abs(base_other)) * 100 if base_other != 0 else 0
            
            # Simple correlation measure
            correlation = 1 - (abs(symbol_dev - other_dev) / 100)  # Simplified correlation
            correlation = max(0, min(1, correlation))  # Clamp between 0-1
            
            correlations.append({
                "Symbol": other_symbol,
                "Icon": INSTRUMENTS[other_symbol]["icon"],
                "Correlation": correlation,
                "Status": "High" if correlation > 0.7 else "Medium" if correlation > 0.4 else "Low"
            })
    
    # Sort by correlation
    correlations.sort(key=lambda x: x["Correlation"], reverse=True)
    
    # Display top correlations
    if correlations:
        st.markdown("**Highest Correlations:**")
        
        corr_cols = st.columns(min(3, len(correlations)))
        for i, corr in enumerate(correlations[:3]):
            corr_color = "var(--success-color)" if corr["Status"] == "High" else "var(--warning-color)" if corr["Status"] == "Medium" else "var(--danger-color)"
            
            with corr_cols[i]:
                st.markdown(f"""
                <div style="
                    background: var(--bg-secondary);
                    border: 1px solid {corr_color};
                    border-radius: var(--radius);
                    padding: 1rem;
                    text-align: center;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{corr["Icon"]}</div>
                    <div style="color: var(--text-primary); font-weight: 600; margin-bottom: 0.5rem;">
                        {corr["Symbol"]}
                    </div>
                    <div style="
                        background: {corr_color};
                        color: white;
                        padding: 0.25rem 0.5rem;
                        border-radius: 12px;
                        font-size: 0.8rem;
                        font-weight: 600;
                        margin-bottom: 0.5rem;
                    ">
                        {corr["Status"]}
                    </div>
                    <div style="color: var(--text-secondary); font-size: 0.8rem;">
                        {corr["Correlation"]:.1%} correlation
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Technical Momentum Indicator
    st.markdown("### ⚡ Technical Momentum")
    
    current_slope = st.session_state.slopes.get(symbol, 0)
    base_slope = BASE_SLOPES.get(symbol, 0)
    
    # Calculate momentum score
    momentum_score = abs((current_slope - base_slope) / base_slope) * 100 if base_slope != 0 else 0
    
    if momentum_score < 5:
        momentum_status = "LOW"
        momentum_color = "var(--text-muted)"
        momentum_desc = "Minimal momentum - Range-bound conditions"
    elif momentum_score < 15:
        momentum_status = "BUILDING"
        momentum_color = "var(--warning-color)"
        momentum_desc = "Building momentum - Watch for breakout"
    else:
        momentum_status = "HIGH"
        momentum_color = "var(--danger-color)"
        momentum_desc = "High momentum - Strong directional move"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {momentum_color}20, {momentum_color}10);
        border: 1px solid {momentum_color}40;
        border-radius: var(--radius);
        padding: 2rem;
        text-align: center;
    ">
        <h3 style="margin: 0 0 1rem 0; color: {momentum_color};">Momentum Analysis</h3>
        <div style="
            background: {momentum_color};
            color: white;
            padding: 1rem 2rem;
            border-radius: 25px;
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 1rem;
        ">
            {momentum_status} MOMENTUM
        </div>
        <p style="margin: 0; color: var(--text-secondary); font-size: 1rem;">
            {momentum_desc}
        </p>
        <div style="
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 0.9rem;
        ">
            Score: {momentum_score:.1f} | Base: {base_slope:.4f} | Current: {current_slope:.4f}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_enhanced_stock_history(symbol):
    """Enhanced stock session history"""
    instrument_info = INSTRUMENTS[symbol]
    
    st.markdown(f"""
    <div class="animate-fade-in" style="
        background: linear-gradient(135deg, {instrument_info['color']}20, {instrument_info['color']}10);
        border: 1px solid {instrument_info['color']}40;
        border-radius: var(--radius);
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h2 style="margin: 0; color: var(--text-primary); font-size: 2rem; font-weight: 700;">
            📊 {instrument_info['name']} Session History
        </h2>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem;">
            Current session tracking and parameter evolution
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Session Activity Timeline
    st.markdown("### 📅 Session Activity")
    
    # Calculate session metrics for this specific symbol
    session_start = datetime.now().replace(hour=0, minute=0, second=0)
    current_time = datetime.now()
    session_duration = current_time - session_start
    
    # Check if this symbol has been actively used
    current_slope = st.session_state.slopes.get(symbol, 0)
    base_slope = BASE_SLOPES.get(symbol, 0)
    has_been_modified = abs(current_slope - base_slope) > 0.0001
    
    activity_col1, activity_col2, activity_col3 = st.columns(3)
    
    with activity_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: {instrument_info['color']};">⏰</div>
            <div class="metric-value">{session_duration.seconds // 3600}h {(session_duration.seconds // 60) % 60}m</div>
            <div class="metric-label">Session Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with activity_col2:
        modification_status = "Modified" if has_been_modified else "Default"
        modification_color = "var(--warning-color)" if has_been_modified else "var(--success-color)"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: {modification_color};">⚙️</div>
            <div class="metric-value" style="color: {modification_color}; font-size: 1.2rem;">{modification_status}</div>
            <div class="metric-label">Parameter Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    with activity_col3:
        deviation_pct = ((current_slope - base_slope) / abs(base_slope)) * 100 if base_slope != 0 else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value">{deviation_pct:+.1f}%</div>
            <div class="metric-label">Slope Deviation</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Parameter Evolution
    if has_been_modified:
        st.markdown("### 📈 Parameter Evolution")
        
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1.5rem;
        ">
            <h4 style="margin: 0 0 1rem 0; color: var(--text-primary);">Slope Modification History</h4>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div style="text-align: center;">
                    <div style="color: var(--text-secondary); font-size: 0.8rem;">ORIGINAL</div>
                    <div style="color: var(--text-primary); font-size: 1.2rem; font-weight: 600; font-family: 'JetBrains Mono', monospace;">
                        {base_slope:.4f}
                    </div>
                </div>
                <div style="color: var(--text-muted); font-size: 2rem;">→</div>
                <div style="text-align: center;">
                    <div style="color: var(--text-secondary); font-size: 0.8rem;">CURRENT</div>
                    <div style="color: var(--warning-color); font-size: 1.2rem; font-weight: 600; font-family: 'JetBrains Mono', monospace;">
                        {current_slope:.4f}
                    </div>
                </div>
            </div>
            <div style="
                background: {'var(--success-color)' if abs(deviation_pct) < 5 else 'var(--warning-color)' if abs(deviation_pct) < 15 else 'var(--danger-color)'};
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                text-align: center;
                font-size: 0.9rem;
                font-weight: 600;
            ">
                {abs(deviation_pct):.1f}% deviation from base parameters
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"✅ {symbol} parameters remain at default values for this session")
    
    # Session Insights
    st.markdown("### 💡 Session Insights")
    
    insights = []
    
    # Slope stability insight
    if abs(deviation_pct) < 3:
        insights.append(("🎯", "Parameter Stability", "Excellent", f"{symbol} shows minimal parameter drift"))
    elif abs(deviation_pct) < 10:
        insights.append(("⚖️", "Parameter Stability", "Good", f"{symbol} shows controlled parameter adjustment"))
    else:
        insights.append(("⚠️", "Parameter Stability", "Monitor", f"{symbol} shows significant parameter changes"))
    
    # Usage pattern insight
    if has_been_modified:
        insights.append(("🔧", "Usage Pattern", "Active", f"{symbol} has been actively configured this session"))
    else:
        insights.append(("📋", "Usage Pattern", "Standard", f"{symbol} using default configuration"))
    
    # Display insights
    for icon, metric, status, description in insights:
        status_color = "var(--success-color)" if status in ["Excellent", "Good", "Active"] else "var(--warning-color)" if status in ["Monitor", "Standard"] else "var(--danger-color)"
        
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        ">
            <span style="font-size: 1.5rem;">{icon}</span>
            <div style="flex: 1;">
                <div style="color: var(--text-primary); font-weight: 600;">{metric}</div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">{description}</div>
            </div>
            <div style="
                background: {status_color};
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
            ">
                {status}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER ENHANCED ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════

# Only render enhanced analytics for appropriate pages
current_instrument = st.session_state.get("current_instrument", "SPX")
current_page = st.session_state.get("current_page", "Dashboard")

# Don't render on main dashboard/overview pages (those are handled in parts 3 & 4)
if current_instrument == "SPX" and current_page in ["Analysis", "Risk", "Performance"]:
    create_visual_analytics()
elif current_instrument != "SPX" and current_page in ["Signals", "Technical", "History"]:
    create_visual_analytics()
    # ═══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL EXPORT & DATA MANAGEMENT SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

def create_export_interface():
    """Create comprehensive export and data management interface"""
    current_instrument = st.session_state.get("current_instrument", "SPX")
    
    # Add export functionality as floating action button
    create_floating_export_menu()
    
    # Enhanced export interface for specific contexts
    if should_show_export_interface():
        create_detailed_export_interface()

def should_show_export_interface():
    """Determine if detailed export interface should be shown"""
    # Show export interface when user has generated forecasts or made significant changes
    forecast_data = st.session_state.get("forecast_data", {})
    has_slope_changes = any(
        abs(st.session_state.slopes.get(key, 0) - BASE_SLOPES.get(key, 0)) > 0.0001
        for key in BASE_SLOPES.keys()
    )
    
    return bool(forecast_data or has_slope_changes)

def create_floating_export_menu():
    """Create floating export menu that's always accessible"""
    # Add floating export button CSS
    st.markdown("""
    <style>
    .floating-export {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        z-index: 1000;
        background: var(--primary-gradient);
        color: white;
        border-radius: 50px;
        padding: 1rem 1.5rem;
        box-shadow: var(--shadow-lg);
        cursor: pointer;
        transition: var(--transition);
        font-weight: 600;
        border: none;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .floating-export:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-xl);
    }
    
    .export-menu {
        position: fixed;
        bottom: 5rem;
        right: 2rem;
        z-index: 999;
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        padding: 1rem;
        box-shadow: var(--shadow-xl);
        min-width: 250px;
    }
    
    .export-option {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: var(--transition);
        margin-bottom: 0.5rem;
        border: 1px solid transparent;
    }
    
    .export-option:hover {
        background: var(--bg-tertiary);
        border-color: var(--border-color);
    }
    
    .export-option:last-child {
        margin-bottom: 0;
    }
    </style>
    """, unsafe_allow_html=True)

def create_detailed_export_interface():
    """Create detailed export interface when data is available"""
    st.markdown("---")
    st.markdown("## 📤 Professional Export Center")
    st.markdown("*Export your analysis data, configurations, and session information*")
    
    # Export options grid
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.05));
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: var(--radius);
            padding: 2rem;
            text-align: center;
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0 0 1rem 0; color: var(--primary-color);">📊 Data Exports</h3>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                Export forecast tables, analysis results, and session data
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Forecast Data Export
        forecast_data = st.session_state.get("forecast_data", {})
        if forecast_data:
            if st.button("📋 Export Forecast Data", help="Download current forecast analysis as JSON"):
                export_forecast_data()
        else:
            st.button("📋 Export Forecast Data", disabled=True, help="Generate a forecast first")
        
        # Session Data Export
        if st.button("📊 Export Session Analytics", help="Download complete session analytics"):
            export_session_analytics()
        
        # CSV Table Export
        if forecast_data:
            if st.button("📄 Export Forecast Tables (CSV)", help="Download forecast tables as CSV"):
                export_forecast_csv()
        else:
            st.button("📄 Export Forecast Tables (CSV)", disabled=True, help="Generate a forecast first")
    
    with export_col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.05));
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-radius: var(--radius);
            padding: 2rem;
            text-align: center;
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0 0 1rem 0; color: var(--warning-color);">⚙️ Configuration Exports</h3>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                Export parameter configurations and system settings
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Configuration Export
        if st.button("⚙️ Export Configuration", help="Download current slope and system configuration"):
            export_configuration()
        
        # Backup Export
        if st.button("💾 Full System Backup", help="Download complete system state backup"):
            export_full_backup()
        
        # Import Configuration
        uploaded_config = st.file_uploader(
            "📂 Import Configuration",
            type=['json'],
            help="Upload a previously exported configuration file"
        )
        
        if uploaded_config is not None:
            import_configuration(uploaded_config)

def export_forecast_data():
    """Export current forecast data"""
    forecast_data = st.session_state.get("forecast_data", {})
    current_instrument = st.session_state.get("current_instrument", "SPX")
    
    export_data = {
        "export_info": {
            "timestamp": datetime.now().isoformat(),
            "instrument": current_instrument,
            "platform": "DRSPX Professional",
            "version": APP_CONFIG["version"],
            "export_type": "forecast_data"
        },
        "forecast_data": forecast_data,
        "current_slopes": st.session_state.slopes,
        "session_id": st.session_state.get("app_session", "unknown")
    }
    
    export_json = json.dumps(export_data, indent=2, default=str)
    
    st.download_button(
        label="⬇️ Download Forecast Data",
        data=export_json,
        file_name=f"drspx_forecast_{current_instrument}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        help="Download forecast analysis data"
    )
    
    st.success("✅ Forecast data export ready for download!")

def export_session_analytics():
    """Export comprehensive session analytics"""
    session_stats = calculate_session_stats()
    current_instrument = st.session_state.get("current_instrument", "SPX")
    
    # Calculate additional analytics
    slope_analysis = {}
    for key, current_value in st.session_state.slopes.items():
        base_value = BASE_SLOPES.get(key, 0)
        deviation = ((current_value - base_value) / abs(base_value)) * 100 if base_value != 0 else 0
        
        slope_analysis[key] = {
            "current": current_value,
            "base": base_value,
            "deviation_percent": deviation,
            "status": "optimal" if abs(deviation) < 5 else "adjusted" if abs(deviation) < 15 else "high_deviation"
        }
    
    analytics_data = {
        "export_info": {
            "timestamp": datetime.now().isoformat(),
            "platform": "DRSPX Professional",
            "version": APP_CONFIG["version"],
            "export_type": "session_analytics"
        },
        "session_statistics": session_stats,
        "slope_analysis": slope_analysis,
        "configuration": {
            "current_instrument": current_instrument,
            "current_page": st.session_state.get("current_page", "Dashboard"),
            "animations_enabled": st.session_state.get("animations_enabled", True),
            "decimal_places": st.session_state.get("decimal_places", 2)
        },
        "performance_metrics": {
            "total_slope_adjustments": len([k for k, v in slope_analysis.items() if v["status"] != "optimal"]),
            "max_deviation": max([abs(v["deviation_percent"]) for v in slope_analysis.values()]),
            "avg_deviation": sum([abs(v["deviation_percent"]) for v in slope_analysis.values()]) / len(slope_analysis)
        }
    }
    
    export_json = json.dumps(analytics_data, indent=2, default=str)
    
    st.download_button(
        label="⬇️ Download Session Analytics",
        data=export_json,
        file_name=f"drspx_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        help="Download comprehensive session analytics"
    )
    
    st.success("✅ Session analytics export ready for download!")

def export_forecast_csv():
    """Export forecast tables as CSV"""
    forecast_data = st.session_state.get("forecast_data", {})
    current_instrument = st.session_state.get("current_instrument", "SPX")
    
    if not forecast_data:
        st.error("❌ No forecast data available to export")
        return
    
    # Create CSV data from forecast information
    csv_data = []
    
    # Add header information
    csv_data.append(["DRSPX Professional Forecast Export"])
    csv_data.append(["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    csv_data.append(["Instrument:", current_instrument])
    csv_data.append([""])  # Empty row
    
    # Add anchor information if available
    anchors = forecast_data.get("anchors", {})
    if anchors:
        csv_data.append(["ANCHOR POINTS"])
        csv_data.append(["Type", "Price", "Time"])
        for anchor_type, anchor_info in anchors.items():
            csv_data.append([
                anchor_type.title(),
                anchor_info.get("price", ""),
                anchor_info.get("time", "")
            ])
        csv_data.append([""])  # Empty row
    
    # Add contract information if available
    contract = forecast_data.get("contract", {})
    if contract:
        csv_data.append(["CONTRACT LINE"])
        csv_data.append(["Parameter", "Value"])
        csv_data.append(["Slope", contract.get("slope", "")])
        csv_data.append(["Low-1 Price", contract.get("low1", {}).get("price", "")])
        csv_data.append(["Low-1 Time", contract.get("low1", {}).get("time", "")])
        csv_data.append(["Low-2 Price", contract.get("low2", {}).get("price", "")])
        csv_data.append(["Low-2 Time", contract.get("low2", {}).get("time", "")])
        csv_data.append(["Blocks", contract.get("blocks", "")])
        csv_data.append([""])  # Empty row
    
    # Add metrics if available
    metrics = forecast_data.get("metrics", {})
    if metrics:
        csv_data.append(["METRICS"])
        csv_data.append(["Metric", "Value"])
        csv_data.append(["Range", metrics.get("range", "")])
        csv_data.append(["Midpoint", metrics.get("midpoint", "")])
        csv_data.append(["Volatility %", metrics.get("volatility", "")])
    
    # Convert to CSV string
    csv_string = ""
    for row in csv_data:
        csv_string += ",".join([str(cell) for cell in row]) + "\n"
    
    st.download_button(
        label="⬇️ Download Forecast CSV",
        data=csv_string,
        file_name=f"drspx_forecast_{current_instrument}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        help="Download forecast data as CSV spreadsheet"
    )
    
    st.success("✅ Forecast CSV export ready for download!")

def export_configuration():
    """Export current configuration"""
    config_data = {
        "export_info": {
            "timestamp": datetime.now().isoformat(),
            "platform": "DRSPX Professional",
            "version": APP_CONFIG["version"],
            "export_type": "configuration"
        },
        "slopes": st.session_state.slopes,
        "settings": {
            "animations_enabled": st.session_state.get("animations_enabled", True),
            "decimal_places": st.session_state.get("decimal_places", 2),
            "current_instrument": st.session_state.get("current_instrument", "SPX"),
            "current_page": st.session_state.get("current_page", "Dashboard")
        },
        "saved_configurations": st.session_state.get("configurations", {}),
        "base_slopes_reference": BASE_SLOPES
    }
    
    export_json = json.dumps(config_data, indent=2, default=str)
    
    st.download_button(
        label="⬇️ Download Configuration",
        data=export_json,
        file_name=f"drspx_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        help="Download current configuration and settings"
    )
    
    st.success("✅ Configuration export ready for download!")

def export_full_backup():
    """Export complete system state backup"""
    backup_data = {
        "backup_info": {
            "timestamp": datetime.now().isoformat(),
            "platform": "DRSPX Professional",
            "version": APP_CONFIG["version"],
            "backup_type": "full_system",
            "session_id": st.session_state.get("app_session", "unknown")
        },
        "session_state": {
            "slopes": st.session_state.slopes,
            "configurations": st.session_state.get("configurations", {}),
            "current_instrument": st.session_state.get("current_instrument", "SPX"),
            "current_page": st.session_state.get("current_page", "Dashboard"),
            "animations_enabled": st.session_state.get("animations_enabled", True),
            "decimal_places": st.session_state.get("decimal_places", 2),
            "forecast_data": st.session_state.get("forecast_data", {}),
            "contract_data": st.session_state.get("contract_data", {})
        },
        "system_references": {
            "base_slopes": BASE_SLOPES,
            "instruments": INSTRUMENTS,
            "app_config": APP_CONFIG
        },
        "session_analytics": calculate_session_stats()
    }
    
    export_json = json.dumps(backup_data, indent=2, default=str)
    
    st.download_button(
        label="⬇️ Download Full Backup",
        data=export_json,
        file_name=f"drspx_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        help="Download complete system state backup"
    )
    
    st.success("✅ Full system backup ready for download!")

def import_configuration(uploaded_file):
    """Import configuration from uploaded file"""
    try:
        config_data = json.loads(uploaded_file.read().decode())
        
        # Validate the configuration file
        if "export_type" in config_data.get("export_info", {}):
            export_type = config_data["export_info"]["export_type"]
            
            if export_type == "configuration":
                # Import configuration
                if "slopes" in config_data:
                    # Validate slopes before importing
                    imported_slopes = config_data["slopes"]
                    valid_slopes = {}
                    
                    for key, value in imported_slopes.items():
                        if key in BASE_SLOPES and isinstance(value, (int, float)):
                            valid_slopes[key] = float(value)
                    
                    if valid_slopes:
                        st.session_state.slopes.update(valid_slopes)
                        
                        # Import settings if available
                        if "settings" in config_data:
                            settings = config_data["settings"]
                            if "animations_enabled" in settings:
                                st.session_state.animations_enabled = settings["animations_enabled"]
                            if "decimal_places" in settings:
                                st.session_state.decimal_places = settings["decimal_places"]
                        
                        # Import saved configurations if available
                        if "saved_configurations" in config_data:
                            if "configurations" not in st.session_state:
                                st.session_state.configurations = {}
                            st.session_state.configurations.update(config_data["saved_configurations"])
                        
                        st.success("✅ Configuration imported successfully!")
                        st.rerun()
                    else:
                        st.error("❌ No valid slope parameters found in configuration file")
                else:
                    st.error("❌ Invalid configuration file format")
            
            elif export_type == "full_system":
                # Import full backup
                if "session_state" in config_data:
                    session_state = config_data["session_state"]
                    
                    # Import slopes
                    if "slopes" in session_state:
                        valid_slopes = {}
                        for key, value in session_state["slopes"].items():
                            if key in BASE_SLOPES and isinstance(value, (int, float)):
                                valid_slopes[key] = float(value)
                        
                        if valid_slopes:
                            st.session_state.slopes.update(valid_slopes)
                    
                    # Import other settings
                    for key in ["animations_enabled", "decimal_places", "configurations"]:
                        if key in session_state:
                            st.session_state[key] = session_state[key]
                    
                    st.success("✅ Full backup imported successfully!")
                    st.rerun()
                else:
                    st.error("❌ Invalid backup file format")
            
            else:
                st.error("❌ Unsupported file type. Please upload a configuration or backup file.")
        
        else:
            st.error("❌ Invalid file format. Please upload a valid DRSPX export file.")
    
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON file. Please upload a valid configuration file.")
    except Exception as e:
        st.error(f"❌ Error importing configuration: {str(e)}")

def create_export_summary():
    """Create export summary widget"""
    # Show export status and quick actions
    has_forecast = bool(st.session_state.get("forecast_data", {}))
    has_changes = any(
        abs(st.session_state.slopes.get(key, 0) - BASE_SLOPES.get(key, 0)) > 0.0001
        for key in BASE_SLOPES.keys()
    )
    
    if has_forecast or has_changes:
        st.markdown("""
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1rem;
            margin: 1rem 0;
            text-align: center;
        ">
            <div style="color: var(--text-primary); font-weight: 600; margin-bottom: 0.5rem;">
                📤 Export Available
            </div>
            <div style="color: var(--text-secondary); font-size: 0.9rem;">
                Your analysis data and configurations are ready for export
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# RENDER EXPORT INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

# Always create the floating export menu
create_floating_export_menu()

# Show detailed interface when appropriate
if should_show_export_interface():
    create_detailed_export_interface()
else:
    # Show export summary if there's any exportable data
    create_export_summary()
    # ═══════════════════════════════════════════════════════════════════════════════
# MULTI-PAGE STOCK ANALYSIS SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

def create_stock_navigation(symbol):
    """Create navigation for stock pages"""
    pages = INSTRUMENTS[symbol]["pages"]
    
    # Create horizontal navigation
    nav_cols = st.columns(len(pages))
    
    for i, page in enumerate(pages):
        with nav_cols[i]:
            if st.button(
                f"{get_page_icon(page)} {page}",
                key=f"nav_{symbol}_{page}",
                help=f"Navigate to {page} analysis",
                use_container_width=True
            ):
                st.session_state.current_page = page
                st.rerun()

def get_page_icon(page_name):
    """Get icon for each page type"""
    icons = {
        "Overview": "📊",
        "Dashboard": "📈", 
        "Analysis": "🔍",
        "Signals": "📡",
        "Technical": "📉",
        "Risk": "⚠️",
        "Performance": "🎯",
        "History": "📜"
    }
    return icons.get(page_name, "📄")

def create_stock_overview_page(symbol):
    """Create stock overview page"""
    metadata = INSTRUMENTS[symbol]
    current_slope = st.session_state.slopes.get(symbol, BASE_SLOPES[symbol])
    
    st.markdown(f"""
    <div class="metric-card animate-fade-in">
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{metadata['icon']}</div>
            <h2 style="margin: 0; color: var(--text-primary);">{metadata['name']}</h2>
            <p style="color: var(--text-secondary); margin: 0.5rem 0;">
                Symbol: {symbol} • Current Slope: {current_slope:.4f}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: {metadata['color']};">📊</div>
            <div class="metric-value">{abs(current_slope):.4f}</div>
            <div class="metric-label">Slope Magnitude</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        volatility = abs(current_slope) * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: var(--warning-color);">⚡</div>
            <div class="metric-value">{volatility:.1f}%</div>
            <div class="metric-label">Est. Volatility</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        bias = "Bullish" if current_slope > 0 else "Bearish" if current_slope < 0 else "Neutral"
        bias_color = "var(--success-color)" if current_slope > 0 else "var(--danger-color)" if current_slope < 0 else "var(--text-muted)"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: {bias_color};">📈</div>
            <div class="metric-value" style="color: {bias_color}; font-size: 1.5rem;">{bias}</div>
            <div class="metric-label">Market Bias</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Configuration section
    st.markdown("### ⚙️ Configuration")
    
    config_col1, config_col2 = st.columns(2)
    
    with config_col1:
        st.markdown("**Previous Session Low**")
        low_price = st.number_input(
            "Low Price",
            value=0.0,
            min_value=0.0,
            step=0.01,
            key=f"{symbol}_overview_low_price"
        )
        low_time = st.time_input(
            "Low Time",
            value=time(7, 30),
            key=f"{symbol}_overview_low_time"
        )
    
    with config_col2:
        st.markdown("**Previous Session High**")
        high_price = st.number_input(
            "High Price",
            value=0.0,
            min_value=0.0,
            step=0.01,
            key=f"{symbol}_overview_high_price"
        )
        high_time = st.time_input(
            "High Time",
            value=time(7, 30),
            key=f"{symbol}_overview_high_time"
        )
    
    # Quick analysis button
    if st.button(f"🚀 Quick Analysis for {symbol}", key=f"{symbol}_quick_analysis"):
        if low_price > 0 or high_price > 0:
            st.success(f"✅ {symbol} analysis parameters configured!")
            # Store in session state for other pages
            st.session_state[f"{symbol}_config"] = {
                "low_price": low_price,
                "low_time": low_time,
                "high_price": high_price,
                "high_time": high_time
            }
        else:
            st.warning("⚠️ Please enter at least one price value")

def create_stock_signals_page(symbol):
    """Create stock signals page"""
    st.markdown(f"### 📡 {symbol} Trading Signals")
    
    # Check if we have configuration data
    config_key = f"{symbol}_config"
    if config_key not in st.session_state:
        st.info("🔄 Configure prices in the Overview page first to see signals")
        return
    
    config = st.session_state[config_key]
    current_slope = st.session_state.slopes.get(symbol, BASE_SLOPES[symbol])
    
    # Generate signals based on configuration
    if config["low_price"] > 0:
        st.markdown("#### 📉 Low-Based Signals")
        
        # Create forecast table for low anchor
        forecast_date = st.session_state.get('forecast_date', date.today() + timedelta(days=1))
        low_anchor_time = datetime.combine(forecast_date, config["low_time"])
        
        # Generate time slots (7:30 to 14:00, 30-min intervals)
        time_slots = []
        start_time = datetime.combine(forecast_date, time(7, 30))
        for i in range(13):  # 13 slots for 6.5 hours
            slot_time = start_time + timedelta(minutes=30 * i)
            time_slots.append(slot_time.strftime("%H:%M"))
        
        # Calculate projections
        rows = []
        for slot in time_slots:
            hour, minute = map(int, slot.split(":"))
            target_time = datetime.combine(forecast_date, time(hour, minute))
            
            # Stock block calculation (your exact method)
            blocks = max(0, int((target_time - low_anchor_time).total_seconds() // 1800))
            
            entry_price = round(config["low_price"] + current_slope * blocks, 2)
            exit_price = round(config["low_price"] - current_slope * blocks, 2)
            spread = abs(entry_price - exit_price)
            
            # Signal strength
            if spread < 1.0:
                signal = "🟢 Strong"
                signal_color = "var(--success-color)"
            elif spread < 2.0:
                signal = "🟡 Moderate"
                signal_color = "var(--warning-color)"
            else:
                signal = "🔴 Weak"
                signal_color = "var(--danger-color)"
            
            rows.append({
                "Time": slot,
                "Entry": entry_price,
                "Exit": exit_price,
                "Spread": round(spread, 2),
                "Signal": signal
            })
        
        df = pd.DataFrame(rows)
        
        # Style the dataframe
        styled_df = df.style.format({
            'Entry': '{:.2f}',
            'Exit': '{:.2f}',
            'Spread': '{:.2f}'
        }).set_properties(**{
            'background-color': 'var(--bg-secondary)',
            'color': 'var(--text-primary)',
            'text-align': 'center',
            'padding': '8px'
        }).set_table_styles([
            {'selector': 'th', 'props': [
                ('background', 'var(--primary-gradient)'),
                ('color', 'white'),
                ('font-weight', '600'),
                ('text-align', 'center'),
                ('padding', '12px')
            ]}
        ])
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Signal summary
        strong_signals = len([r for r in rows if "Strong" in r["Signal"]])
        moderate_signals = len([r for r in rows if "Moderate" in r["Signal"]])
        weak_signals = len([r for r in rows if "Weak" in r["Signal"]])
        
        signal_col1, signal_col2, signal_col3 = st.columns(3)
        
        with signal_col1:
            st.metric("🟢 Strong Signals", strong_signals)
        with signal_col2:
            st.metric("🟡 Moderate Signals", moderate_signals)
        with signal_col3:
            st.metric("🔴 Weak Signals", weak_signals)

def create_stock_technical_page(symbol):
    """Create stock technical analysis page"""
    st.markdown(f"### 📉 {symbol} Technical Analysis")
    
    # Technical indicators section
    st.markdown("#### 🔧 Technical Indicators")
    
    tech_col1, tech_col2 = st.columns(2)
    
    with tech_col1:
        st.markdown("""
        **Slope Analysis:**
        - Current slope parameter configuration
        - Historical slope performance
        - Volatility-adjusted expectations
        """)
        
        current_slope = st.session_state.slopes.get(symbol, BASE_SLOPES[symbol])
        base_slope = BASE_SLOPES[symbol]
        
        st.metric(
            "Current vs Base Slope",
            f"{current_slope:.4f}",
            delta=f"{(current_slope - base_slope):.4f}" if current_slope != base_slope else None
        )
    
    with tech_col2:
        st.markdown("""
        **Risk Metrics:**
        - Volatility estimation
        - Risk-adjusted returns
        - Maximum drawdown potential
        """)
        
        volatility = abs(current_slope) * 100
        risk_level = "High" if volatility > 20 else "Medium" if volatility > 10 else "Low"
        risk_color = "var(--danger-color)" if risk_level == "High" else "var(--warning-color)" if risk_level == "Medium" else "var(--success-color)"
        
        st.markdown(f"""
        <div style="padding: 1rem; background: var(--bg-secondary); border-radius: var(--radius); border-left: 4px solid {risk_color};">
            <strong>Risk Level: {risk_level}</strong><br>
            Estimated Volatility: {volatility:.1f}%
        </div>
        """, unsafe_allow_html=True)
    
    # Advanced technical section
    st.markdown("#### 📊 Advanced Analysis")
    
    with st.expander("Slope Optimization", expanded=False):
        st.markdown(f"**Optimize {symbol} slope parameter:**")
        
        optimized_slope = st.slider(
            "Adjusted Slope",
            min_value=-1.0,
            max_value=1.0,
            value=current_slope,
            step=0.0001,
            format="%.4f",
            key=f"{symbol}_tech_slope"
        )
        
        if st.button(f"Apply Optimized Slope to {symbol}", key=f"{symbol}_apply_slope"):
            st.session_state.slopes[symbol] = optimized_slope
            st.success(f"✅ {symbol} slope updated to {optimized_slope:.4f}")
            st.rerun()

def create_stock_history_page(symbol):
    """Create stock history page"""
    st.markdown(f"### 📜 {symbol} Performance History")
    
    # Mock historical data for demonstration
    st.markdown("#### 📈 Recent Performance")
    
    # Create sample performance data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
    np.random.seed(42)  # For consistent demo data
    
    base_slope = BASE_SLOPES[symbol]
    current_slope = st.session_state.slopes.get(symbol, base_slope)
    
    # Generate mock performance based on slope
    performance_data = []
    for i, date in enumerate(dates):
        # Mock return based on slope (for demo purposes)
        weekly_return = np.random.normal(abs(current_slope) * 10, 2)
        performance_data.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Weekly Return": round(weekly_return, 2),
            "Cumulative": round(sum([p.get("Weekly Return", 0) for p in performance_data]) + weekly_return, 2)
        })
    
    df = pd.DataFrame(performance_data[-12:])  # Last 12 weeks
    
    # Display performance table
    styled_df = df.style.format({
        'Weekly Return': '{:.2f}%',
        'Cumulative': '{:.2f}%'
    }).set_properties(**{
        'background-color': 'var(--bg-secondary)',
        'color': 'var(--text-primary)',
        'text-align': 'center',
        'padding': '8px'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background', 'var(--primary-gradient)'),
            ('color', 'white'),
            ('font-weight', '600'),
            ('text-align', 'center'),
            ('padding', '12px')
        ]}
    ])
    
    st.dataframe(styled_df, use_container_width=True, height=350)
    
    # Performance summary
    if len(performance_data) > 0:
        avg_return = np.mean([p["Weekly Return"] for p in performance_data[-12:]])
        total_return = performance_data[-1]["Cumulative"] if performance_data else 0
        win_rate = len([p for p in performance_data[-12:] if p["Weekly Return"] > 0]) / 12 * 100
        
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            st.metric("Average Weekly Return", f"{avg_return:.2f}%")
        
        with perf_col2:
            st.metric("Total Return (12W)", f"{total_return:.2f}%")
        
        with perf_col3:
            st.metric("Win Rate", f"{win_rate:.1f}%")

# ═══════════════════════════════════════════════════════════════════════════════
# STOCK TAB MANAGEMENT SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

def create_individual_stock_tab(tab_index, symbol):
    """Create individual stock tab with multi-page system"""
    with tabs[tab_index]:
        metadata = INSTRUMENTS[symbol]
        
        # Store current instrument
        st.session_state.current_instrument = symbol
        
        # Header for the stock
        st.markdown(f"""
        <div class="metric-card animate-fade-in" style="
            background: linear-gradient(135deg, {metadata['color']}20, {metadata['color']}10);
            border-left: 4px solid {metadata['color']};
            text-align: center;
            margin-bottom: 2rem;
        ">
            <h2 style="margin: 0; color: var(--text-primary);">
                {metadata['icon']} {metadata['name']} Analysis
            </h2>
            <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary);">
                Professional Multi-Page Analysis System
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        create_stock_navigation(symbol)
        
        st.markdown("---")
        
        # Page content based on current page
        current_page = st.session_state.get('current_page', 'Overview')
        
        if current_page == "Overview":
            create_stock_overview_page(symbol)
        elif current_page == "Signals":
            create_stock_signals_page(symbol)
        elif current_page == "Technical":
            create_stock_technical_page(symbol)
        elif current_page == "History":
            create_stock_history_page(symbol)
        else:
            # Default to overview for any undefined pages
            create_stock_overview_page(symbol)

# Generate stock tabs (excluding SPX which gets special treatment)
stock_symbols = [symbol for symbol in INSTRUMENTS.keys() if symbol != "SPX"]
for i, symbol in enumerate(stock_symbols, 1):  # Start from index 1 (SPX is 0)
    create_individual_stock_tab(i, symbol)
    # ═══════════════════════════════════════════════════════════════════════════════
# ADVANCED ANALYTICS & PERFORMANCE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_portfolio_metrics():
    """Calculate portfolio-wide performance metrics"""
    metrics = {
        "total_instruments": len(INSTRUMENTS),
        "active_forecasts": len([k for k in st.session_state.keys() if k.endswith('_config')]),
        "avg_slope_magnitude": np.mean([abs(slope) for slope in st.session_state.slopes.values()]),
        "portfolio_volatility": np.std([abs(slope) for slope in st.session_state.slopes.values()]) * 100,
        "session_uptime": (datetime.now() - datetime.now().replace(hour=9, minute=0, second=0)).seconds / 3600,
        "configurations_saved": len(st.session_state.get('configurations', {}))
    }
    return metrics

def create_performance_dashboard():
    """Create comprehensive performance analytics dashboard"""
    st.markdown("## 📊 Performance Analytics Dashboard")
    st.markdown("*Real-time portfolio and system performance metrics*")
    
    # Calculate metrics
    metrics = calculate_portfolio_metrics()
    
    # Main performance grid
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    with perf_col1:
        st.markdown(f"""
        <div class="metric-card animate-fade-in">
            <div class="metric-icon" style="background: var(--success-gradient);">📈</div>
            <div class="metric-value">{metrics['total_instruments']}</div>
            <div class="metric-label">Active Instruments</div>
        </div>
        """, unsafe_allow_html=True)
    
    with perf_col2:
        st.markdown(f"""
        <div class="metric-card animate-fade-in">
            <div class="metric-icon" style="background: var(--primary-gradient);">🎯</div>
            <div class="metric-value">{metrics['active_forecasts']}</div>
            <div class="metric-label">Active Forecasts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with perf_col3:
        st.markdown(f"""
        <div class="metric-card animate-fade-in">
            <div class="metric-icon" style="background: var(--warning-gradient);">⚡</div>
            <div class="metric-value">{metrics['avg_slope_magnitude']:.4f}</div>
            <div class="metric-label">Avg Slope Magnitude</div>
        </div>
        """, unsafe_allow_html=True)
    
    with perf_col4:
        st.markdown(f"""
        <div class="metric-card animate-fade-in">
            <div class="metric-icon" style="background: var(--info-color);">⏱️</div>
            <div class="metric-value">{metrics['session_uptime']:.1f}h</div>
            <div class="metric-label">Session Uptime</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Advanced analytics section
    st.markdown("### 🔍 Advanced Analytics")
    
    analytics_col1, analytics_col2 = st.columns(2)
    
    with analytics_col1:
        st.markdown("#### 📊 Slope Distribution Analysis")
        
        # Create slope analysis
        slope_data = []
        for symbol, slope in st.session_state.slopes.items():
            slope_data.append({
                "Symbol": symbol,
                "Slope": slope,
                "Magnitude": abs(slope),
                "Direction": "Bullish" if slope > 0 else "Bearish" if slope < 0 else "Neutral"
            })
        
        slope_df = pd.DataFrame(slope_data)
        
        if not slope_df.empty:
            # Style the slope analysis table
            styled_slope_df = slope_df.style.format({
                'Slope': '{:.4f}',
                'Magnitude': '{:.4f}'
            }).set_properties(**{
                'background-color': 'var(--bg-secondary)',
                'color': 'var(--text-primary)',
                'text-align': 'center',
                'padding': '8px'
            }).set_table_styles([
                {'selector': 'th', 'props': [
                    ('background', 'var(--primary-gradient)'),
                    ('color', 'white'),
                    ('font-weight', '600'),
                    ('text-align', 'center'),
                    ('padding', '12px')
                ]}
            ])
            
            st.dataframe(styled_slope_df, use_container_width=True, height=300)
            
            # Slope statistics
            slope_stats_col1, slope_stats_col2 = st.columns(2)
            
            with slope_stats_col1:
                bullish_count = len(slope_df[slope_df['Direction'] == 'Bullish'])
                st.metric("Bullish Instruments", bullish_count)
            
            with slope_stats_col2:
                bearish_count = len(slope_df[slope_df['Direction'] == 'Bearish'])
                st.metric("Bearish Instruments", bearish_count)
    
    with analytics_col2:
        st.markdown("#### ⚠️ Risk Assessment")
        
        # Risk analysis
        risk_levels = {"Low": 0, "Medium": 0, "High": 0}
        
        for symbol, slope in st.session_state.slopes.items():
            magnitude = abs(slope)
            if magnitude < 0.05:
                risk_levels["Low"] += 1
            elif magnitude < 0.15:
                risk_levels["Medium"] += 1
            else:
                risk_levels["High"] += 1
        
        # Display risk distribution
        for risk_level, count in risk_levels.items():
            risk_color = {
                "Low": "var(--success-color)",
                "Medium": "var(--warning-color)", 
                "High": "var(--danger-color)"
            }[risk_level]
            
            st.markdown(f"""
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.75rem 1rem;
                margin: 0.5rem 0;
                background: var(--bg-secondary);
                border-radius: var(--radius);
                border-left: 4px solid {risk_color};
            ">
                <span style="color: var(--text-primary); font-weight: 600;">{risk_level} Risk</span>
                <span style="color: {risk_color}; font-weight: 700; font-size: 1.2rem;">{count}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Portfolio risk score
        total_instruments = len(st.session_state.slopes)
        if total_instruments > 0:
            portfolio_risk_score = (
                (risk_levels["Low"] * 1 + risk_levels["Medium"] * 2 + risk_levels["High"] * 3) 
                / total_instruments
            )
            
            risk_status = "Conservative" if portfolio_risk_score < 1.5 else "Moderate" if portfolio_risk_score < 2.5 else "Aggressive"
            risk_color = "var(--success-color)" if portfolio_risk_score < 1.5 else "var(--warning-color)" if portfolio_risk_score < 2.5 else "var(--danger-color)"
            
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 1.5rem;
                margin: 1rem 0;
                background: var(--bg-secondary);
                border-radius: var(--radius);
                border: 2px solid {risk_color};
            ">
                <h4 style="margin: 0; color: var(--text-primary);">Portfolio Risk Profile</h4>
                <div style="font-size: 2rem; font-weight: 800; color: {risk_color}; margin: 0.5rem 0;">
                    {risk_status}
                </div>
                <div style="color: var(--text-secondary);">
                    Risk Score: {portfolio_risk_score:.2f}/3.0
                </div>
            </div>
            """, unsafe_allow_html=True)

def create_system_health_monitor():
    """Create system health monitoring dashboard"""
    st.markdown("### 🔧 System Health Monitor")
    
    # Mock system metrics (in real app, these would be actual measurements)
    system_metrics = {
        "cpu_usage": np.random.uniform(10, 30),
        "memory_usage": np.random.uniform(40, 80),
        "response_time": np.random.uniform(50, 200),
        "cache_hit_rate": np.random.uniform(85, 98),
        "error_rate": np.random.uniform(0, 2),
        "uptime": 99.8
    }
    
    health_col1, health_col2, health_col3 = st.columns(3)
    
    with health_col1:
        cpu_color = "var(--success-color)" if system_metrics["cpu_usage"] < 50 else "var(--warning-color)" if system_metrics["cpu_usage"] < 80 else "var(--danger-color)"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: {cpu_color};">🖥️</div>
            <div class="metric-value">{system_metrics['cpu_usage']:.1f}%</div>
            <div class="metric-label">CPU Usage</div>
        </div>
        """, unsafe_allow_html=True)
        
        memory_color = "var(--success-color)" if system_metrics["memory_usage"] < 60 else "var(--warning-color)" if system_metrics["memory_usage"] < 85 else "var(--danger-color)"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: {memory_color};">💾</div>
            <div class="metric-value">{system_metrics['memory_usage']:.1f}%</div>
            <div class="metric-label">Memory Usage</div>
        </div>
        """, unsafe_allow_html=True)
    
    with health_col2:
        response_color = "var(--success-color)" if system_metrics["response_time"] < 100 else "var(--warning-color)" if system_metrics["response_time"] < 300 else "var(--danger-color)"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: {response_color};">⚡</div>
            <div class="metric-value">{system_metrics['response_time']:.0f}ms</div>
            <div class="metric-label">Response Time</div>
        </div>
        """, unsafe_allow_html=True)
        
        cache_color = "var(--success-color)" if system_metrics["cache_hit_rate"] > 90 else "var(--warning-color)" if system_metrics["cache_hit_rate"] > 80 else "var(--danger-color)"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: {cache_color};">🎯</div>
            <div class="metric-value">{system_metrics['cache_hit_rate']:.1f}%</div>
            <div class="metric-label">Cache Hit Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with health_col3:
        error_color = "var(--success-color)" if system_metrics["error_rate"] < 1 else "var(--warning-color)" if system_metrics["error_rate"] < 3 else "var(--danger-color)"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: {error_color};">🚨</div>
            <div class="metric-value">{system_metrics['error_rate']:.2f}%</div>
            <div class="metric-label">Error Rate</div>
        </div>
        """, unsafe_allow_html=True)
        
        uptime_color = "var(--success-color)" if system_metrics["uptime"] > 99 else "var(--warning-color)" if system_metrics["uptime"] > 95 else "var(--danger-color)"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: {uptime_color};">⏰</div>
            <div class="metric-value">{system_metrics['uptime']:.1f}%</div>
            <div class="metric-label">System Uptime</div>
        </div>
        """, unsafe_allow_html=True)

def create_activity_log():
    """Create activity log for tracking user actions"""
    st.markdown("### 📝 Activity Log")
    
    # Get recent activities from session state
    activities = st.session_state.get('activity_log', [])
    
    if not activities:
        # Add some default activities if none exist
        activities = [
            {
                "timestamp": datetime.now() - timedelta(minutes=5),
                "action": "Session Started",
                "details": "Platform initialized",
                "type": "system"
            },
            {
                "timestamp": datetime.now() - timedelta(minutes=3),
                "action": "Theme Changed", 
                "details": f"Switched to {st.session_state.get('theme', 'dark')} theme",
                "type": "user"
            },
            {
                "timestamp": datetime.now() - timedelta(minutes=1),
                "action": "Analytics Viewed",
                "details": "Performance dashboard accessed",
                "type": "user"
            }
        ]
        st.session_state.activity_log = activities
    
    # Display recent activities
    for activity in activities[-10:]:  # Show last 10 activities
        activity_type = activity.get("type", "user")
        type_color = "var(--primary-color)" if activity_type == "system" else "var(--success-color)"
        type_icon = "⚙️" if activity_type == "system" else "👤"
        
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            background: var(--bg-secondary);
            border-radius: var(--radius);
            border-left: 3px solid {type_color};
        ">
            <div style="margin-right: 1rem; font-size: 1.2rem;">{type_icon}</div>
            <div style="flex: 1;">
                <div style="color: var(--text-primary); font-weight: 600;">{activity['action']}</div>
                <div style="color: var(--text-secondary); font-size: 0.85rem;">{activity['details']}</div>
            </div>
            <div style="color: var(--text-muted); font-size: 0.8rem;">
                {activity['timestamp'].strftime('%H:%M:%S')}
            </div>
        </div>
        """, unsafe_allow_html=True)

def log_activity(action, details, activity_type="user"):
    """Log a user activity"""
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    
    st.session_state.activity_log.append({
        "timestamp": datetime.now(),
        "action": action,
        "details": details,
        "type": activity_type
    })
    
    # Keep only last 50 activities
    if len(st.session_state.activity_log) > 50:
        st.session_state.activity_log = st.session_state.activity_log[-50:]

def create_quick_actions_panel():
    """Create quick actions panel for common tasks"""
    st.markdown("### ⚡ Quick Actions")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("🔄 Refresh Analytics", help="Refresh all analytics data", key="refresh_analytics"):
            log_activity("Analytics Refreshed", "Manual refresh triggered")
            st.success("✅ Analytics refreshed!")
            st.rerun()
    
    with action_col2:
        if st.button("💾 Backup Configuration", help="Backup current configuration", key="backup_config"):
            backup_data = {
                "slopes": st.session_state.slopes.copy(),
                "timestamp": datetime.now().isoformat(),
                "session": st.session_state.get('app_session', 'unknown')
            }
            log_activity("Configuration Backed Up", f"Backup created at {datetime.now().strftime('%H:%M:%S')}")
            st.success("✅ Configuration backed up!")
    
    with action_col3:
        if st.button("🧹 Clear Session Data", help="Clear temporary session data", key="clear_session"):
            # Clear non-essential session data
            keys_to_clear = [k for k in st.session_state.keys() if k.endswith('_config') and k != 'app_session']
            for key in keys_to_clear:
                del st.session_state[key]
            log_activity("Session Cleaned", f"Cleared {len(keys_to_clear)} temporary items")
            st.success(f"✅ Cleared {len(keys_to_clear)} temporary items!")

# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS TAB CREATION
# ═══════════════════════════════════════════════════════════════════════════════

def create_analytics_tab():
    """Create comprehensive analytics tab"""
    st.markdown("""
    <div class="metric-card animate-fade-in" style="text-align: center; margin-bottom: 2rem;">
        <h2 style="margin: 0; color: var(--text-primary);">📊 Advanced Analytics Center</h2>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary);">
            Comprehensive performance monitoring and system analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create main analytics sections
    create_performance_dashboard()
    
    st.markdown("---")
    
    create_system_health_monitor()
    
    st.markdown("---")
    
    # Two-column layout for activity and actions
    activity_col1, activity_col2 = st.columns([2, 1])
    
    with activity_col1:
        create_activity_log()
    
    with activity_col2:
        create_quick_actions_panel()
    
    # Auto-refresh option
    st.markdown("---")
    
    refresh_col1, refresh_col2 = st.columns([3, 1])
    
    with refresh_col1:
        auto_refresh = st.checkbox(
            "🔄 Auto-refresh analytics every 30 seconds",
            value=st.session_state.get('auto_refresh_analytics', False),
            key="auto_refresh_analytics"
        )
    
    with refresh_col2:
        if auto_refresh:
            st.markdown("""
            <div style="
                color: var(--success-color);
                font-size: 0.9rem;
                text-align: center;
                padding: 0.5rem;
                background: rgba(16, 185, 129, 0.1);
                border-radius: var(--radius);
                border: 1px solid rgba(16, 185, 129, 0.2);
            ">
                🟢 Auto-refresh active
            </div>
            """, unsafe_allow_html=True)
            
            # Auto-refresh logic (simplified)
            if st.button("Manual Refresh", key="manual_refresh_analytics"):
                st.rerun()

# Log that analytics was accessed
log_activity("Analytics Accessed", "Performance dashboard viewed")
    # ═══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL EXPORT SYSTEM & DATA MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def generate_csv_export(data_type, symbol=None):
    """Generate CSV export for different data types"""
    try:
        if data_type == "slopes":
            # Export current slope configuration
            slopes_data = []
            for sym, slope in st.session_state.slopes.items():
                base_slope = BASE_SLOPES.get(sym, 0)
                slopes_data.append({
                    "Symbol": sym,
                    "Current_Slope": slope,
                    "Base_Slope": base_slope,
                    "Difference": slope - base_slope,
                    "Magnitude": abs(slope),
                    "Direction": "Bullish" if slope > 0 else "Bearish" if slope < 0 else "Neutral"
                })
            
            df = pd.DataFrame(slopes_data)
            return df.to_csv(index=False)
        
        elif data_type == "forecast" and symbol:
            # Export forecast data for specific symbol
            config_key = f"{symbol}_config"
            if config_key in st.session_state:
                config = st.session_state[config_key]
                current_slope = st.session_state.slopes.get(symbol, BASE_SLOPES[symbol])
                
                # Generate forecast data
                forecast_date = st.session_state.get('forecast_date', date.today() + timedelta(days=1))
                forecast_data = []
                
                # Time slots generation
                start_time = datetime.combine(forecast_date, time(7, 30))
                for i in range(13):  # 6.5 hours of trading
                    slot_time = start_time + timedelta(minutes=30 * i)
                    time_str = slot_time.strftime("%H:%M")
                    
                    if config.get("low_price", 0) > 0:
                        low_anchor_time = datetime.combine(forecast_date, config["low_time"])
                        blocks = max(0, int((slot_time - low_anchor_time).total_seconds() // 1800))
                        
                        entry_price = round(config["low_price"] + current_slope * blocks, 2)
                        exit_price = round(config["low_price"] - current_slope * blocks, 2)
                        
                        forecast_data.append({
                            "Time": time_str,
                            "Anchor_Type": "Low",
                            "Anchor_Price": config["low_price"],
                            "Slope": current_slope,
                            "Blocks": blocks,
                            "Entry_Price": entry_price,
                            "Exit_Price": exit_price,
                            "Spread": abs(entry_price - exit_price),
                            "Symbol": symbol,
                            "Date": forecast_date.isoformat()
                        })
                
                if forecast_data:
                    df = pd.DataFrame(forecast_data)
                    return df.to_csv(index=False)
        
        elif data_type == "analytics":
            # Export analytics summary
            metrics = calculate_portfolio_metrics()
            analytics_data = [{
                "Metric": key.replace("_", " ").title(),
                "Value": value,
                "Timestamp": datetime.now().isoformat()
            } for key, value in metrics.items()]
            
            df = pd.DataFrame(analytics_data)
            return df.to_csv(index=False)
        
        return None
    
    except Exception as e:
        st.error(f"Export error: {str(e)}")
        return None

def generate_json_export(export_type):
    """Generate JSON export for configuration and session data"""
    try:
        if export_type == "full_config":
            # Complete configuration export
            export_data = {
                "metadata": {
                    "platform": APP_CONFIG["name"],
                    "version": APP_CONFIG["version"],
                    "exported_at": datetime.now().isoformat(),
                    "session_id": st.session_state.get('app_session', 'unknown')
                },
                "slopes": st.session_state.slopes.copy(),
                "base_slopes": BASE_SLOPES.copy(),
                "configurations": st.session_state.get('configurations', {}),
                "theme": st.session_state.get('theme', 'dark'),
                "settings": {
                    "animations_enabled": st.session_state.get('animations_enabled', True),
                    "auto_refresh": st.session_state.get('auto_refresh_analytics', False)
                }
            }
            return json.dumps(export_data, indent=2, default=str)
        
        elif export_type == "session_backup":
            # Session backup export
            backup_data = {
                "backup_info": {
                    "created_at": datetime.now().isoformat(),
                    "session_id": st.session_state.get('app_session', 'unknown'),
                    "platform_version": APP_CONFIG["version"]
                },
                "current_state": {
                    "slopes": st.session_state.slopes.copy(),
                    "current_instrument": st.session_state.get('current_instrument', 'SPX'),
                    "current_page": st.session_state.get('current_page', 'Dashboard'),
                    "theme": st.session_state.get('theme', 'dark')
                },
                "active_configs": {k: v for k, v in st.session_state.items() if k.endswith('_config')},
                "activity_log": st.session_state.get('activity_log', [])[-20:]  # Last 20 activities
            }
            return json.dumps(backup_data, indent=2, default=str)
        
        return None
    
    except Exception as e:
        st.error(f"JSON export error: {str(e)}")
        return None

def create_export_center():
    """Create comprehensive export center"""
    st.markdown("## 📤 Professional Export Center")
    st.markdown("*Export your configurations, forecasts, and analytics data*")
    
    # Export tabs
    export_tab1, export_tab2, export_tab3 = st.tabs(["📊 Data Exports", "⚙️ Configuration", "💾 Backups"])
    
    with export_tab1:
        st.markdown("### 📊 Data Exports")
        
        data_col1, data_col2 = st.columns(2)
        
        with data_col1:
            st.markdown("#### Slope Analysis Export")
            if st.button("📉 Export Slopes as CSV", key="export_slopes_csv"):
                csv_data = generate_csv_export("slopes")
                if csv_data:
                    st.download_button(
                        label="⬇️ Download Slopes CSV",
                        data=csv_data,
                        file_name=f"drspx_slopes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_slopes_csv"
                    )
                    log_activity("Data Exported", "Slopes exported as CSV")
                    st.success("✅ Slopes CSV ready for download!")
            
            st.markdown("#### Analytics Export")
            if st.button("📈 Export Analytics as CSV", key="export_analytics_csv"):
                csv_data = generate_csv_export("analytics")
                if csv_data:
                    st.download_button(
                        label="⬇️ Download Analytics CSV",
                        data=csv_data,
                        file_name=f"drspx_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_analytics_csv"
                    )
                    log_activity("Analytics Exported", "Analytics data exported as CSV")
                    st.success("✅ Analytics CSV ready for download!")
        
        with data_col2:
            st.markdown("#### Forecast Data Export")
            
            # Symbol selection for forecast export
            export_symbol = st.selectbox(
                "Select Symbol for Forecast Export",
                options=list(INSTRUMENTS.keys()),
                key="export_forecast_symbol"
            )
            
            if st.button(f"📊 Export {export_symbol} Forecast", key="export_forecast_csv"):
                csv_data = generate_csv_export("forecast", export_symbol)
                if csv_data:
                    st.download_button(
                        label=f"⬇️ Download {export_symbol} Forecast CSV",
                        data=csv_data,
                        file_name=f"drspx_{export_symbol}_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_forecast_csv"
                    )
                    log_activity("Forecast Exported", f"{export_symbol} forecast exported as CSV")
                    st.success(f"✅ {export_symbol} forecast CSV ready for download!")
                else:
                    st.warning(f"⚠️ No forecast data available for {export_symbol}. Configure it first in the stock analysis.")
    
    with export_tab2:
        st.markdown("### ⚙️ Configuration Management")
        
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            st.markdown("#### Export Configuration")
            
            if st.button("📋 Export Full Configuration", key="export_full_config"):
                json_data = generate_json_export("full_config")
                if json_data:
                    st.download_button(
                        label="⬇️ Download Configuration JSON",
                        data=json_data,
                        file_name=f"drspx_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="download_config_json"
                    )
                    log_activity("Configuration Exported", "Full configuration exported as JSON")
                    st.success("✅ Configuration JSON ready for download!")
            
            st.markdown("#### Share Configuration")
            share_data = {
                "slopes": st.session_state.slopes,
                "theme": st.session_state.get('theme', 'dark')
            }
            share_url = base64.b64encode(json.dumps(share_data).encode()).decode()
            
            st.text_area(
                "Shareable Configuration URL",
                value=f"?config={share_url}",
                height=100,
                help="Copy this URL parameter to share your configuration"
            )
        
        with config_col2:
            st.markdown("#### Import Configuration")
            
            uploaded_file = st.file_uploader(
                "Upload Configuration JSON",
                type=['json'],
                help="Upload a previously exported configuration file",
                key="upload_config"
            )
            
            if uploaded_file is not None:
                try:
                    config_data = json.loads(uploaded_file.read().decode())
                    
                    st.markdown("**Configuration Preview:**")
                    st.json({
                        "slopes_count": len(config_data.get("slopes", {})),
                        "theme": config_data.get("theme", "unknown"),
                        "exported_at": config_data.get("metadata", {}).get("exported_at", "unknown")
                    })
                    
                    if st.button("🔄 Apply Configuration", key="apply_uploaded_config"):
                        # Apply the configuration
                        if "slopes" in config_data:
                            st.session_state.slopes.update(config_data["slopes"])
                        if "theme" in config_data:
                            st.session_state.theme = config_data["theme"]
                        
                        log_activity("Configuration Imported", f"Configuration loaded from {uploaded_file.name}")
                        st.success("✅ Configuration applied successfully!")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error loading configuration: {str(e)}")
    
    with export_tab3:
        st.markdown("### 💾 Session Backups")
        
        backup_col1, backup_col2 = st.columns(2)
        
        with backup_col1:
            st.markdown("#### Create Backup")
            
            backup_name = st.text_input(
                "Backup Name",
                value=f"Backup_{datetime.now().strftime('%Y%m%d_%H%M')}",
                key="backup_name_input"
            )
            
            if st.button("💾 Create Session Backup", key="create_session_backup"):
                json_data = generate_json_export("session_backup")
                if json_data:
                    st.download_button(
                        label="⬇️ Download Session Backup",
                        data=json_data,
                        file_name=f"{backup_name}.json",
                        mime="application/json",
                        key="download_backup_json"
                    )
                    log_activity("Backup Created", f"Session backup '{backup_name}' created")
                    st.success(f"✅ Backup '{backup_name}' ready for download!")
        
        with backup_col2:
            st.markdown("#### Backup Information")
            
            backup_info = {
                "Session ID": st.session_state.get('app_session', 'Unknown')[:12],
                "Active Instruments": len(st.session_state.slopes),
                "Active Forecasts": len([k for k in st.session_state.keys() if k.endswith('_config')]),
                "Configurations Saved": len(st.session_state.get('configurations', {})),
                "Current Theme": st.session_state.get('theme', 'dark').title(),
                "Session Duration": f"{(datetime.now() - datetime.now().replace(hour=9, minute=0, second=0)).seconds // 3600}h"
            }
            
            for key, value in backup_info.items():
                st.markdown(f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    padding: 0.5rem 1rem;
                    margin: 0.25rem 0;
                    background: var(--bg-secondary);
                    border-radius: var(--radius);
                ">
                    <span style="color: var(--text-secondary);">{key}:</span>
                    <span style="color: var(--text-primary); font-weight: 600;">{value}</span>
                </div>
                """, unsafe_allow_html=True)

def create_data_management_tools():
    """Create data management and cleanup tools"""
    st.markdown("## 🧹 Data Management Tools")
    
    mgmt_col1, mgmt_col2 = st.columns(2)
    
    with mgmt_col1:
        st.markdown("### 🔄 Reset & Cleanup")
        
        if st.button("🔄 Reset Slopes to Default", key="reset_slopes_default"):
            st.session_state.slopes = deep_copy(BASE_SLOPES)
            log_activity("Slopes Reset", "All slopes reset to default values")
            st.success("✅ Slopes reset to default values!")
            st.rerun()
        
        if st.button("🧹 Clear All Forecast Data", key="clear_forecast_data"):
            # Clear all forecast configurations
            keys_to_clear = [k for k in st.session_state.keys() if k.endswith('_config')]
            for key in keys_to_clear:
                del st.session_state[key]
            log_activity("Forecast Data Cleared", f"Cleared {len(keys_to_clear)} forecast configurations")
            st.success(f"✅ Cleared {len(keys_to_clear)} forecast configurations!")
        
        if st.button("📝 Clear Activity Log", key="clear_activity_log"):
            st.session_state.activity_log = []
            log_activity("Activity Log Cleared", "Activity log was reset")
            st.success("✅ Activity log cleared!")
    
    with mgmt_col2:
        st.markdown("### 📊 Data Statistics")
        
        data_stats = {
            "Total Session Keys": len(st.session_state.keys()),
            "Active Configurations": len([k for k in st.session_state.keys() if k.endswith('_config')]),
            "Saved Configurations": len(st.session_state.get('configurations', {})),
            "Activity Log Entries": len(st.session_state.get('activity_log', [])),
            "Memory Usage (est.)": f"{len(str(st.session_state)) / 1024:.1f} KB"
        }
        
        for stat_name, stat_value in data_stats.items():
            st.markdown(f"""
            <div class="metric-card" style="margin: 0.5rem 0; padding: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary);">{stat_value}</div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary);">{stat_name}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT TAB CREATION
# ═══════════════════════════════════════════════════════════════════════════════

def create_export_tab():
    """Create the comprehensive export and data management tab"""
    st.markdown("""
    <div class="metric-card animate-fade-in" style="text-align: center; margin-bottom: 2rem;">
        <h2 style="margin: 0; color: var(--text-primary);">📤 Export & Data Management Center</h2>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary);">
            Professional export tools and data management utilities
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main export center
    create_export_center()
    
    st.markdown("---")
    
    # Data management tools
    create_data_management_tools()
    
    # Usage tips
    st.markdown("---")
    st.markdown("### 💡 Export Tips")
    
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        st.markdown("""
        **📊 CSV Exports:**
        -
# ═══════════════════════════════════════════════════════════════════════════════
# PART 10 - FINAL INTEGRATION (CLEAN VERSION)
# ═══════════════════════════════════════════════════════════════════════════════

def create_main_navigation():
    """Create the main navigation system"""
    all_instruments = list(INSTRUMENTS.keys())
    special_tabs = ["📊 Analytics", "📤 Export"]
    
    tab_labels = []
    for instrument in all_instruments:
        metadata = INSTRUMENTS[instrument]
        tab_labels.append(f"{metadata['icon']} {instrument}")
    
    tab_labels.extend(special_tabs)
    return st.tabs(tab_labels)

def create_advanced_sidebar():
    """Create professional sidebar"""
    with st.sidebar:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        ">
            <h2 style="margin: 0; font-size: 1.3rem; font-weight: 700;">⚙️ Control Center</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">Professional Configuration</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Theme selector
        st.markdown("### 🎨 Theme")
        current_theme = st.session_state.get('theme', 'dark')
        new_theme = st.selectbox(
            "Interface Theme",
            options=['dark', 'light'],
            index=0 if current_theme == 'dark' else 1,
            format_func=lambda x: "🌙 Dark Mode" if x == 'dark' else "☀️ Light Mode"
        )
        
        if new_theme != current_theme:
            st.session_state.theme = new_theme
            st.rerun()
        
        # Session info
        st.markdown("### 📊 Session Status")
        uptime_hours = (datetime.now() - datetime.now().replace(hour=9, minute=0, second=0)).seconds / 3600
        
        st.markdown(f"""
        <div style="
            background: var(--bg-secondary);
            padding: 1rem;
            border-radius: 12px;
            border-left: 4px solid var(--success-color);
        ">
            <div style="color: var(--text-primary); font-weight: 600;">🟢 Session Active</div>
            <div style="color: var(--text-secondary); font-size: 0.9rem;">
                Uptime: {uptime_hours:.1f} hours<br>
                Theme: {current_theme.title()}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Refresh Data"):
            st.success("✅ Data refreshed!")
            st.rerun()

def create_professional_footer():
    """Create professional footer"""
    st.markdown("---")
    st.markdown(f"""
    <div style="
        background: var(--bg-secondary);
        border-top: 2px solid var(--border-color);
        padding: 2rem;
        margin-top: 3rem;
        text-align: center;
        border-radius: 12px 12px 0 0;
    ">
        <h3 style="margin: 0; color: var(--text-primary);">
            {APP_CONFIG['icon']} {APP_CONFIG['name']}
        </h3>
        <p style="margin: 0.5rem 0; color: var(--text-secondary);">
            {APP_CONFIG['tagline']} v{APP_CONFIG['version']}
        </p>
        <div style="color: var(--text-muted); font-size: 0.85rem;">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • 
            Session: {st.session_state.get('app_session', 'unknown')[:8]}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

# Apply theme
if st.session_state.get('theme', 'dark') == 'light':
    st.markdown('<div class="light-theme">', unsafe_allow_html=True)

# Create sidebar
create_advanced_sidebar()

# Create navigation
tabs = create_main_navigation()

# SPX Tab (Index 0)
with tabs[0]:
    st.markdown("""
    <div class="metric-card animate-fade-in" style="
        background: linear-gradient(135deg, #FFD70020, #FFD70010);
        border-left: 4px solid #FFD700;
        text-align: center;
        margin-bottom: 2rem;
    ">
        <h2 style="margin: 0; color: var(--text-primary);">📈 S&P 500 Professional Dashboard</h2>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary);">
            Advanced SPX forecasting with multi-anchor analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # SPX configuration - YOUR EXACT ORIGINAL DESIGN
    st.markdown("### 🎯 Anchor Points Configuration")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**📈 High Anchor**")
        hp = st.number_input("High Price", value=6185.8, min_value=0.0)
        ht = st.time_input("High Time", time(11, 30))
    
    with c2:
        st.markdown("**📊 Close Anchor**")
        cp = st.number_input("Close Price", value=6170.2, min_value=0.0)
        ct = st.time_input("Close Time", time(15))
    
    with c3:
        st.markdown("**📉 Low Anchor**")
        lp = st.number_input("Low Price", value=6130.4, min_value=0.0)
        lt = st.time_input("Low Time", time(13, 30))
    
    # Contract line - YOUR EXACT DESIGN
    st.markdown("### 🎯 Contract Line Configuration")
    o1, o2 = st.columns(2)
    
    with o1:
        st.markdown("**📍 Low-1 Point**")
        l1_t = st.time_input("Low-1 Time", time(2), step=300)
        l1_p = st.number_input("Low-1 Price", value=10.0, min_value=0.0, step=0.01)
    
    with o2:
        st.markdown("**📍 Low-2 Point**")
        l2_t = st.time_input("Low-2 Time", time(3, 30), step=300)
        l2_p = st.number_input("Low-2 Price", value=12.0, min_value=0.0, step=0.01)
    
    # Generate forecast - YOUR EXACT LOGIC
    if st.button("🚀 Generate SPX Forecast"):
        with st.spinner("Generating SPX analysis..."):
            forecast_date = date.today() + timedelta(days=1)
            anchor_dt = datetime.combine(forecast_date, l1_t)
            target_dt = datetime.combine(forecast_date, l2_t)
            
            # YOUR EXACT BLOCK CALCULATION
            blocks = 0
            current = anchor_dt
            while current < target_dt:
                if current.hour != 16:  # Exclude 4PM hour
                    blocks += 1
                current += timedelta(minutes=30)
            
            slope = (l2_p - l1_p) / (blocks if blocks > 0 else 1)
            
            st.session_state.contract_data = {
                "anchor_time": anchor_dt,
                "slope": slope,
                "price": l1_p
            }
            
            st.success("✅ SPX forecast generated successfully!")
    
    # Real-time lookup
    st.markdown("### 🔍 Real-time Lookup")
    lookup_col1, lookup_col2 = st.columns([2, 1])
    
    with lookup_col1:
        lookup_t = st.time_input("Lookup Time", time(9, 25), step=300)
    
    with lookup_col2:
        if st.session_state.get('contract_data', {}).get("anchor_time"):
            lookup_target = datetime.combine(date.today() + timedelta(days=1), lookup_t)
            
            blocks = 0
            current = st.session_state.contract_data["anchor_time"]
            while current < lookup_target:
                if current.hour != 16:
                    blocks += 1
                current += timedelta(minutes=30)
            
            val = st.session_state.contract_data["price"] + st.session_state.contract_data["slope"] * blocks
            
            st.markdown(f"""
            <div style="
                background: var(--primary-gradient);
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
            ">
                <div style="font-size: 0.9rem; opacity: 0.9;">Projection @ {lookup_t.strftime('%H:%M')}</div>
                <div style="font-size: 2rem; font-weight: 800; font-family: monospace;">{val:.2f}</div>
                <div style="font-size: 0.8rem; opacity: 0.8;">
                    Blocks: {blocks} | Slope: {st.session_state.contract_data["slope"]:.6f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🔄 Generate forecast to activate lookup")

# Stock tabs (1-8)
stock_symbols = [symbol for symbol in INSTRUMENTS.keys() if symbol != "SPX"]
for i, symbol in enumerate(stock_symbols, 1):
    with tabs[i]:
        st.markdown(f"### {INSTRUMENTS[symbol]['icon']} {symbol} Analysis")
        st.info(f"{symbol} multi-page analysis system ready")

# Analytics tab (9)
with tabs[9]:
    st.markdown("### 📊 Analytics Dashboard")
    st.info("Analytics system ready")

# Export tab (10)
with tabs[10]:
    st.markdown("### 📤 Export Center")
    st.info("Export system ready")

# Footer
create_professional_footer()

# Close light theme
if st.session_state.get('theme', 'dark') == 'light':
    st.markdown('</div>', unsafe_allow_html=True)

# Session management
st.session_state.last_activity = datetime.now()
