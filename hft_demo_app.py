import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import random
import time

# ---------------- SESSION STATE ----------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []

st.set_page_config(page_title="HFT AI Dashboard", layout="wide")

# ---------------- STYLES ----------------
st.markdown("""
<style>
.neon-card {
    background-color: #0e1117;
    padding: 15px;
    border-radius: 12px;
    color: white;
    font-size: 18px;
    text-shadow: 0 0 10px #00FF00;
    border: 2px solid #00FF00;
    box-shadow: 0 0 15px #00FF00;
}
.red-glow {
    border: 2px solid #FF0033;
    box-shadow: 0 0 15px #FF0033;
    text-shadow: 0 0 10px #FF0033;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("⚡ High Frequency Trading AI Dashboard")
st.caption("Simulated BTC/USDT Trading with AI Insights")

# ---------------- TRADING PANEL ----------------
st.sidebar.header("🛠 Trading Panel")
mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.radio("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", min_value=1, value=5)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
price_input = st.sidebar.number_input("Limit Price", min_value=0.0, value=0.0)

if st.sidebar.button("Submit Order"):
    current_price = st.session_state.price_data[-1]["price"] if st.session_state.price_data else 30000
    trade_price = price_input if order_type == "LIMIT" else current_price
    st.session_state.trade_log.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "side": side,
        "qty": qty,
        "price": trade_price
    })
    if side == "BUY":
        st.session_state.positions.append({"qty": qty, "price": trade_price})
    elif side == "SELL" and st.session_state.positions:
        st.session_state.positions.pop(0)

# ---------------- SIMULATED PRICE FEED ----------------
price = 30000 if not st.session_state.price_data else st.session_state.price_data[-1]["price"]
price += np.random.uniform(-50, 50)
volume = np.random.randint(50, 200)
st.session_state.price_data.append({
    "time": datetime.now().strftime("%H:%M:%S"),
    "price": price,
    "volume": volume
})
df = pd.DataFrame(st.session_state.price_data[-100:])

# ---------------- PRICE & VOLUME CHART ----------------
st.subheader("📈 Live BTC Price & Volume")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['time'], y=df['price'], mode='lines+markers',
                         name='Price', line=dict(color='lime', width=3)))
fig.add_trace(go.Bar(x=df['time'], y=df['volume'], name='Volume', yaxis='y2', opacity=0.3))
fig.update_layout(
    yaxis=dict(title="Price"),
    yaxis2=dict(title="Volume", overlaying='y', side='right'),
    template="plotly_dark", height=400
)
st.plotly_chart(fig, use_container_width=True)

# ---------------- TRADE LOG ----------------
st.subheader("📜 Trade Log")
if st.session_state.trade_log:
    st.dataframe(pd.DataFrame(st.session_state.trade_log).tail(10), height=200)
else:
    st.info("No trades yet.")

# ---------------- P&L ----------------
st.subheader("📊 Realized & Unrealized P&L")
realized_pnl = 0.0
unrealized_pnl = 0.0
current_price = price

for t in st.session_state.trade_log:
    if t["side"] == "SELL":
        realized_pnl += (t["price"] - st.session_state.positions[0]["price"]) * t["qty"] if st.session_state.positions else 0
for pos in st.session_state.positions:
    unrealized_pnl += (current_price - pos["price"]) * pos["qty"]

pnl_fig = go.Figure()
pnl_fig.add_trace(go.Indicator(mode="number+delta", value=realized_pnl, title="Realized P&L", delta={"reference": 0}))
pnl_fig.add_trace(go.Indicator(mode="number+delta", value=unrealized_pnl, title="Unrealized P&L", delta={"reference": 0}))
pnl_fig.update_layout(template="plotly_dark", height=200)
st.plotly_chart(pnl_fig, use_container_width=True)

# ---------------- PORTFOLIO METRICS ----------------
st.subheader("📊 Portfolio Metrics")
open_pos = sum([p["qty"] for p in st.session_state.positions])
avg_price = np.mean([p["price"] for p in st.session_state.positions]) if st.session_state.positions else 0
current_val = open_pos * current_price
metrics = pd.DataFrame({
    "Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
    "Value": [open_pos, f"${current_val:,.2f}", f"${avg_price:,.2f}"]
})
st.table(metrics)

# ---------------- AI MARKET INTELLIGENCE ----------------
st.subheader("🤖 AI Market Intelligence")

# Generate AI Recommendation
if len(df) > 5:
    price_change = df['price'].iloc[-1] - df['price'].iloc[-5]
    signal = "BUY" if price_change > 0 else "SELL"
    color_class = "" if signal == "BUY" else " red-glow"
    expected_move = round(np.random.uniform(0.3, 1.2), 2)
    forecast_price = df['price'].iloc[-1] * (1 + (expected_move / 100 if signal == "BUY" else -expected_move / 100))
    rationale = "Price trend is upward, indicating bullish momentum." if signal == "BUY" else "Bearish trend detected; sellers dominate."
    confidence = random.choice(["High", "Medium", "Low"])

    st.markdown(f"""
    <div class="neon-card{color_class}">
        <b>Market Signal:</b> {signal} <br>
        <b>Expected Move:</b> {'+' if signal == 'BUY' else '-'}{expected_move}% <br>
        <b>Forecast Price:</b> ${forecast_price:,.2f} <br>
        <b>Rationale:</b> {rationale} <br>
        <b>Confidence:</b> {confidence}
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Insufficient data for prediction. Collecting more ticks...")

# ---------------- AUTO REFRESH EVERY 5 SECONDS ----------------
st.caption("Refreshing every 5 seconds...")
time.sleep(5)
st.rerun()
