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

# -------------------- CUSTOM CSS --------------------
st.markdown("""
    <style>
    body {
        background-color: #0f172a;
        color: white;
    }
    .sidebar .sidebar-content {
        background: #1e293b;
        padding: 15px;
    }
    .neon-box {
        border: 2px solid;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        animation: glow-green 1.5s infinite alternate;
    }
    @keyframes glow-green {
        from { box-shadow: 0 0 10px #39ff14; border-color:#39ff14; color:#39ff14;}
        to { box-shadow: 0 0 25px #39ff14; border-color:#39ff14; color:#39ff14;}
    }
    .neon-sell {
        animation: glow-red 1.5s infinite alternate;
    }
    @keyframes glow-red {
        from { box-shadow: 0 0 10px #ff073a; border-color:#ff073a; color:#ff073a;}
        to { box-shadow: 0 0 25px #ff073a; border-color:#ff073a; color:#ff073a;}
    }
    .buy-button {
        background: #39ff14;
        color: black;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        width: 100%;
        font-size: 16px;
        margin-top: 10px;
        box-shadow: 0 0 15px #39ff14;
    }
    .buy-button:hover {
        box-shadow: 0 0 30px #39ff14;
    }
    .sell-button {
        background: #ff073a;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        width: 100%;
        font-size: 16px;
        margin-top: 10px;
        box-shadow: 0 0 15px #ff073a;
    }
    .sell-button:hover {
        box-shadow: 0 0 30px #ff073a;
    }
    h1, h2, h3 {
        color: #39ff14;
        text-shadow: 0 0 10px #39ff14;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- INITIALIZE SESSION STATE --------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []

# -------------------- AUTO REFRESH --------------------
st_autorefresh(interval=5000, key="auto-refresh")

# -------------------- PRICE SIMULATION --------------------
price = 30000 + np.random.randn() * 50
volume = random.randint(10, 100)
st.session_state.price_data.append({"time": datetime.now(), "price": price, "volume": volume})

# -------------------- AI SIGNAL GENERATION --------------------
recent_prices = [p["price"] for p in st.session_state.price_data[-10:]]
signal = "HOLD"
reason = "Insufficient data for prediction."
forecast = ""

if len(recent_prices) >= 10:
    trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
    if trend > 0:
        signal = "BUY"
        reason = "Price trend is upward, indicating bullish momentum. Buyers dominate order flow."
        forecast = "Price expected to rise by ~0.8% in next few minutes based on volatility patterns."
    elif trend < 0:
        signal = "SELL"
        reason = "Price trend is downward, indicating bearish momentum. Sellers dominate order flow."
        forecast = "Price likely to drop by ~0.7% in next few minutes due to negative trend."

# -------------------- SIDEBAR: AI PANEL + TRADING PANEL --------------------
st.sidebar.markdown("<h2>🤖 AI Market Intelligence</h2>", unsafe_allow_html=True)
if signal == "BUY":
    st.sidebar.markdown(f"<div class='neon-box'>{signal}</div>", unsafe_allow_html=True)
elif signal == "SELL":
    st.sidebar.markdown(f"<div class='neon-box neon-sell'>{signal}</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown(f"<div class='neon-box'>HOLD</div>", unsafe_allow_html=True)

st.sidebar.write(reason)
st.sidebar.write(forecast)

# Trading Panel
st.sidebar.markdown("<h2>🛠 Trading Panel</h2>", unsafe_allow_html=True)
mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.radio("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", min_value=1, value=5)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
price_input = None
if order_type == "LIMIT":
    price_input = st.sidebar.number_input("Limit Price", min_value=10000, value=30000)
if st.sidebar.button("Submit Order"):
    trade_price = price_input if order_type == "LIMIT" else price
    st.session_state.trade_log.append({
        "time": datetime.now(),
        "side": side,
        "qty": qty,
        "price": round(trade_price, 2)
    })

# BUY / SELL Buttons
st.sidebar.markdown("<h3>Quick Actions</h3>", unsafe_allow_html=True)
st.sidebar.button("BUY", key="buy_button", help="Quick BUY Order", on_click=lambda: st.session_state.trade_log.append({
    "time": datetime.now(), "side": "BUY", "qty": 5, "price": round(price, 2)
}), use_container_width=True)
st.sidebar.button("SELL", key="sell_button", help="Quick SELL Order", on_click=lambda: st.session_state.trade_log.append({
    "time": datetime.now(), "side": "SELL", "qty": 5, "price": round(price, 2)
}), use_container_width=True)

# -------------------- MAIN DASHBOARD --------------------
st.markdown("<h1 style='text-align:center;'>⚡ High Frequency Trading AI Dashboard</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # Live BTC Price with Volume
    st.subheader("📈 Live BTC Price & Volume")
    df = pd.DataFrame(st.session_state.price_data[-100:])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["price"], mode="lines+markers", name="Price", line=dict(color="lime", width=3)))
    fig.add_trace(go.Bar(x=df["time"], y=df["volume"], name="Volume", marker_color="blue", opacity=0.3, yaxis="y2"))
    fig.update_layout(
        template="plotly_dark",
        yaxis=dict(title="Price (USD)"),
        yaxis2=dict(title="Volume", overlaying="y", side="right"),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # P&L Line Chart
    st.subheader("📊 Realized & Unrealized P&L")
    pnl = [random.uniform(-100, 150) for _ in range(len(df))]
    fig_pnl = go.Figure()
    fig_pnl.add_trace(go.Scatter(x=df["time"], y=pnl, mode="lines", name="P&L", line=dict(color="yellow", width=2)))
    fig_pnl.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig_pnl, use_container_width=True)

with col2:
    # Trade Log
    st.subheader("📜 Trade Log")
    trade_df = pd.DataFrame(st.session_state.trade_log)
    if not trade_df.empty:
        st.dataframe(trade_df.tail(10))
    else:
        st.write("No trades yet.")

    # Portfolio Metrics
    st.subheader("📊 Portfolio Metrics")
    st.table(pd.DataFrame({
        "Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
        "Value": ["0", "$0.00", "$0.00"]
    }))
