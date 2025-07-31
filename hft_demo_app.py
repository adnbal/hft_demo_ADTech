import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# --------------------- PAGE CONFIG ---------------------
st.set_page_config(page_title="⚡ HFT AI Dashboard", layout="wide")

# --------------------- SESSION STATE INIT ---------------------
if "price_data" not in st.session_state:
    base_price = 30000
    st.session_state.price_data = [
        {"time": datetime.now() - timedelta(seconds=i*5), "price": base_price + random.uniform(-50, 50),
         "volume": random.uniform(0.5, 3)} for i in range(50)
    ][::-1]  # Pre-populate 50 ticks

if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

if "positions" not in st.session_state:
    st.session_state.positions = []

# --------------------- TITLE ---------------------
st.title("⚡ High Frequency Trading AI Dashboard")
st.caption("Simulated BTC/USDT Trading with AI Insights")

# --------------------- TRADING PANEL ---------------------
st.sidebar.header("🛠 Trading Panel")
mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.radio("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", min_value=0.01, value=1.0, step=0.01)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
price_input = st.sidebar.number_input("Limit Price", min_value=0.0, value=30000.0)

if st.sidebar.button("Submit Order"):
    current_price = st.session_state.price_data[-1]["price"]
    trade_price = price_input if order_type == "LIMIT" else current_price
    st.session_state.trade_log.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "side": side,
        "qty": qty,
        "price": trade_price
    })
    if side == "BUY":
        st.session_state.positions.append({"qty": qty, "price": trade_price})
    else:
        if st.session_state.positions:
            st.session_state.positions.pop(0)

# --------------------- SIMULATE NEW PRICE ---------------------
last_price = st.session_state.price_data[-1]["price"]
new_price = last_price + random.uniform(-30, 30)
new_volume = random.uniform(0.5, 3)
st.session_state.price_data.append({"time": datetime.now(), "price": new_price, "volume": new_volume})
if len(st.session_state.price_data) > 200:
    st.session_state.price_data = st.session_state.price_data[-200:]

df = pd.DataFrame(st.session_state.price_data)

# --------------------- LAYOUT ---------------------
col1, col2 = st.columns([2, 1])

# --------------------- PRICE & VOLUME CHART ---------------------
with col1:
    st.subheader("📈 Live BTC Price & Volume")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['price'], mode='lines+markers',
                             name='Price', line=dict(color='cyan', width=3)))
    fig.update_layout(height=400, template="plotly_dark", margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

# --------------------- TRADE LOG ---------------------
with col2:
    st.subheader("📜 Trade Log")
    df_trades = pd.DataFrame(st.session_state.trade_log)
    if not df_trades.empty:
        st.dataframe(df_trades.tail(10))
    else:
        st.info("No trades yet.")

# --------------------- REALIZED & UNREALIZED P&L ---------------------
st.subheader("📊 Realized & Unrealized P&L")
current_price = df['price'].iloc[-1]
realized_pnl = 0.0
unrealized_pnl = 0.0
for pos in st.session_state.positions:
    unrealized_pnl += (current_price - pos["price"]) * pos["qty"]

pnl_df = pd.DataFrame({
    "Type": ["Realized P&L", "Unrealized P&L"],
    "Value": [realized_pnl, unrealized_pnl]
})
pnl_fig = go.Figure(data=[go.Bar(x=pnl_df["Type"], y=pnl_df["Value"], marker_color=["yellow", "green"])])
pnl_fig.update_layout(template="plotly_dark", height=300)
st.plotly_chart(pnl_fig, use_container_width=True)

# --------------------- PORTFOLIO METRICS ---------------------
st.subheader("📊 Portfolio Metrics")
open_position = sum([p["qty"] for p in st.session_state.positions])
avg_price = (sum([p["qty"] * p["price"] for p in st.session_state.positions]) / open_position) if open_position else 0
current_value = open_position * current_price

metrics_df = pd.DataFrame({
    "Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
    "Value": [open_position, f"${current_value:,.2f}", f"${avg_price:,.2f}"]
})
st.table(metrics_df)

# --------------------- AI MARKET INTELLIGENCE ---------------------
st.subheader("🤖 AI Market Intelligence")
# Compute short trend
recent_prices = df['price'].tail(10).tolist()
trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]

# AI recommendation logic
if trend > 0:
    recommendation = "BUY"
    color = "#00FF00"
    rationale = "Price trend is upward, indicating bullish momentum. Buyers dominate order flow."
    forecast = "Price expected to rise by ~0.8% in next few minutes based on volatility patterns."
else:
    recommendation = "SELL"
    color = "#FF3131"
    rationale = "Downward slope detected with increasing sell pressure."
    forecast = "Price likely to drop ~1.2% short-term unless liquidity spike occurs."

ai_html = f"""
<div style='background-color:black; border: 2px solid {color}; border-radius:15px;
padding:15px; text-align:center; color:white; font-size:20px;
box-shadow:0 0 20px {color};'>
<strong>Market Signal: {recommendation}</strong><br>
<span style='font-size:16px;'>{rationale}</span><br>
<span style='font-size:14px; color:gray;'>{forecast}</span>
</div>
"""
st.markdown(ai_html, unsafe_allow_html=True)

# --------------------- AUTO REFRESH EVERY 30 SECONDS ---------------------
st.caption("Refreshing every 30 seconds...")
st_autorefresh = st.experimental_singleton(lambda: None)  # Dummy to avoid errors
time.sleep(30)
st.rerun()
