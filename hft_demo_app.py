import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import random

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="AI HFT Dashboard", layout="wide")

# -------------------- SESSION STATE --------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

# -------------------- AUTO REFRESH --------------------
st_autorefresh(interval=5000, key="auto-refresh")

# -------------------- PRICE SIMULATION --------------------
price = 30000 + np.random.randn() * 50
volume = random.randint(10, 100)
st.session_state.price_data.append({"time": datetime.now(), "price": price, "volume": volume})

# -------------------- AI SIGNAL --------------------
recent_prices = [p["price"] for p in st.session_state.price_data[-10:]]
signal = "HOLD"
reason = "Collecting more data for better prediction."
forecast = ""
color = "#39ff14"  # Default green for glow

if len(recent_prices) >= 10:
    trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
    if trend > 0:
        signal = "BUY"
        reason = "Price trend is upward, indicating bullish momentum."
        forecast = "Expected ~0.8% rise in next few minutes."
        color = "#39ff14"  # Green glow for BUY
    elif trend < 0:
        signal = "SELL"
        reason = "Price trend is downward, indicating bearish momentum."
        forecast = "Expected ~0.7% drop in next few minutes."
        color = "#ff073a"  # Red glow for SELL

# -------------------- CUSTOM CSS --------------------
st.markdown(f"""
    <style>
    body {{
        background-color: #0f172a;
        color: white;
        margin: 0;
    }}
    .main > div {{
        padding-top: 0rem;  /* Remove empty space at top */
    }}
    .sidebar .sidebar-content {{
        background: #1e293b;
        padding: 15px;
        border-radius: 10px;
    }}
    .right-panel {{
        background: #1e293b;
        padding: 15px;
        border-radius: 10px;
        min-height: 100%;
    }}
    .neon-title {{
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        color: {color};
        text-shadow: 0 0 20px {color}, 0 0 30px {color};
        border: 2px solid {color};
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 10px;
    }}
    .neon-box {{
        border: 2px solid {color};
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: {color};
        animation: glow 1.5s infinite alternate;
    }}
    @keyframes glow {{
        from {{ box-shadow: 0 0 10px {color}; }}
        to {{ box-shadow: 0 0 25px {color}; }}
    }}
    </style>
""", unsafe_allow_html=True)

# -------------------- LAYOUT --------------------
col_ai, col_main, col_trade = st.columns([0.4, 1.2, 0.6])

# ---------- AI PANEL ----------
with col_ai:
    st.markdown(f"<div class='neon-title'>🤖 AI Market Intelligence</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='neon-box'>{signal}</div>", unsafe_allow_html=True)
    st.write(reason)
    st.write(forecast)

# ---------- MAIN PANEL ----------
with col_main:
    st.markdown(f"<div class='neon-title'>⚡ High Frequency Trading Dashboard</div>", unsafe_allow_html=True)

    # Price & Volume Chart
    df = pd.DataFrame(st.session_state.price_data[-100:])
    if not df.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["time"], y=df["price"], mode="lines+markers",
                                 name="Price", line=dict(color="lime", width=3)))
        fig.add_trace(go.Bar(x=df["time"], y=df["volume"], name="Volume",
                             marker_color="blue", opacity=0.3, yaxis="y2"))
        fig.update_layout(template="plotly_dark",
                          yaxis=dict(title="Price (USD)"),
                          yaxis2=dict(title="Volume", overlaying="y", side="right"),
                          height=400)
        st.plotly_chart(fig, use_container_width=True)

    # P&L Line Chart
    pnl = [random.uniform(-100, 150) for _ in range(len(df))]
    st.markdown(f"<div class='neon-title'>📊 P&L Analysis</div>", unsafe_allow_html=True)
    fig_pnl = go.Figure()
    fig_pnl.add_trace(go.Scatter(x=df["time"], y=pnl, mode="lines", name="P&L", line=dict(color="yellow", width=2)))
    fig_pnl.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig_pnl, use_container_width=True)

    # Trade Log
    st.markdown(f"<div class='neon-title'>📜 Trade Log</div>", unsafe_allow_html=True)
    trade_df = pd.DataFrame(st.session_state.trade_log)
    st.dataframe(trade_df if not trade_df.empty else pd.DataFrame(columns=["time", "side", "qty", "price"]))

# ---------- TRADING PANEL ----------
with col_trade:
    st.markdown("<div class='right-panel'>", unsafe_allow_html=True)
    st.markdown(f"<div class='neon-title'>🛠 Trading Panel</div>", unsafe_allow_html=True)

    mode = st.radio("Mode", ["Simulation", "Live"])
    side = st.radio("Side", ["BUY", "SELL"])
    qty = st.number_input("Quantity", min_value=1, value=5)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    price_input = None
    if order_type == "LIMIT":
        price_input = st.number_input("Limit Price", min_value=10000, value=30000)

    if st.button("Submit Order"):
        trade_price = price_input if order_type == "LIMIT" else price
        st.session_state.trade_log.append({
            "time": datetime.now(),
            "side": side,
            "qty": qty,
            "price": round(trade_price, 2)
        })

    st.markdown("</div>", unsafe_allow_html=True)
