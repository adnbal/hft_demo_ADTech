import os
os.environ["STREAMLIT_WATCH_FILE_SYSTEM"] = "false"

import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

# ----------------------------
# ✅ PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="HFT Demo", page_icon="📈", layout="wide")

# ----------------------------
# ✅ SESSION STATE INIT
# ----------------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []

if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

if "positions" not in st.session_state:
    st.session_state.positions = {"long": 0, "short": 0}

# ----------------------------
# ✅ PRICE SIMULATION FUNCTION
# ----------------------------
def simulate_price():
    """Simulate BTC/USDT price movement"""
    base_price = 68000
    if st.session_state.price_data:
        base_price = st.session_state.price_data[-1]["price"]
    # Random price movement
    price = base_price + random.uniform(-50, 50)
    return round(price, 2)

# ----------------------------
# ✅ UPDATE POSITIONS FUNCTION
# ----------------------------
def update_positions(side, qty, price):
    if side == "BUY":
        st.session_state.positions["long"] += qty
    else:
        st.session_state.positions["short"] += qty

# ----------------------------
# ✅ HEADER
# ----------------------------
st.title("⚡ High-Frequency Trading (HFT) Demo")
st.caption("Real-time BTC/USDT Price Simulation with Mock Orders")

# ----------------------------
# ✅ LIVE PRICE FEED
# ----------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Live BTC/USDT Price")
    price_placeholder = st.empty()

    # Update price every second for live effect
    price = simulate_price()
    st.session_state.price_data.append({"time": datetime.now(), "price": price})
    price_placeholder.metric("BTC/USDT", f"${price}")

with col2:
    st.subheader("📊 Current Positions")
    st.write(st.session_state.positions)

# ----------------------------
# ✅ ORDER ENTRY
# ----------------------------
st.sidebar.header("Place Order")
mode = st.sidebar.radio("Mode", ["Simulation", "Live"], index=0)
side = st.sidebar.selectbox("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity (BTC)", min_value=0.001, step=0.001)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
price_input = st.sidebar.number_input("Limit Price", min_value=1.0, value=price, step=1.0)

if st.sidebar.button("Submit Order"):
    trade_price = price_input if order_type == "LIMIT" else price

    if mode == "Simulation":
        update_positions(side, qty, trade_price)
        st.session_state.trade_log.append({
            "time": datetime.now(),
            "side": side,
            "qty": qty,
            "price": trade_price
        })
        st.sidebar.success(f"✅ {side} {qty} BTC at ${trade_price}")
    else:
        st.sidebar.warning("Live trading not implemented in this demo.")

# ----------------------------
# ✅ PRICE CHART
# ----------------------------
if len(st.session_state.price_data) > 0:
    df_price = pd.DataFrame(st.session_state.price_data[-100:])
    st.line_chart(df_price.set_index("time")["price"])

# ----------------------------
# ✅ TRADE LOG
# ----------------------------
st.subheader("📜 Trade Log")
if len(st.session_state.trade_log) > 0:
    df_trades = pd.DataFrame(st.session_state.trade_log)
    st.dataframe(df_trades)
else:
    st.info("No trades yet. Place an order from the sidebar!")
