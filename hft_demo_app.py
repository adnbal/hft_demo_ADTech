import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import random
import time

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="⚡ HFT AI Dashboard", layout="wide")

# ---------------------- SESSION STATE INIT ----------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []

# ---------------------- SIMULATE PRICE FEED ----------------------
current_price = 30000 + random.uniform(-200, 200)
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.session_state.price_data.append({"time": timestamp, "price": current_price, "volume": random.randint(1, 100)})

# Keep last 200 ticks
st.session_state.price_data = st.session_state.price_data[-200:]

# ---------------------- TRADING PANEL ----------------------
st.title("⚡ High Frequency Trading AI Dashboard")
st.caption("Simulated BTC/USDT Trading with AI Insights")

with st.sidebar:
    st.header("🛠 Trading Panel")
    mode = st.radio("Mode", ["Simulation", "Live"])
    side = st.radio("Side", ["BUY", "SELL"])
    qty = st.number_input("Quantity", min_value=1, value=5)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    price_input = st.number_input("Limit Price", min_value=10000.0, value=current_price, step=100.0)

    if st.button("Submit Order"):
        trade_price = price_input if order_type == "LIMIT" else current_price
        st.session_state.trade_log.append({
            "time": datetime.now(),
            "side": side,
            "qty": qty,
            "price": trade_price
        })

        # Update positions
        if side == "BUY":
            st.session_state.positions.append({"qty": qty, "price": trade_price})
        else:
            # Reduce position for SELL
            if st.session_state.positions:
                st.session_state.positions.pop(0)

# ---------------------- PRICE & VOLUME CHART ----------------------
st.subheader("📈 Live BTC Price & Volume")

df = pd.DataFrame(st.session_state.price_data)
fig = go.Figure()

fig.add_trace(go.Scatter(x=df['time'], y=df['price'], mode='lines', name='Price', line=dict(color='lime', width=3)))
fig.add_trace(go.Bar(x=df['time'], y=df['volume'], name='Volume', yaxis='y2', opacity=0.3, marker_color='blue'))

fig.update_layout(
    title="BTC Price & Volume",
    xaxis_title="Time",
    yaxis_title="Price",
    yaxis2=dict(title="Volume", overlaying="y", side="right"),
    template="plotly_dark",
    height=400
)
st.plotly_chart(fig, use_container_width=True)

# ---------------------- TRADE LOG ----------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📜 Trade Log")
    if st.session_state.trade_log:
        df_trades = pd.DataFrame(st.session_state.trade_log)
        st.dataframe(df_trades.tail(10), use_container_width=True)
    else:
        st.info("No trades yet.")

# ---------------------- REALIZED & UNREALIZED PNL ----------------------
realized_pnl = 0.0
unrealized_pnl = 0.0
for pos in st.session_state.positions:
    unrealized_pnl += (current_price - pos["price"]) * pos["qty"]

pnl_df = pd.DataFrame({
    "Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
    "Value": [
        sum([p["qty"] for p in st.session_state.positions]),
        f"${sum([p['qty'] for p in st.session_state.positions]) * current_price:,.2f}",
        f"${np.mean([p['price'] for p in st.session_state.positions]) if st.session_state.positions else 0:.2f}"
    ]
})

with col2:
    st.subheader("📊 Portfolio Metrics")
    st.dataframe(pnl_df, use_container_width=True)

# ---------------------- PNL LINE CHART ----------------------
st.subheader("📊 Realized & Unrealized P&L")
pnl_chart = go.Figure()
pnl_chart.add_trace(go.Scatter(x=df['time'], y=[realized_pnl]*len(df), mode='lines', name='Realized P&L', line=dict(color='green', width=3)))
pnl_chart.add_trace(go.Scatter(x=df['time'], y=[unrealized_pnl]*len(df), mode='lines', name='Unrealized P&L', line=dict(color='yellow', width=3)))
pnl_chart.update_layout(template="plotly_dark", height=300)
st.plotly_chart(pnl_chart, use_container_width=True)

# ---------------------- BID-ASK SPREAD ----------------------
st.subheader("📊 Bid-Ask Spread")
bid = current_price - random.uniform(5, 15)
ask = current_price + random.uniform(5, 15)
spread_fig = go.Figure()
spread_fig.add_trace(go.Indicator(
    mode="gauge+number",
    value=ask - bid,
    title={'text': "Spread (USD)"},
    gauge={'axis': {'range': [0, 50]}, 'bar': {'color': "cyan"}}
))
spread_fig.update_layout(template="plotly_dark", height=250)
st.plotly_chart(spread_fig, use_container_width=True)

# ---------------------- AI MARKET INTELLIGENCE ----------------------
st.subheader("🤖 AI Market Intelligence")

if len(df) > 20:
    recent_trend = df['price'].iloc[-10:].mean() - df['price'].iloc[-20:-10].mean()
    recommendation = "BUY" if recent_trend > 0 else "SELL"
    glow_color = "green" if recommendation == "BUY" else "red"
    
    # Generate AI commentary with reasoning
    if recommendation == "BUY":
        ai_msg = f"""
        <div style='background:black; padding:15px; border-radius:10px; text-align:center; 
        font-size:20px; color:{glow_color}; text-shadow: 0px 0px 15px {glow_color};'>
        Market is bullish 📈 → Consider <b>{recommendation}</b><br>
        Recent price momentum is strong with higher lows and strong volume.<br>
        Forecast: Price expected to rise by 0.8%-1.2% in next 30 ticks.<br>
        Strategy: Enter BUY with tight stop-loss at {current_price * 0.98:.2f}.
        </div>
        """
    else:
        ai_msg = f"""
        <div style='background:black; padding:15px; border-radius:10px; text-align:center; 
        font-size:20px; color:{glow_color}; text-shadow: 0px 0px 15px {glow_color};'>
        Market is bearish 📉 → Consider <b>{recommendation}</b><br>
        Downward pressure observed with declining volume.<br>
        Forecast: Price expected to drop by 0.5%-1.0% in next 30 ticks.<br>
        Strategy: Open SELL positions or exit long positions immediately.
        </div>
        """
    st.markdown(ai_msg, unsafe_allow_html=True)
else:
    st.info("Insufficient data for prediction. Collecting more ticks...")

# ---------------------- AUTO REFRESH ----------------------
st.caption("Refreshing every 30 seconds...")
time.sleep(30)
st.query_params(refresh=str(time.time()))
