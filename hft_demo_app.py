import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="HFT AI Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    body { background-color: #0e1117; color: white; }
    .neon-buy {
        color: #00FF00; font-size: 22px; font-weight: bold;
        text-shadow: 0 0 10px #00FF00, 0 0 20px #00FF00, 0 0 30px #00FF00;
        padding: 15px; border-radius: 10px; text-align: center;
    }
    .neon-sell {
        color: #FF0000; font-size: 22px; font-weight: bold;
        text-shadow: 0 0 10px #FF0000, 0 0 20px #FF0000, 0 0 30px #FF0000;
        padding: 15px; border-radius: 10px; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Auto refresh every 5 sec
st_autorefresh(interval=5000, key="data_refresh")

# ---------------------- SESSION STATE INIT ----------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []

# ---------------------- SIMULATE PRICE DATA ----------------------
def generate_price():
    last_price = st.session_state.price_data[-1]["price"] if st.session_state.price_data else 30000
    new_price = last_price + np.random.randint(-150, 150)
    return round(new_price, 2)

# Add new price data
st.session_state.price_data.append({"time": datetime.now(), "price": generate_price()})
df_price = pd.DataFrame(st.session_state.price_data[-100:])

# ---------------------- SIDEBAR ----------------------
st.sidebar.header("🛠 Trading Panel")
mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.radio("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", min_value=0.01, max_value=5.0, step=0.01, value=1.0)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
limit_price = st.sidebar.number_input("Limit Price", value=30000.0, step=100.0)

if st.sidebar.button("Submit Order"):
    trade_price = df_price["price"].iloc[-1] if order_type == "MARKET" else limit_price
    st.session_state.trade_log.append({"time": datetime.now(), "side": side, "qty": qty, "price": trade_price})
    if side == "BUY":
        st.session_state.positions.append({"qty": qty, "price": trade_price})
    else:
        if st.session_state.positions:
            st.session_state.positions.pop(0)

# ---------------------- MAIN TITLE ----------------------
st.title("⚡ High Frequency Trading AI Dashboard")
st.caption("Simulated BTC/USDT Trading with AI Insights")

# ---------------------- LIVE PRICE CHART ----------------------
st.subheader("📈 Live BTC Price")
if not df_price.empty:
    fig = go.Figure(data=[go.Candlestick(x=df_price["time"],
                                         open=df_price["price"]-20,
                                         high=df_price["price"]+50,
                                         low=df_price["price"]-50,
                                         close=df_price["price"],
                                         increasing_line_color='green',
                                         decreasing_line_color='red')])
    fig.update_layout(height=350, margin=dict(l=0,r=0,t=30,b=0), paper_bgcolor="#0e1117", font_color="white")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Waiting for price data...")

# ---------------------- TRADE LOG ----------------------
col1, col2 = st.columns(2)
with col1:
    st.subheader("📜 Trade Log")
    if st.session_state.trade_log:
        df_trades = pd.DataFrame(st.session_state.trade_log)
        st.dataframe(df_trades.tail(10))
    else:
        st.write("No trades yet.")

# ---------------------- P&L SECTION ----------------------
with col2:
    st.subheader("📊 Realized & Unrealized P&L")
    current_price = df_price["price"].iloc[-1]
    realized_pnl = sum([t.get("PnL", 0) for t in st.session_state.trade_log])
    unrealized_pnl = sum([(current_price - pos["price"]) * pos["qty"] for pos in st.session_state.positions])

    fig_pnl = go.Figure()
    fig_pnl.add_trace(go.Indicator(mode="number+delta",
                                   value=unrealized_pnl,
                                   title={"text": "Unrealized P&L (USD)"},
                                   number={"prefix": "$"},
                                   delta={"reference": 0}))
    fig_pnl.update_layout(height=250, paper_bgcolor="#0e1117", font_color="white")
    st.plotly_chart(fig_pnl, use_container_width=True)

# ---------------------- PORTFOLIO METRICS ----------------------
st.subheader("📊 Portfolio Metrics")
open_pos = sum([p["qty"] for p in st.session_state.positions])
avg_price = np.mean([p["price"] for p in st.session_state.positions]) if st.session_state.positions else 0
current_value = open_pos * current_price
metrics = pd.DataFrame({"Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
                        "Value": [round(open_pos, 4), f"${current_value:,.2f}", f"${avg_price:,.2f}"]})
st.table(metrics)

# ---------------------- AI MARKET INSIGHT ----------------------
st.subheader("🤖 AI Market Intelligence")
if len(df_price) > 10:
    recent_prices = df_price["price"].tolist()[-10:]
    trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
    if trend > 0:
        recommendation = "BUY"
        reason = "Market trend is bullish with upward momentum and strong support levels."
    else:
        recommendation = "SELL"
        reason = "Market shows bearish sentiment with resistance pushing prices down."
    # Neon recommendation
    st.markdown(f"<div class='neon-{recommendation.lower()}'>Recommendation: {recommendation} <br>Reason: {reason}</div>", unsafe_allow_html=True)
else:
    st.write("Waiting for more price data to generate AI insights...")

