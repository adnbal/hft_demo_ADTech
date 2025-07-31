import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="auto-refresh")

st.set_page_config(layout="wide")

# ------------------- CSS for Styling -------------------
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: white;
        }
        .panel {
            background-color: #1e1e1e;
            border: 2px solid white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .neon {
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 0 15px #39ff14;
            color: white;
        }
        .neon-red {
            box-shadow: 0 0 15px #ff073a;
        }
        .button-signal {
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            padding: 8px;
            margin-top: 10px;
            border-radius: 8px;
            box-shadow: 0 0 15px #39ff14;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------- Session State -------------------
if "price_data" not in st.session_state or not isinstance(st.session_state.price_data, list):
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []
if "ai_signal" not in st.session_state:
    st.session_state.ai_signal = "HOLD"
if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = []

# ------------------- Simulated Price Generator -------------------
def generate_price_data():
    last_price = st.session_state.price_data[-1][1] if st.session_state.price_data else 30000
    new_price = round(last_price + np.random.uniform(-50, 50), 2)
    new_volume = np.random.randint(10, 100)
    st.session_state.price_data.append((datetime.now().strftime("%H:%M:%S"), new_price, new_volume))
    if len(st.session_state.price_data) > 100:
        st.session_state.price_data.pop(0)

# ------------------- AI Market Signal -------------------
def ai_market_signal():
    if len(st.session_state.price_data) < 10:
        return "HOLD", "Collecting more data for better prediction."
    prices = [p[1] for p in st.session_state.price_data[-10:]]
    trend = np.polyfit(range(len(prices)), prices, 1)[0]
    if trend > 0.8:
        return "BUY", "Upward trend → bullish momentum.\nExpected +0.8% in next few mins."
    elif trend < -0.8:
        return "SELL", "Downward trend → bearish momentum.\nPossible -0.7% drop soon."
    else:
        return "HOLD", "Sideways movement.\nLimited opportunity now."

# ------------------- Layout -------------------
col1, col2, col3 = st.columns([1.5, 3, 1.5])

# AI PANEL
with col1:
    signal, ai_text = ai_market_signal()
    st.session_state.ai_signal = signal
    neon_class = "neon" if signal == "BUY" else "neon neon-red" if signal == "SELL" else "neon"
    st.markdown(f'<div class="panel"><div class="{neon_class}">🤖 AI Market Intelligence</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="button-signal">{signal}</div>', unsafe_allow_html=True)
    st.write(ai_text)
    st.markdown('</div>', unsafe_allow_html=True)

# MAIN DASHBOARD
with col2:
    st.markdown(f'<div class="panel"><div class="{neon_class}">⚡ High Frequency Trading Dashboard</div>', unsafe_allow_html=True)
    generate_price_data()
    df = pd.DataFrame(st.session_state.price_data, columns=["time", "price", "volume"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["price"], mode='lines+markers', name="Price", line=dict(color="lime", width=2)))
    fig.add_trace(go.Bar(x=df["time"], y=df["volume"], name="Volume", marker=dict(color="blue"), yaxis="y2"))
    fig.update_layout(
        template="plotly_dark",
        yaxis=dict(title="Price (USD)"),
        yaxis2=dict(title="Volume", overlaying="y", side="right"),
        margin=dict(l=10, r=10, t=30, b=10),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------- Realized & Unrealized P&L -------------------
    st.markdown(f'<div class="panel"><div class="{neon_class}">📊 Realized & Unrealized P&L</div>', unsafe_allow_html=True)
    realized_pnl = sum([t.get("PnL", 0) for t in st.session_state.trade_log])
    unrealized_pnl = np.random.uniform(-500, 500)  # Simulated
    st.metric("Realized P&L (USD)", f"${realized_pnl:,.2f}")
    st.metric("Unrealized P&L (USD)", f"${unrealized_pnl:,.2f}")

    st.session_state.pnl_history.append((datetime.now().strftime("%H:%M:%S"), realized_pnl, unrealized_pnl))
    pnl_df = pd.DataFrame(st.session_state.pnl_history, columns=["time", "realized", "unrealized"])
    fig_pnl = go.Figure()
    fig_pnl.add_trace(go.Scatter(x=pnl_df["time"], y=pnl_df["realized"], mode="lines", name="Realized P&L", line=dict(color="yellow")))
    fig_pnl.add_trace(go.Scatter(x=pnl_df["time"], y=pnl_df["unrealized"], mode="lines", name="Unrealized P&L", line=dict(color="green")))
    fig_pnl.update_layout(template="plotly_dark", height=300)
    st.plotly_chart(fig_pnl, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# TRADING PANEL
with col3:
    st.markdown(f'<div class="panel"><div class="{neon_class}">🛠 Trading Panel</div>', unsafe_allow_html=True)
    mode = st.radio("Mode", ["Simulation", "Live"])
    side = st.radio("Side", ["BUY", "SELL"])
    qty = st.number_input("Quantity", min_value=1, value=1, step=1)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    price = st.number_input("Limit Price", min_value=1.0, value=30000.0, step=100.0)

    if st.button("Submit Order"):
        st.session_state.trade_log.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "side": side, "qty": qty, "price": price})
        st.success(f"Order Submitted: {side} {qty} @ {price}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Trade Log
    st.markdown('<div class="panel"><b>📜 Trade Log</b></div>', unsafe_allow_html=True)
    if st.session_state.trade_log:
        st.dataframe(pd.DataFrame(st.session_state.trade_log).tail(10))
    else:
        st.write("No trades yet.")

    # Portfolio Metrics
    st.markdown('<div class="panel"><b>📊 Portfolio Metrics</b></div>', unsafe_allow_html=True)
    st.table(pd.DataFrame({"Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
                           "Value": [qty, f"${qty * price:,.2f}", f"${price:,.2f}"]}))
