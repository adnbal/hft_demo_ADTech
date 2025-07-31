import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import random
import time

# -------------------------------
# ✅ Page Config
# -------------------------------
st.set_page_config(page_title="HFT AI Dashboard", layout="wide")

# -------------------------------
# ✅ Initialize Session State
# -------------------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "position" not in st.session_state:
    st.session_state.position = 0.0
if "avg_price" not in st.session_state:
    st.session_state.avg_price = 0.0
if "realized_pnl" not in st.session_state:
    st.session_state.realized_pnl = 0.0

# -------------------------------
# ✅ Title
# -------------------------------
st.markdown(
    "<h1 style='color:#00FFAA; text-align:center;'>⚡ High Frequency Trading AI Dashboard</h1>",
    unsafe_allow_html=True
)
st.markdown("<h4 style='text-align:center;'>Simulated BTC/USDT Trading with AI Insights</h4>", unsafe_allow_html=True)

# -------------------------------
# ✅ Sidebar: Trading Panel
# -------------------------------
st.sidebar.header("🛠 Trading Panel")
mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.radio("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", min_value=0.001, step=0.001)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
price_input = st.sidebar.number_input("Limit Price", min_value=0.0, value=0.0)

# -------------------------------
# ✅ Generate Simulated Price Data
# -------------------------------
if len(st.session_state.price_data) == 0:
    base_price = 30000
    for i in range(100):
        price = base_price + random.uniform(-100, 100)
        st.session_state.price_data.append({"time": datetime.now(), "price": price})

# Simulate price update
new_price = st.session_state.price_data[-1]["price"] + random.uniform(-30, 30)
st.session_state.price_data.append({"time": datetime.now(), "price": new_price})
price = new_price

# -------------------------------
# ✅ Trade Execution
# -------------------------------
def update_positions(side, qty, trade_price):
    if side == "BUY":
        total_cost = st.session_state.position * st.session_state.avg_price + qty * trade_price
        st.session_state.position += qty
        st.session_state.avg_price = total_cost / st.session_state.position
    elif side == "SELL" and st.session_state.position > 0:
        sell_qty = min(qty, st.session_state.position)
        pnl = (trade_price - st.session_state.avg_price) * sell_qty
        st.session_state.realized_pnl += pnl
        st.session_state.position -= sell_qty
        if st.session_state.position == 0:
            st.session_state.avg_price = 0

if st.sidebar.button("Submit Order"):
    trade_price = price_input if order_type == "LIMIT" else price
    if mode == "Simulation":
        update_positions(side, qty, trade_price)
        st.session_state.trade_log.append({
            "time": datetime.now(),
            "side": side,
            "qty": qty,
            "price": trade_price
        })
        st.success(f"Order Executed: {side} {qty} BTC at ${trade_price:.2f}")

# -------------------------------
# ✅ Layout
# -------------------------------
col1, col2 = st.columns(2)

# ✅ Price Chart
with col1:
    st.subheader("📈 Live BTC Price")
    if len(st.session_state.price_data) > 0:
        df_price = pd.DataFrame(st.session_state.price_data[-100:])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_price["time"], y=df_price["price"], mode="lines", name="BTC Price", line=dict(color="cyan", width=2)))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Waiting for price data...")

# ✅ Trade Log
with col2:
    st.subheader("📜 Trade Log")
    df_trades = pd.DataFrame(st.session_state.trade_log)
    if not df_trades.empty:
        st.dataframe(df_trades.tail(10))
    else:
        st.info("No trades yet.")

# -------------------------------
# ✅ P&L and Portfolio
# -------------------------------
st.subheader("📊 Realized & Unrealized P&L")
if st.session_state.position > 0:
    unrealized = (price - st.session_state.avg_price) * st.session_state.position
else:
    unrealized = 0.0

fig_pnl = go.Figure()
fig_pnl.add_trace(go.Indicator(
    mode="number+delta",
    value=st.session_state.realized_pnl,
    title={"text": "Realized P&L (USD)"},
    delta={"reference": 0, "relative": False},
    number={"prefix": "$", "font": {"size": 30}}
))
fig_pnl.add_trace(go.Indicator(
    mode="number+delta",
    value=unrealized,
    title={"text": "Unrealized P&L (USD)"},
    delta={"reference": 0, "relative": False},
    number={"prefix": "$", "font": {"size": 30}}
))
fig_pnl.update_layout(grid={"rows": 1, "columns": 2})
st.plotly_chart(fig_pnl, use_container_width=True)

# Portfolio Metrics Table
st.subheader("📊 Portfolio Metrics")
metrics = {
    "Open Position (BTC)": f"{st.session_state.position:.4f}",
    "Current Value (USD)": f"${price * st.session_state.position:.2f}",
    "Average Entry Price": f"${st.session_state.avg_price:.2f}"
}
df_metrics = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
st.table(df_metrics)

# -------------------------------
# ✅ AI Market Intelligence
# -------------------------------
st.subheader("🤖 AI Market Intelligence")

# Calculate basic indicators for reasoning
prices = [p["price"] for p in st.session_state.price_data[-50:]]
short_ma = np.mean(prices[-10:])
long_ma = np.mean(prices[-30:])
rsi = (np.mean(prices[-10:]) / np.mean(prices[-30:])) * 50 + 25  # simplified RSI

signal = ""
color = ""
reasoning = ""

if short_ma > long_ma and rsi > 60:
    signal = "BUY"
    color = "green"
    reasoning = f"""
    ✅ **Market is bullish** 📈  
    - Short MA ({short_ma:.2f}) > Long MA ({long_ma:.2f})  
    - RSI: {rsi:.2f} (>60 → overbought trend)  
    - Price momentum strong, potential upward continuation.  
    **Forecast:** BTC likely to test resistance in next 15–30 mins.
    """
elif short_ma < long_ma and rsi < 40:
    signal = "SELL"
    color = "red"
    reasoning = f"""
    ❌ **Market is bearish** 📉  
    - Short MA ({short_ma:.2f}) < Long MA ({long_ma:.2f})  
    - RSI: {rsi:.2f} (<40 → oversold trend)  
    - Downward pressure, risk of further decline.  
    **Forecast:** Possible breakdown if support fails in next 15–30 mins.
    """
else:
    signal = "HOLD"
    color = "yellow"
    reasoning = f"""
    ⚠️ **Market is neutral**  
    - MA signals mixed: Short MA ({short_ma:.2f}), Long MA ({long_ma:.2f})  
    - RSI: {rsi:.2f} (range-bound)  
    **Forecast:** Sideways movement expected. Avoid aggressive trades.
    """

st.markdown(
    f"<div style='background-color:black; padding:20px; border-radius:15px; text-align:center; border:3px solid {color}; box-shadow: 0 0 30px {color};'>"
    f"<h2 style='color:{color}; font-size:36px;'>Recommendation: {signal}</h2>"
    f"<p style='color:white; font-size:18px;'>{reasoning}</p>"
    "</div>",
    unsafe_allow_html=True
)

st.markdown("<p style='text-align:center;'>Refreshing every 5 seconds...</p>", unsafe_allow_html=True)

# Auto refresh
time.sleep(5)
st.experimental_rerun()
