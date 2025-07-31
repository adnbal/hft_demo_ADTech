import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import random
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --------------------- PAGE CONFIG ---------------------
st.set_page_config(page_title="HFT AI Dashboard", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #0a0a0a;
        color: white;
    }
    .neon-box {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: #fff;
        text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc, 0 0 30px #00ffcc;
    }
    .buy-glow {
        background-color: #001f1f;
        border: 2px solid #00ffcc;
        box-shadow: 0 0 20px #00ffcc;
    }
    .sell-glow {
        background-color: #1f0000;
        border: 2px solid #ff0044;
        box-shadow: 0 0 20px #ff0044;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------- SESSION STATE ---------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []

# --------------------- SIDEBAR PANEL ---------------------
st.sidebar.header("🛠 Trading Panel")
mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.radio("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", min_value=0.01, value=1.0, step=0.01)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
limit_price = st.sidebar.number_input("Limit Price", min_value=10000.0, value=30000.0, step=100.0)
submit_order = st.sidebar.button("Submit Order")

# --------------------- SIMULATED PRICE DATA ---------------------
price = 30000 + np.random.randn() * 50
timestamp = datetime.now().strftime("%H:%M:%S")
st.session_state.price_data.append({"time": timestamp, "price": price, "bid": price - 10, "ask": price + 10})

# --------------------- HANDLE TRADES ---------------------
if submit_order:
    trade_price = price if order_type == "MARKET" else limit_price
    st.session_state.trade_log.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "side": side,
        "qty": qty,
        "price": trade_price
    })
    if side == "BUY":
        st.session_state.positions.append({"qty": qty, "price": trade_price})
    else:  # SELL
        if st.session_state.positions:
            st.session_state.positions.pop(0)

# --------------------- LAYOUT ---------------------
st.title("⚡ High Frequency Trading AI Dashboard")
st.write("### Simulated BTC/USDT Trading with AI Insights")

col1, col2 = st.columns([2, 1])

# --------------------- PRICE CHART ---------------------
with col1:
    st.subheader("📈 Live BTC Price")
    if len(st.session_state.price_data) > 5:
        df = pd.DataFrame(st.session_state.price_data)
        fig = go.Figure(data=[
            go.Candlestick(x=df['time'], open=df['price'] - 20, high=df['price'] + 20,
                           low=df['price'] - 40, close=df['price'], name="BTC Price",
                           increasing_line_color='lime', decreasing_line_color='red')
        ])
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Waiting for price data...")

# --------------------- TRADE LOG ---------------------
with col2:
    st.subheader("📜 Trade Log")
    if st.session_state.trade_log:
        df_trades = pd.DataFrame(st.session_state.trade_log)
        st.dataframe(df_trades.tail(10), height=300)
    else:
        st.write("No trades yet.")

# --------------------- P&L CALCULATIONS ---------------------
current_price = price
realized_pnl = 0.0
unrealized_pnl = sum((current_price - pos["price"]) * pos["qty"] for pos in st.session_state.positions)

# Add to P&L history
if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = []
st.session_state.pnl_history.append({
    "time": timestamp,
    "realized": realized_pnl,
    "unrealized": unrealized_pnl
})

# --------------------- P&L GRAPH ---------------------
st.subheader("📊 Realized & Unrealized P&L")
df_pnl = pd.DataFrame(st.session_state.pnl_history)
if len(df_pnl) > 1:
    fig_pnl = go.Figure()
    fig_pnl.add_trace(go.Scatter(x=df_pnl['time'], y=df_pnl['realized'], mode='lines+markers',
                                 name='Realized P&L', line=dict(color='yellow', width=3)))
    fig_pnl.add_trace(go.Scatter(x=df_pnl['time'], y=df_pnl['unrealized'], mode='lines+markers',
                                 name='Unrealized P&L', line=dict(color='lime', width=3)))
    fig_pnl.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig_pnl, use_container_width=True)

# --------------------- PORTFOLIO METRICS ---------------------
st.subheader("📊 Portfolio Metrics")
open_position = sum(pos["qty"] for pos in st.session_state.positions)
current_value = open_position * current_price
avg_entry_price = (sum(pos["qty"] * pos["price"] for pos in st.session_state.positions) / open_position) if open_position > 0 else 0
metrics_df = pd.DataFrame({
    "Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
    "Value": [f"{open_position:.4f}", f"${current_value:,.2f}", f"${avg_entry_price:,.2f}"]
})
st.table(metrics_df)

# --------------------- AI RECOMMENDATION ---------------------
trend = "Bullish 📈 → Consider BUY" if random.random() > 0.5 else "Bearish 📉 → Consider SELL"
insight_reason = (
    "Volatility is high, trend momentum strong, price forecast suggests upward breakout."
    if "BUY" in trend else
    "Downtrend forming, high selling pressure detected, short-term bearish pattern likely."
)
glow_class = "buy-glow" if "BUY" in trend else "sell-glow"

st.markdown(f"""
<div class="neon-box {glow_class}">
    <h2>🤖 AI Market Intelligence</h2>
    <p>{trend}</p>
    <p><i>{insight_reason}</i></p>
    <p>Forecast: Next 1hr projected move: ± {round(np.random.uniform(0.5, 1.5), 2)}%</p>
</div>
""", unsafe_allow_html=True)

# --------------------- AUTO REFRESH ---------------------
st_autorefresh(interval=5000, key="refresh")
