import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="⚡ High Frequency Trading AI Dashboard", layout="wide")
st.title("⚡ High Frequency Trading AI Dashboard")
st.caption("Simulated BTC/USDT Trading with AI Insights")

# ---------------------- SESSION STATE INIT ----------------------
if 'price_data' not in st.session_state:
    st.session_state.price_data = []
if 'trade_log' not in st.session_state:
    st.session_state.trade_log = []
if 'position' not in st.session_state:
    st.session_state.position = 0
if 'realized_pnl' not in st.session_state:
    st.session_state.realized_pnl = 0
if 'pnl_history' not in st.session_state:
    st.session_state.pnl_history = []

# ---------------------- SIDEBAR: TRADING PANEL ----------------------
st.sidebar.header("🛠 Trading Panel")
mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.radio("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", min_value=0.001, value=0.01, step=0.001)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
price_input = st.sidebar.number_input("Limit Price", min_value=10000.0, value=30000.0, step=100.0)

# ---------------------- PRICE SIMULATION ----------------------
def get_live_price():
    base_price = 30000
    price = round(base_price + np.random.randn() * 100, 2)
    bid = price - np.random.uniform(10, 15)
    ask = price + np.random.uniform(10, 15)
    return price, bid, ask

current_price, bid_price, ask_price = get_live_price()
st.session_state.price_data.append({"time": datetime.now(), "price": current_price, "bid": bid_price, "ask": ask_price})

# ---------------------- FUNCTIONS ----------------------
def update_positions(side, qty, trade_price):
    if side == "BUY":
        st.session_state.position += qty
        st.session_state.realized_pnl -= qty * trade_price
    elif side == "SELL":
        st.session_state.position -= qty
        st.session_state.realized_pnl += qty * trade_price
    unrealized = st.session_state.position * current_price
    st.session_state.pnl_history.append({
        "time": datetime.now(),
        "realized": st.session_state.realized_pnl,
        "unrealized": unrealized
    })

# ---------------------- EXECUTE ORDER ----------------------
if st.sidebar.button("Submit Order"):
    trade_price = price_input if order_type == "LIMIT" else current_price
    if mode == "Simulation":
        update_positions(side, qty, trade_price)
        st.session_state.trade_log.append({
            "time": datetime.now(),
            "side": side,
            "qty": qty,
            "price": trade_price
        })
        st.success(f"✅ Order Executed: {side} {qty} BTC at ${trade_price}")
    else:
        st.error("❌ Live trading not supported in demo mode")

# ---------------------- MAIN LAYOUT ----------------------
col1, col2 = st.columns(2)

# ✅ PRICE & BID-ASK CHART
with col1:
    st.subheader("📈 Live BTC Price & Spread")
    if len(st.session_state.price_data) > 0:
        df_price = pd.DataFrame(st.session_state.price_data[-100:])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_price["time"], y=df_price["price"], mode="lines", name="Mid Price", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=df_price["time"], y=df_price["bid"], mode="lines", name="Bid", line=dict(color="green", dash="dot")))
        fig.add_trace(go.Scatter(x=df_price["time"], y=df_price["ask"], mode="lines", name="Ask", line=dict(color="red", dash="dot")))
        fig.update_layout(title="BTC/USDT Price with Bid-Ask Spread", xaxis_title="Time", yaxis_title="Price (USD)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Waiting for price data...")

# ✅ TRADE LOG
with col2:
    st.subheader("📜 Trade Log")
    df_trades = pd.DataFrame(st.session_state.trade_log)
    if not df_trades.empty:
        st.dataframe(df_trades.tail(10))
    else:
        st.write("No trades yet.")

# ---------------------- AI RECOMMENDATION ----------------------
st.markdown("---")
st.subheader("🤖 AI Recommendation")
if len(st.session_state.price_data) >= 2:
    last_price = st.session_state.price_data[-1]["price"]
    prev_price = st.session_state.price_data[-2]["price"]
    if last_price > prev_price:
        rec = "Market is bullish 📈 → Consider BUY"
    elif last_price < prev_price:
        rec = "Market is bearish 📉 → Consider SELL"
    else:
        rec = "Market is stable → Hold"
else:
    rec = "Insufficient data to analyze."
st.info(rec)

# ---------------------- PORTFOLIO METRICS ----------------------
st.markdown("---")
st.subheader("📊 Portfolio Metrics")
current_position = st.session_state.position
avg_price = np.mean([t["price"] for t in st.session_state.trade_log]) if st.session_state.trade_log else 0
current_value = current_position * current_price
st.metric("Open Position (BTC)", f"{current_position:.4f}")
st.metric("Current Value (USD)", f"${current_value:,.2f}")
st.metric("Average Entry Price", f"${avg_price:,.2f}")

# ---------------------- PNL CHART WITH TWO LINES ----------------------
if len(st.session_state.pnl_history) > 0:
    df_pnl = pd.DataFrame(st.session_state.pnl_history)
    fig_pnl = go.Figure()
    fig_pnl.add_trace(go.Scatter(x=df_pnl["time"], y=df_pnl["realized"], mode="lines", name="Realized PnL", line=dict(color="green")))
    fig_pnl.add_trace(go.Scatter(x=df_pnl["time"], y=df_pnl["unrealized"], mode="lines", name="Unrealized PnL", line=dict(color="yellow")))
    fig_pnl.update_layout(title="Realized vs Unrealized PnL", xaxis_title="Time", yaxis_title="PnL (USD)")
    st.plotly_chart(fig_pnl, use_container_width=True)

# ---------------------- AUTO REFRESH ----------------------
time.sleep(5)
st.rerun()
