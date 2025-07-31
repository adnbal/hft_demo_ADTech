import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime

st.set_page_config(page_title="HFT AI Dashboard", layout="wide")

# ---------------------- PAGE TITLE ----------------------
st.title("⚡ High Frequency Trading AI Dashboard")
st.caption("Simulated BTC/USDT Trading with AI Insights")

# ---------------------- SESSION STATE ----------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []

# ---------------------- SIMULATE LIVE PRICE ----------------------
def get_live_price():
    base_price = 68000
    noise = random.uniform(-15, 15)
    return base_price + noise

# Append price to session
current_price = get_live_price()
st.session_state.price_data.append({"time": datetime.now(), "price": current_price})
if len(st.session_state.price_data) > 500:
    st.session_state.price_data = st.session_state.price_data[-500:]

# ---------------------- SIDEBAR: TRADING PANEL ----------------------
st.sidebar.header("🛠 Trading Panel")

mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.radio("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", value=0.01, step=0.01)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
price_input = st.sidebar.number_input("Limit Price", value=current_price, step=10.0)

# ---------------------- ORDER EXECUTION ----------------------
def update_positions(side, qty, price):
    pnl = 0.0
    if side == "BUY":
        st.session_state.positions.append({"qty": qty, "price": price})
    elif side == "SELL" and st.session_state.positions:
        pos = st.session_state.positions.pop(0)
        pnl = (price - pos["price"]) * pos["qty"]
    return pnl

if st.sidebar.button("Submit Order"):
    trade_price = price_input if order_type == "LIMIT" else current_price
    pnl = update_positions(side, qty, trade_price)
    st.session_state.trade_log.append({
        "time": datetime.now(),
        "side": side,
        "qty": qty,
        "price": trade_price,
        "PnL": pnl
    })
    st.success(f"Order executed: {side} {qty} BTC @ {trade_price:.2f}")

# ---------------------- MAIN LAYOUT ----------------------
col1, col2 = st.columns([2, 1])

# ✅ Live BTC Price Chart + Table
with col1:
    st.subheader("📈 Live BTC Price")
    if len(st.session_state.price_data) > 1:
        df_price = pd.DataFrame(st.session_state.price_data[-100:])
        st.line_chart(df_price.set_index("time")["price"])
        st.dataframe(df_price.tail(10), use_container_width=True)
    else:
        st.info("Waiting for price data...")

# ✅ Trade Log Table
with col2:
    st.subheader("📜 Trade Log")
    df_trades = pd.DataFrame(st.session_state.trade_log)
    if not df_trades.empty:
        st.dataframe(df_trades.tail(10), use_container_width=True)
    else:
        st.write("No trades yet.")

# ---------------------- P&L CHART ----------------------
st.markdown("---")
st.subheader("📊 Realized & Unrealized P&L")

realized_pnl = sum([t["PnL"] for t in st.session_state.trade_log])
unrealized_pnl = 0.0
for pos in st.session_state.positions:
    unrealized_pnl += (current_price - pos["price"]) * pos["qty"]

pnl_df = pd.DataFrame({
    "Metric": ["Realized P&L", "Unrealized P&L"],
    "Value": [realized_pnl, unrealized_pnl]
})
st.bar_chart(pnl_df.set_index("Metric"))

# ---------------------- PORTFOLIO METRICS ----------------------
st.markdown("### 📊 Portfolio Metrics")
open_pos = sum([p["qty"] for p in st.session_state.positions])
avg_price = np.mean([p["price"] for p in st.session_state.positions]) if st.session_state.positions else 0
current_value = open_pos * current_price

metrics = {
    "Open Position (BTC)": round(open_pos, 4),
    "Current Value (USD)": f"${current_value:,.2f}",
    "Average Entry Price": f"${avg_price:,.2f}"
}
st.table(pd.DataFrame(metrics.items(), columns=["Metric", "Value"]))

# ---------------------- AI RECOMMENDATION (Neon Glow) ----------------------
st.markdown("---")
st.subheader("🤖 AI Market Intelligence")

if len(st.session_state.price_data) >= 10:
    prices = [p["price"] for p in st.session_state.price_data[-10:]]
    trend = prices[-1] - prices[0]
    avg_move = np.mean(np.diff(prices))
    volatility = np.std(prices)
    current_price = prices[-1]

    confidence = min(95, max(50, int(abs(trend) / (volatility + 0.0001) * 12)))
    forecast_price = current_price + avg_move * 2
    price_change_pct = (forecast_price - current_price) / current_price * 100

    if trend > 0:
        direction = "BUY"
        signal_text = "📈 Market is bullish → Consider BUY"
        glow_color = "#00ff99"
        rationale = f"Upward momentum with ${trend:.2f} gain in 10 ticks."
        prediction_reasoning = "Demand surge suggests continued uptrend."
    elif trend < 0:
        direction = "SELL"
        signal_text = "📉 Market is bearish → Consider SELL"
        glow_color = "#ff1744"
        rationale = f"Downward pressure with ${abs(trend):.2f} drop."
        prediction_reasoning = "Weak support indicates potential decline."
    else:
        direction = "HOLD"
        signal_text = "➖ Neutral trend → HOLD"
        glow_color = "#00b0ff"
        rationale = "Minimal movement detected."
        prediction_reasoning = "Await breakout for direction clarity."

    neon_css = f"""
    <style>
    .neon-box {{
        background: #0d0d0d;
        padding: 20px;
        margin-top: 10px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 0 20px {glow_color}, 0 0 40px {glow_color}, 0 0 60px {glow_color};
        border: 2px solid {glow_color};
        animation: flicker 1.5s infinite alternate;
    }}
    .neon-text {{
        color: {glow_color};
        font-size: 26px;
        font-weight: bold;
        text-shadow: 0 0 5px {glow_color}, 0 0 10px {glow_color}, 0 0 20px {glow_color};
    }}
    .details {{
        color: white;
        font-size: 16px;
        margin-top: 10px;
        text-align: left;
    }}
    @keyframes flicker {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.85; }}
    }}
    </style>
    """

    neon_html = f"""
    <div class="neon-box">
        <div class="neon-text">{signal_text}</div>
        <div class="details">
            <p><b>Reason:</b> {rationale}</p>
            <p><b>Why next move {('up' if trend>0 else 'down') if trend!=0 else 'uncertain'}:</b> {prediction_reasoning}</p>
            <p><b>Forecast:</b> ${forecast_price:,.2f} ({price_change_pct:+.2f}%)</p>
            <p><b>Confidence:</b> {confidence}%</p>
        </div>
    </div>
    """

    st.markdown(neon_css + neon_html, unsafe_allow_html=True)

else:
    st.info("Waiting for more price data to generate AI insights...")

# ---------------------- AUTO REFRESH ----------------------
st.caption("Refreshing every 5 seconds...")
st.experimental_rerun()
