import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import time
from streamlit_autorefresh import st_autorefresh

# ---------- Page Config ----------
st.set_page_config(page_title="HFT Dashboard", layout="wide")

# ---------- Auto-refresh ----------
st_autorefresh(interval=5000, key="refresh")  # refresh every 5 sec

# ---------- Custom CSS ----------
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: white;
        }
        .neon {
            font-size: 22px;
            font-weight: bold;
            color: white;
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            border: 2px solid white;
            background-color: #111;
            box-shadow: 0 0 10px #39ff14, 0 0 20px #39ff14;
            animation: flicker 1.5s infinite alternate;
        }
        @keyframes flicker {
            0% { text-shadow: 0 0 5px #39ff14, 0 0 10px #39ff14; }
            100% { text-shadow: 0 0 20px #39ff14, 0 0 40px #39ff14; }
        }
        .panel {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 15px;
            border: 2px solid white;
            height: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []

# ---------- Mock Price Feed ----------
def get_live_price():
    base_price = 30000
    return base_price + random.uniform(-200, 200)

# ---------- AI Signal ----------
def ai_market_signal():
    if len(st.session_state.price_data) < 10:
        return "HOLD", "Collecting more data for better prediction."
    prices = [p[1] for p in st.session_state.price_data[-10:]]
    trend = (prices[-1] - prices[0]) / prices[0]
    if trend > 0.002:
        return "BUY", "Strong bullish momentum detected."
    elif trend < -0.002:
        return "SELL", "Bearish trend detected."
    else:
        return "HOLD", "Market neutral. Wait for clarity."

# ---------- Layout ----------
left, middle, right = st.columns([1.5, 3, 1.5])

# ---------- AI Panel ----------
with left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>🤖 AI Market Intelligence</div>", unsafe_allow_html=True)

    ai_signal, ai_text = ai_market_signal()
    color = "#39ff14" if ai_signal == "BUY" else "#ff073a" if ai_signal == "SELL" else "#ffff00"

    st.markdown(f"""
        <div style='text-align:center;font-size:24px;font-weight:bold;color:white;
        background-color:{color};border-radius:10px;padding:12px;margin-bottom:15px;
        box-shadow:0 0 20px {color},0 0 40px {color};'>{ai_signal}</div>
    """, unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:18px;line-height:1.6;'>{ai_text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Main Panel ----------
with middle:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>⚡ High Frequency Trading Dashboard</div>", unsafe_allow_html=True)

    # Update Price Data
    price = get_live_price()
    st.session_state.price_data.append((time.strftime('%H:%M:%S'), price, random.randint(10, 100)))
    df = pd.DataFrame(st.session_state.price_data, columns=['time', 'price', 'volume'])

    # Price & Volume Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['price'], mode='lines+markers', name='Price', line=dict(color='lime')))
    fig.add_trace(go.Bar(x=df['time'], y=df['volume'], name='Volume', yaxis='y2', marker=dict(color='blue')))
    fig.update_layout(template="plotly_dark", xaxis=dict(title="Time"),
                      yaxis=dict(title="Price"), yaxis2=dict(title="Volume", overlaying="y", side="right"), height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Trade Log
    st.subheader("📜 Trade Log")
    if st.session_state.trade_log:
        st.dataframe(pd.DataFrame(st.session_state.trade_log))
    else:
        st.info("No trades yet.")

    # PnL Calculation (basic)
    pnl = []
    cum_pnl = 0
    for trade in st.session_state.trade_log:
        if trade["side"] == "BUY":
            cum_pnl -= trade["qty"] * trade["price"]
        else:
            cum_pnl += trade["qty"] * trade["price"]
        pnl.append(cum_pnl)
    pnl_fig = go.Figure()
    pnl_fig.add_trace(go.Scatter(x=[t["time"] for t in st.session_state.trade_log], y=pnl, mode='lines', name='PnL', line=dict(color='cyan')))
    pnl_fig.update_layout(template="plotly_dark", title="📊 Realized PnL", height=300)
    st.plotly_chart(pnl_fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Trading Panel ----------
with right:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>🛠 Trading Panel</div>", unsafe_allow_html=True)

    mode = st.radio("Mode", ["Simulation", "Live"])
    side = st.radio("Side", ["BUY", "SELL"])
    qty = st.number_input("Quantity", min_value=1.0, step=1.0, value=1.0)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    limit_price = st.number_input("Limit Price", value=30000.0, step=0.01)

    if st.button("Submit Order"):
        trade_price = price if order_type == "MARKET" else limit_price
        st.session_state.trade_log.append({"time": time.strftime('%H:%M:%S'), "side": side, "qty": qty, "price": trade_price})
        st.success(f"Order placed: {side} {qty} @ {trade_price}")

    st.markdown("</div>", unsafe_allow_html=True)
