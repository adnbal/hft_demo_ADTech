import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time
from datetime import datetime

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="⚡ HFT AI Dashboard", layout="wide")
st.markdown("<h1 style='text-align:center; color:cyan;'>⚡ High Frequency Trading AI Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<style>body {background-color:#0E1117; color:white;} .stButton>button{background-color:#00FF00; color:black; font-weight:bold;}</style>", unsafe_allow_html=True)

# ---------------------- INITIALIZE SESSION STATE ----------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []

# ---------------------- SIDEBAR CONTROLS ----------------------
st.sidebar.header("🛠 Trading Panel")
mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.radio("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", min_value=1.0, value=1.0, step=1.0)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
price_input = st.sidebar.number_input("Limit Price", min_value=10000.0, value=30000.0, step=100.0)

if st.sidebar.button("Submit Order"):
    current_price = st.session_state.price_data[-1]["price"] if st.session_state.price_data else 30000
    trade_price = price_input if order_type == "LIMIT" else current_price

    # Record Trade
    st.session_state.trade_log.append({
        "time": datetime.now(),
        "side": side,
        "qty": qty,
        "price": trade_price
    })

    # Update Positions
    if side == "BUY":
        st.session_state.positions.append({"qty": qty, "price": trade_price})
    elif side == "SELL":
        if st.session_state.positions:
            st.session_state.positions.pop(0)

# ---------------------- PRICE SIMULATION ----------------------
if len(st.session_state.price_data) == 0:
    base_price = 30000
else:
    base_price = st.session_state.price_data[-1]["price"]

new_price = base_price + random.uniform(-50, 50)
volume = random.randint(1, 10)
st.session_state.price_data.append({
    "time": datetime.now(),
    "price": new_price,
    "volume": volume
})

# Convert to DataFrame
df = pd.DataFrame(st.session_state.price_data)

# ---------------------- LAYOUT ----------------------
col1, col2 = st.columns([3, 2])

# ---------------------- PRICE & VOLUME CHART ----------------------
with col1:
    st.subheader("📈 Live BTC Price & Volume")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=df['time'], y=df['price'], mode='lines+markers',
        name='Price', line=dict(color='lime', width=3)
    ), secondary_y=False)

    fig.add_trace(go.Bar(
        x=df['time'], y=df['volume'], name='Volume',
        marker_color='rgba(0,255,0,0.4)'
    ), secondary_y=True)

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        height=450
    )
    fig.update_yaxes(title_text="Price (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Volume", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------- TRADE LOG ----------------------
with col2:
    st.subheader("📜 Trade Log")
    df_trades = pd.DataFrame(st.session_state.trade_log)
    if not df_trades.empty:
        st.dataframe(df_trades.tail(10))
    else:
        st.write("No trades yet.")

# ---------------------- P&L SECTION ----------------------
st.subheader("📊 Realized & Unrealized P&L")
current_price = df['price'].iloc[-1]
realized_pnl = 0.0
unrealized_pnl = sum([(current_price - pos["price"]) * pos["qty"] for pos in st.session_state.positions])

pnl_chart = go.Figure()
pnl_chart.add_trace(go.Indicator(
    mode="number+delta",
    value=unrealized_pnl,
    delta={'reference': 0},
    title={"text": "Unrealized P&L (USD)"},
    number={'font': {'size': 40, 'color': 'lime' if unrealized_pnl >= 0 else 'red'}}
))
pnl_chart.update_layout(template="plotly_dark", height=250)
st.plotly_chart(pnl_chart, use_container_width=True)

# ---------------------- PORTFOLIO METRICS ----------------------
st.subheader("📊 Portfolio Metrics")
open_position = sum([pos["qty"] for pos in st.session_state.positions])
avg_entry = np.mean([pos["price"] for pos in st.session_state.positions]) if st.session_state.positions else 0
st.table(pd.DataFrame({
    "Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
    "Value": [open_position, f"${open_position * current_price:,.2f}", f"${avg_entry:,.2f}"]
}))

# ---------------------- AI RECOMMENDATION ----------------------
st.subheader("🤖 AI Market Intelligence")
if len(df) > 10:
    price_change = (df['price'].iloc[-1] - df['price'].iloc[-10]) / df['price'].iloc[-10] * 100
    if price_change > 0.2:
        recommendation = "BUY"
        rationale = f"Market is bullish 📈 → Price increased by {price_change:.2f}% in last 10 ticks. Strong momentum suggests an uptrend."
    elif price_change < -0.2:
        recommendation = "SELL"
        rationale = f"Market is bearish 📉 → Price dropped by {price_change:.2f}% in last 10 ticks. Possible downward pressure ahead."
    else:
        recommendation = "HOLD"
        rationale = "Market is stable → Minimal price change detected. Low volatility indicates sideways movement."
else:
    recommendation = "WAIT"
    rationale = "Insufficient data for prediction. Collecting more ticks..."

# Neon Glow Style for Recommendation
color = "lime" if recommendation == "BUY" else "red" if recommendation == "SELL" else "yellow"
st.markdown(f"""
<div style="padding:15px; border-radius:10px; background-color:black; border:2px solid {color}; text-align:center; font-size:24px; color:{color}; text-shadow: 0 0 20px {color};">
<strong>{recommendation}</strong><br><span style="font-size:16px; color:white;">{rationale}</span>
</div>
""", unsafe_allow_html=True)

# ---------------------- AUTO REFRESH ----------------------
st.caption("Refreshing every 5 seconds...")
time.sleep(5)
st.experimental_set_query_params(refresh=str(time.time()))
