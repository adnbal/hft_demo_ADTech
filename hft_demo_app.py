import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI HFT Dashboard", layout="wide")

# ---------------- SESSION STATE ----------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "pnl_history" not in st.session_state:
    st.session_state.pnl_history = []

# ---------------- AUTO REFRESH ----------------
st_autorefresh(interval=5000, key="auto-refresh")

# ---------------- PRICE SIMULATION ----------------
price = 30000 + np.random.randn() * 50
volume = random.randint(10, 100)
st.session_state.price_data.append({"time": datetime.now(), "price": price, "volume": volume})

# ---------------- AI SIGNAL ----------------
recent_prices = [p["price"] for p in st.session_state.price_data[-10:]]
signal = "HOLD"
reason = "Collecting more data for better prediction."
forecast = ""
color = "#FFD700"  # Yellow for HOLD

if len(recent_prices) >= 10:
    trend = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
    if trend > 0:
        signal = "BUY"
        reason = "Upward trend → bullish momentum."
        forecast = "Expected +0.8% in next few mins."
        color = "#39ff14"  # Neon green
    elif trend < 0:
        signal = "SELL"
        reason = "Downward trend → bearish pressure."
        forecast = "Expected -0.7% in next few mins."
        color = "#FF073A"  # Neon red

# ---------------- CUSTOM CSS ----------------
st.markdown(f"""
    <style>
    body {{
        background-color: #0f172a;
        color: white;
        margin: 0;
    }}
    .main > div {{
        padding-top: 0rem;
    }}
    /* Neon Titles */
    .neon-title {{
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        color: white;
        border: 2px solid {color};
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 15px;
        box-shadow: 0 0 15px {color}, 0 0 30px {color};
    }}
    /* AI Signal Box */
    .neon-box {{
        border: 2px solid {color};
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: white;
        box-shadow: 0 0 15px {color}, 0 0 30px {color};
        margin-bottom: 15px;
    }}
    /* Panels */
    .side-panel {{
        background-color: #1f2937; /* Grey */
        border-radius: 12px;
        border: 2px solid white;
        padding: 20px;
        height: 100%;
    }}
    .middle-panel {{
        background-color: #0f172a; /* Black */
        border-radius: 12px;
        border: 2px solid white;
        padding: 20px;
        height: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

# ---------------- LAYOUT ----------------
col_ai, col_main, col_trade = st.columns([0.35, 1.3, 0.6])

# ---- LEFT AI PANEL ----
with col_ai:
    st.markdown("<div class='side-panel'>", unsafe_allow_html=True)
    st.markdown(f"<div class='neon-title'>🤖 AI Market Intelligence</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='neon-box'>{signal}</div>", unsafe_allow_html=True)
    st.write(reason)
    st.write(forecast)
    st.markdown("</div>", unsafe_allow_html=True)

# ---- MIDDLE MAIN PANEL ----
with col_main:
    st.markdown("<div class='middle-panel'>", unsafe_allow_html=True)
    st.markdown(f"<div class='neon-title'>⚡ High Frequency Trading Dashboard</div>", unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.price_data[-50:])
    if not df.empty:
        # Price & Volume Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["time"], y=df["price"], mode="lines+markers",
                                 name="Price", line=dict(color=color, width=3)))
        fig.add_trace(go.Bar(x=df["time"], y=df["volume"], name="Volume",
                             marker_color="blue", opacity=0.4, yaxis="y2"))
        fig.update_layout(template="plotly_dark",
                          yaxis=dict(title="Price (USD)"),
                          yaxis2=dict(title="Volume", overlaying="y", side="right"),
                          height=400)
        st.plotly_chart(fig, use_container_width=True)

    # ---- Realized & Unrealized P&L ----
    st.subheader("📊 Realized & Unrealized P&L")
    pnl = random.randint(-1500, 1500)
    st.metric("Unrealized P&L (USD)", f"${pnl}", delta=pnl)

    # Store history for P&L line chart
    st.session_state.pnl_history.append({"time": datetime.now(), "pnl": pnl})
    pnl_df = pd.DataFrame(st.session_state.pnl_history[-50:])
    if not pnl_df.empty:
        fig_pnl = go.Figure()
        fig_pnl.add_trace(go.Scatter(x=pnl_df["time"], y=pnl_df["pnl"], mode="lines",
                                     line=dict(color=color, width=3)))
        fig_pnl.update_layout(template="plotly_dark", title="P&L Over Time")
        st.plotly_chart(fig_pnl, use_container_width=True)

    # ---- Trade Log ----
    st.subheader("📜 Trade Log")
    if st.session_state.trade_log:
        st.dataframe(pd.DataFrame(st.session_state.trade_log))
    else:
        st.write("No trades yet.")

    # ---- Portfolio Metrics ----
    st.subheader("📊 Portfolio Metrics")
    metrics = pd.DataFrame({
        "Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
        "Value": [5, "$151,035.36", "$30,000.00"]
    })
    st.dataframe(metrics)

    st.markdown("</div>", unsafe_allow_html=True)

# ---- RIGHT TRADING PANEL ----
with col_trade:
    st.markdown("<div class='side-panel'>", unsafe_allow_html=True)
    st.markdown(f"<div class='neon-title'>🛠 Trading Panel</div>", unsafe_allow_html=True)

    # Trading Inputs
    st.radio("Mode", ["Simulation", "Live"])
    st.radio("Side", ["BUY", "SELL"])
    qty = st.number_input("Quantity", min_value=1, value=1)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    if order_type == "LIMIT":
        st.number_input("Limit Price", min_value=1.0, value=30000.0, step=0.01)
    st.button("Submit Order")

    st.markdown("</div>", unsafe_allow_html=True)
