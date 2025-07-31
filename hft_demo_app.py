import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import random
from streamlit_autorefresh import st_autorefresh

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="⚡ HFT AI Dashboard", layout="wide")

# ---------------------- SESSION STATE INIT ----------------------
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

# ---------------------- HEADER ----------------------
st.markdown("<h1 style='color:#00f3ff; text-shadow: 0 0 15px #00f3ff;'>⚡ High Frequency Trading AI Dashboard</h1>", unsafe_allow_html=True)
st.caption("Simulated BTC/USDT Trading with AI Insights")

# ---------------------- SIDEBAR: TRADING PANEL ----------------------
st.sidebar.markdown("<h2 style='color:#39ff14;'>🛠 Trading Panel</h2>", unsafe_allow_html=True)

mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.radio("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", min_value=0.001, step=0.001, value=0.01)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
price_input = st.sidebar.number_input("Limit Price", min_value=0.0, value=0.0, step=0.1)

# ---------------------- PRICE SIMULATION ----------------------
def simulate_price():
    if not st.session_state.price_data:
        return 30000.0
    last_price = st.session_state.price_data[-1]["price"]
    return round(last_price * (1 + random.uniform(-0.001, 0.0015)), 2)

price = simulate_price()
st.session_state.price_data.append({"time": datetime.now(), "price": price, "bid": price - 5, "ask": price + 5})

# ---------------------- EXECUTE TRADE ----------------------
def update_positions(side, qty, trade_price):
    if side == "BUY":
        total_cost = st.session_state.position * st.session_state.avg_price + qty * trade_price
        st.session_state.position += qty
        st.session_state.avg_price = total_cost / st.session_state.position
    else:
        if qty > st.session_state.position:
            qty = st.session_state.position
        pnl = (trade_price - st.session_state.avg_price) * qty
        st.session_state.realized_pnl += pnl
        st.session_state.position -= qty
        if st.session_state.position == 0:
            st.session_state.avg_price = 0.0

if st.sidebar.button("Submit Order"):
    trade_price = price_input if order_type == "LIMIT" else price
    update_positions(side, qty, trade_price)
    st.session_state.trade_log.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "side": side,
        "qty": qty,
        "price": trade_price
    })
    st.success(f"✅ {side} {qty} BTC at {trade_price} USD")

# ---------------------- MAIN DASHBOARD ----------------------
col1, col2 = st.columns(2)

# ---------------------- PRICE CHART ----------------------
with col1:
    st.subheader("📈 Live BTC Price")
    df_price = pd.DataFrame(st.session_state.price_data[-100:])
    if not df_price.empty:
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=df_price["time"], y=df_price["price"], mode="lines+markers", name="BTC Price", line=dict(color="#00f3ff", width=3)))
        fig_price.update_layout(template="plotly_dark", height=300)
        st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.info("Waiting for price data...")

# ---------------------- TRADE LOG ----------------------
with col2:
    st.subheader("📜 Trade Log")
    df_trades = pd.DataFrame(st.session_state.trade_log)
    st.dataframe(df_trades.tail(10) if not df_trades.empty else "No trades yet.")

# ---------------------- BID-ASK SPREAD ----------------------
st.subheader("📊 Bid-Ask Spread")
if not df_price.empty:
    fig_spread = go.Figure()
    fig_spread.add_trace(go.Scatter(x=df_price["time"], y=df_price["bid"], mode="lines", name="Bid", line=dict(color="yellow")))
    fig_spread.add_trace(go.Scatter(x=df_price["time"], y=df_price["ask"], mode="lines", name="Ask", line=dict(color="orange")))
    fig_spread.update_layout(template="plotly_dark", height=250)
    st.plotly_chart(fig_spread, use_container_width=True)

# ---------------------- REALIZED & UNREALIZED PNL ----------------------
st.subheader("📊 Realized & Unrealized P&L")
if not df_price.empty:
    unrealized_pnl = (price - st.session_state.avg_price) * st.session_state.position
    pnl_fig = go.Figure()
    pnl_fig.add_trace(go.Scatter(x=df_price["time"], y=[st.session_state.realized_pnl]*len(df_price), name="Realized P&L", line=dict(color="green", dash="dot")))
    pnl_fig.add_trace(go.Scatter(x=df_price["time"], y=[unrealized_pnl]*len(df_price), name="Unrealized P&L", line=dict(color="yellow", dash="dot")))
    pnl_fig.update_layout(template="plotly_dark", height=250)
    st.plotly_chart(pnl_fig, use_container_width=True)

# ---------------------- PORTFOLIO METRICS ----------------------
st.subheader("📊 Portfolio Metrics")
metrics_df = pd.DataFrame({
    "Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
    "Value": [round(st.session_state.position, 4),
              f"${round(st.session_state.position * price, 2)}",
              f"${round(st.session_state.avg_price, 2)}"]
})
st.table(metrics_df)

# ---------------------- AI MARKET INTELLIGENCE ----------------------
st.subheader("🤖 AI Market Intelligence")
if len(st.session_state.price_data) > 10:
    recent_prices = [p["price"] for p in st.session_state.price_data[-10:]]
    avg_recent = np.mean(recent_prices)
    trend = "bullish 📈" if recent_prices[-1] > avg_recent else "bearish 📉"
    
    # Forecast with random sentiment for demo
    future_price = price * (1 + random.uniform(-0.02, 0.03))
    if trend == "bullish 📈":
        recommendation = "BUY"
        color = "#39ff14"  # Neon Green
        reasoning = f"Market trend is bullish with upward momentum. Average recent price: {avg_recent:.2f}. Short-term forecast suggests price could rise towards {future_price:.2f}. High trading volume supports upward trend."
    else:
        recommendation = "SELL"
        color = "#ff073a"  # Neon Red
        reasoning = f"Market trend is bearish with downward signals. Average recent price: {avg_recent:.2f}. Forecast indicates possible dip towards {future_price:.2f}. Reduced buying pressure detected."

    st.markdown(f"""
    <div style='background-color:#111; padding:20px; border-radius:12px; text-align:center;
    box-shadow:0 0 20px {color}; color:{color}; font-size:24px; font-weight:bold;'>
    {recommendation} SIGNAL
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<p style='color:white; font-size:16px;'>{reasoning}</p>", unsafe_allow_html=True)
else:
    st.info("Waiting for more price data to generate AI insights...")

# ---------------------- AUTO REFRESH ----------------------
st.caption("Refreshing every 5 seconds...")
st_autorefresh(interval=5000, key="refresh")
