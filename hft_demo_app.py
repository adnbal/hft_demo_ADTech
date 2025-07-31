import streamlit as st
import pandas as pd
import random
import time
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide", page_title="HFT AI Dashboard")

# ---------------------- CSS Styling ----------------------
st.markdown("""
    <style>
    body {
        background-color: black;
    }
    .left-panel, .right-panel {
        background-color: #2c2c2c;
        padding: 15px;
        border: 2px solid white;
        border-radius: 10px;
        height: 100vh;
    }
    .middle-panel {
        background-color: black;
        padding: 15px;
    }
    @keyframes neon-flash-green {
        0%, 100% {box-shadow: 0 0 10px #39ff14, 0 0 20px #39ff14;}
        50% {box-shadow: 0 0 30px #00ff00, 0 0 60px #00ff00;}
    }
    @keyframes neon-flash-red {
        0%, 100% {box-shadow: 0 0 10px #ff073a, 0 0 20px #ff073a;}
        50% {box-shadow: 0 0 30px #ff0000, 0 0 60px #ff0000;}
    }
    .neon-green {
        animation: neon-flash-green 1.5s infinite alternate;
        color: #39ff14;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        padding: 10px;
        border-radius: 8px;
    }
    .neon-red {
        animation: neon-flash-red 1.5s infinite alternate;
        color: #ff073a;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------- Session State ----------------------
if 'price_data' not in st.session_state:
    st.session_state.price_data = []
if 'trade_log' not in st.session_state:
    st.session_state.trade_log = []
if 'positions' not in st.session_state:
    st.session_state.positions = []

# ---------------------- Simulate Live Price ----------------------
price = 30000 + random.uniform(-100, 100)
st.session_state.price_data.append((datetime.now(), price, random.randint(50, 200)))

# ---------------------- AI Market Intelligence ----------------------
def ai_market_signal():
    prices = [p[1] for p in st.session_state.price_data[-10:]]
    if len(prices) < 3:
        return "WAIT", "Insufficient data for prediction. Collecting more ticks..."
    avg = sum(prices) / len(prices)
    trend = prices[-1] - prices[0]
    if trend > 0:
        return "BUY", "Market Signal: BUY\nPrice trend is upward, strong bullish momentum. Expect +0.8% rise in short term."
    elif trend < 0:
        return "SELL", "Market Signal: SELL\nDowntrend forming, sellers dominant. Expect ~0.5% drop based on volatility."
    else:
        return "HOLD", "Market neutral. No strong signals detected."
    
ai_signal, ai_text = ai_market_signal()
neon_class = "neon-green" if ai_signal == "BUY" else "neon-red" if ai_signal == "SELL" else "neon-green"

# ---------------------- Layout ----------------------
left, middle, right = st.columns([1.5, 3, 1.5])

# -------- LEFT PANEL: AI Intelligence --------
with left:
    st.markdown(f"<div class='{neon_class}'>🤖 AI Market Intelligence</div>", unsafe_allow_html=True)
    st.write(ai_text)

# -------- MIDDLE PANEL: Price & P&L Charts --------
with middle:
    st.markdown(f"<div class='{neon_class}'>⚡ High Frequency Trading AI Dashboard</div>", unsafe_allow_html=True)

    # Price & Volume Chart
    df = pd.DataFrame(st.session_state.price_data, columns=["time", "price", "volume"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['price'], mode='lines', name='Price', line=dict(color='lime')))
    fig.add_trace(go.Bar(x=df['time'], y=df['volume'], name='Volume', marker_color='blue', yaxis='y2'))
    fig.update_layout(title="Live BTC Price & Volume", xaxis_title="Time",
                      yaxis=dict(title="Price", side="left"),
                      yaxis2=dict(title="Volume", overlaying="y", side="right"),
                      plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'))
    st.plotly_chart(fig, use_container_width=True)

    # P&L Chart
    pnl = []
    realized = 0
    for t in st.session_state.trade_log:
        if t['side'] == 'SELL':
            realized += (t['price'] - 30000) * t['qty']
        pnl.append(realized)
    if pnl:
        pnl_fig = go.Figure()
        pnl_fig.add_trace(go.Scatter(y=pnl, mode='lines+markers', name="P&L", line=dict(color='yellow')))
        pnl_fig.update_layout(title="Realized P&L Over Time", plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'))
        st.plotly_chart(pnl_fig, use_container_width=True)

    # Trade Log
    st.subheader("📜 Trade Log")
    if st.session_state.trade_log:
        st.dataframe(pd.DataFrame(st.session_state.trade_log))
    else:
        st.write("No trades yet.")

# -------- RIGHT PANEL: Trading Controls --------
with right:
    st.markdown(f"<div class='{neon_class}'>🛠 Trading Panel</div>", unsafe_allow_html=True)
    mode = st.radio("Mode", ["Simulation", "Live"])
    side = st.radio("Side", ["BUY", "SELL"])
    qty = st.number_input("Quantity", min_value=1, value=1)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    price_input = None
    if order_type == "LIMIT":
        price_input = st.number_input("Limit Price", min_value=1.0, value=price)
    if st.button("Submit Order"):
        trade_price = price_input if order_type == "LIMIT" else price
        st.session_state.trade_log.append({"time": datetime.now(), "side": side, "qty": qty, "price": trade_price})

# ---------------------- Auto Refresh ----------------------
time.sleep(5)
st.rerun()
