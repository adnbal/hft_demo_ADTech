import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="⚡ HFT AI Dashboard", layout="wide")
st.title("⚡ High Frequency Trading AI Dashboard")
st.caption("Simulated BTC/USDT Trading with AI Insights")

# -------------------- SESSION STATE --------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []

# -------------------- SIDEBAR --------------------
st.sidebar.header("🛠 Trading Panel")
mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.radio("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", min_value=1.0, step=1.0)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
limit_price = st.sidebar.number_input("Limit Price", min_value=1.0, step=0.01)
submit = st.sidebar.button("Submit Order")

# -------------------- SIMULATE PRICE STREAM --------------------
price = 30000 + np.random.randn() * 50  # base price with noise
volume = np.random.randint(10, 200)  # increased for visibility

st.session_state.price_data.append({"time": datetime.now(), "price": price, "volume": volume})
if len(st.session_state.price_data) > 500:
    st.session_state.price_data.pop(0)

# -------------------- EXECUTE ORDERS --------------------
if submit:
    trade_price = price if order_type == "MARKET" else limit_price
    st.session_state.trade_log.append({"time": datetime.now(), "side": side, "qty": qty, "price": trade_price})
    if side == "BUY":
        st.session_state.positions.append({"price": trade_price, "qty": qty})
    elif side == "SELL" and st.session_state.positions:
        sell_qty = qty
        while sell_qty > 0 and st.session_state.positions:
            pos = st.session_state.positions.pop(0)
            sell_qty -= pos["qty"]

# -------------------- LIVE PRICE & VOLUME CHART --------------------
st.subheader("📈 Live BTC Price & Volume")
df = pd.DataFrame(st.session_state.price_data)

fig = go.Figure()

# Price Line
fig.add_trace(go.Scatter(x=df['time'], y=df['price'], mode='lines', name='Price', line=dict(color='lime', width=2)))

# Volume Bars (secondary axis)
fig.add_trace(go.Bar(x=df['time'], y=df['volume'], name='Volume', marker_color='rgba(0, 200, 255, 0.6)', yaxis='y2'))

fig.update_layout(
    template="plotly_dark",
    height=400,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(title="Time"),
    yaxis=dict(title="Price (USD)", side="left"),
    yaxis2=dict(title="Volume", side="right", overlaying="y", showgrid=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)

# -------------------- TRADE LOG --------------------
st.subheader("📜 Trade Log")
df_trades = pd.DataFrame(st.session_state.trade_log)
if not df_trades.empty:
    st.dataframe(df_trades.tail(10), use_container_width=True)
else:
    st.write("No trades yet.")

# -------------------- REALIZED & UNREALIZED P&L (BIG KPI CARDS) --------------------
st.subheader("📊 Realized & Unrealized P&L")

realized_pnl = 0.0
unrealized_pnl = 0.0
current_price = price

for t in st.session_state.trade_log:
    if t["side"] == "SELL" and st.session_state.positions:
        realized_pnl += (t["price"] - st.session_state.positions[0]["price"]) * t["qty"]

for pos in st.session_state.positions:
    unrealized_pnl += (current_price - pos["price"]) * pos["qty"]

# KPI cards
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<h3 style='color:lime;'>Realized P&L (USD)</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:lime;'>${realized_pnl:,.2f}</h1>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<h3 style='color:yellow;'>Unrealized P&L (USD)</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:yellow;'>${unrealized_pnl:,.2f}</h1>", unsafe_allow_html=True)

# -------------------- PORTFOLIO METRICS --------------------
st.subheader("📊 Portfolio Metrics")
open_position = sum(pos["qty"] for pos in st.session_state.positions)
current_value = open_position * current_price
avg_entry_price = np.mean([pos["price"] for pos in st.session_state.positions]) if st.session_state.positions else 0

metrics = pd.DataFrame({
    "Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
    "Value": [open_position, f"${current_value:,.2f}", f"${avg_entry_price:,.2f}"]
})
st.table(metrics)

# -------------------- AI MARKET INTELLIGENCE --------------------
st.subheader("🤖 AI Market Intelligence")

if len(df) > 10:
    price_change = df['price'].iloc[-1] - df['price'].iloc[-10]
    if price_change > 0:
        signal = "BUY"
        reason = "Price trend is upward, indicating bullish momentum. Buyers dominate order flow."
        forecast = f"Price expected to rise by ~{abs(price_change/current_price)*100:.2f}% in next few minutes based on volatility patterns."
    else:
        signal = "SELL"
        reason = "Price trend is downward, indicating bearish pressure. Sellers dominate order flow."
        forecast = f"Price expected to drop by ~{abs(price_change/current_price)*100:.2f}% in next few minutes due to strong resistance levels."

    st.markdown(f"""
    <div style='padding:15px;border-radius:10px;background:{"#00ff00" if signal=="BUY" else "#ff0000"};color:black;font-size:20px;font-weight:bold;text-align:center;'>
        Market Signal: {signal}
    </div>
    """, unsafe_allow_html=True)
    st.write(reason)
    st.write(forecast)
else:
    st.write("WAIT")
    st.write("Insufficient data for prediction. Collecting more ticks...")

# -------------------- AUTO REFRESH EVERY 5 SECONDS --------------------
st.caption("Refreshing every 5 seconds...")
st_autorefresh(interval=5000, key="data_refresh")
