import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
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
    return round(base_price + np.random.randn() * 100, 2)

# Update price list
current_price = get_live_price()
st.session_state.price_data.append({"time": datetime.now(), "price": current_price})

# ---------------------- FUNCTIONS ----------------------
def update_positions(side, qty, trade_price):
    if side == "BUY":
        st.session_state.position += qty
    elif side == "SELL":
        st.session_state.position -= qty
    pnl = st.session_state.position * trade_price
    st.session_state.pnl_history.append({"time": datetime.now(), "pnl": pnl})

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

# ✅ PRICE CHART
with col1:
    st.subheader("📈 Live BTC Price")
    if len(st.session_state.price_data) > 0:
        df_price = pd.DataFrame(st.session_state.price_data[-100:])
        fig_price = px.line(df_price, x="time", y="price", title="BTC/USDT Price Trend")
        st.plotly_chart(fig_price, use_container_width=True)
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

# ---------------------- PNL CHART ----------------------
if len(st.session_state.pnl_history) > 0:
    df_pnl = pd.DataFrame(st.session_state.pnl_history)
    fig_pnl = px.line(df_pnl, x="time", y="pnl", title="PnL Over Time")
    st.plotly_chart(fig_pnl, use_container_width=True)

# ---------------------- AUTO REFRESH ----------------------
st_autorefresh = st.empty()
st_autorefresh.text("Refreshing every 5 seconds...")
time.sleep(5)
st.experimental_rerun()
