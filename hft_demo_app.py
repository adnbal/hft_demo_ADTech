import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time

st.set_page_config(layout="wide")

# ---------- Initialize Session State ----------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []
if "ai_signal" not in st.session_state:
    st.session_state.ai_signal = "HOLD"
if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = []

# ---------- Generate Mock Price Data ----------
def generate_price_data():
    last_price = st.session_state.price_data[-1][1] if st.session_state.price_data else 30000
    new_price = last_price + random.uniform(-50, 50)
    volume = random.randint(10, 100)
    timestamp = pd.Timestamp.now().strftime("%H:%M:%S")
    st.session_state.price_data.append((timestamp, new_price, volume))
    return new_price

# ---------- Compute AI Signal ----------
def ai_market_signal():
    if len(st.session_state.price_data) < 5:
        return "HOLD", "Collecting more data for better prediction."
    prices = [p[1] for p in st.session_state.price_data[-10:]]
    trend = np.polyfit(range(len(prices)), prices, 1)[0]
    if trend > 1:
        return "BUY", "Upward trend → bullish momentum. Expected +0.8% in next few mins."
    elif trend < -1:
        return "SELL", "Downward trend → bearish signal. Possible -0.7% in next few mins."
    else:
        return "HOLD", "Sideways movement. Limited opportunity now."

# ---------- Layout Styling ----------
st.markdown("""
    <style>
    body {background-color: #0E1117;}
    .neon-box {
        border-radius: 10px;
        padding: 12px;
        font-weight: bold;
        text-align: center;
        color: white;
        box-shadow: 0 0 20px #00ff00;
        animation: glow 1.5s infinite alternate;
    }
    @keyframes glow {
        from { box-shadow: 0 0 15px #00ff00; }
        to { box-shadow: 0 0 35px #00ff00; }
    }
    .panel {
        background-color: #1E1E1E;
        border: 2px solid white;
        border-radius: 10px;
        padding: 15px;
        height: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Panel Layout ----------
col_left, col_center, col_right = st.columns([1.5, 3, 1.5])

# ---------- LEFT PANEL: AI Market Intelligence ----------
with col_left:
    ai_signal, ai_text = ai_market_signal()
    st.session_state.ai_signal = ai_signal
    color_map = {"BUY": "#00ff00", "SELL": "#ff073a", "HOLD": "#f5d300"}

    st.markdown(f"""
        <div class="panel" style="box-shadow: 0 0 15px {color_map[ai_signal]};">
            <h3 style="color:{color_map[ai_signal]};text-align:center;">🤖 AI Market Intelligence</h3>
            <div class="neon-box" style="background:{color_map[ai_signal]};color:black;">{ai_signal}</div>
            <p style="text-align:center;color:white;margin-top:10px;">{ai_text}</p>
        </div>
    """, unsafe_allow_html=True)

# ---------- CENTER PANEL: Dashboard ----------
with col_center:
    st.markdown(f"""
        <div class="panel" style="box-shadow: 0 0 15px {color_map[ai_signal]};">
            <h3 style="color:{color_map[ai_signal]};text-align:center;">⚡ High Frequency Trading Dashboard</h3>
        </div>
    """, unsafe_allow_html=True)

    # Update price data
    current_price = generate_price_data()
    df = pd.DataFrame(st.session_state.price_data, columns=["time", "price", "volume"])

    # Main Price + Volume Chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df['time'], y=df['price'], mode='lines+markers',
                             name='Price', line=dict(color='lime', width=2)), secondary_y=False)
    fig.add_trace(go.Bar(x=df['time'], y=df['volume'], name='Volume', marker_color='blue', opacity=0.4),
                  secondary_y=True)
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20),
                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=True),
                      template="plotly_dark", legend=dict(orientation="h", y=-0.3))

    st.plotly_chart(fig, use_container_width=True)

    # P&L Chart
    realized_pnl = sum([t.get("pnl", 0) for t in st.session_state.trade_log])
    st.session_state.pnl_history.append(realized_pnl)
    pnl_fig = go.Figure()
    pnl_fig.add_trace(go.Scatter(y=st.session_state.pnl_history, mode='lines+markers',
                                 name="P&L", line=dict(color=color_map[ai_signal], width=3)))
    pnl_fig.update_layout(title="📊 Realized P&L Trend", template="plotly_dark")
    st.plotly_chart(pnl_fig, use_container_width=True)

    # Trade Log Table
    st.subheader("📜 Trade Log")
    if st.session_state.trade_log:
        st.dataframe(pd.DataFrame(st.session_state.trade_log))
    else:
        st.write("No trades yet.")

# ---------- RIGHT PANEL: Trading Panel ----------
with col_right:
    st.markdown(f"""
        <div class="panel" style="box-shadow: 0 0 15px {color_map[ai_signal]};">
            <h3 style="color:{color_map[ai_signal]};text-align:center;">🛠 Trading Panel</h3>
        </div>
    """, unsafe_allow_html=True)

    mode = st.radio("Mode", ["Simulation", "Live"])
    side = st.radio("Side", ["BUY", "SELL"])
    qty = st.number_input("Quantity", value=1, step=1)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    limit_price = None
    if order_type == "LIMIT":
        limit_price = st.number_input("Limit Price", value=current_price, step=1.0, format="%.2f")

    st.write(f"**Current Market Price:** ${current_price:,.2f}")

    if st.button("Submit Order"):
        trade = {"time": pd.Timestamp.now(), "side": side, "qty": qty, "price": current_price}
        if order_type == "LIMIT":
            trade["limit_price"] = limit_price
        st.session_state.trade_log.append(trade)
        st.success(f"Order Submitted: {side} {qty} BTC @ {current_price:.2f}")

# Auto-refresh every 5 seconds
st.experimental_set_query_params(refresh=str(time.time()))
time.sleep(5)
st.experimental_rerun()
