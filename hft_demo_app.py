import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
from datetime import datetime
import random
import requests

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="HFT Trading AI Dashboard", layout="wide")

# ------------------ SESSION STATE ------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "positions" not in st.session_state:
    st.session_state.positions = {"BTC": {"qty": 0, "avg_price": 0}}
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "pnl" not in st.session_state:
    st.session_state.pnl = []

# ------------------ HELPER FUNCTIONS ------------------
def update_positions(side, qty, price):
    pos = st.session_state.positions["BTC"]
    if side == "BUY":
        total_qty = pos["qty"] + qty
        avg_price = (pos["avg_price"] * pos["qty"] + price * qty) / total_qty if total_qty != 0 else 0
        pos["qty"], pos["avg_price"] = total_qty, avg_price
    else:  # SELL
        pos["qty"] -= qty
        if pos["qty"] < 0:
            pos["qty"] = 0
        # Realized PnL
        pnl_value = (price - pos["avg_price"]) * qty
        st.session_state.pnl.append({"time": datetime.now(), "pnl": pnl_value})

def generate_fake_price():
    return round(30000 + random.uniform(-200, 200), 2)

def calculate_metrics():
    trades = st.session_state.trade_log
    if len(trades) == 0:
        return {"Total Trades": 0, "PnL": 0, "ROI": "0%"}
    total_pnl = sum([(t["price"] - st.session_state.positions["BTC"]["avg_price"]) * t["qty"]
                     for t in trades if t["side"] == "SELL"])
    invested = sum([t["price"] * t["qty"] for t in trades if t["side"] == "BUY"])
    roi = (total_pnl / invested * 100) if invested > 0 else 0
    return {"Total Trades": len(trades), "PnL": round(total_pnl, 2), "ROI": f"{roi:.2f}%"}

def get_ai_recommendation():
    try:
        ai_key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        if not ai_key:
            return "⚠️ AI key not found in secrets."
        prompt = f"BTC is at {st.session_state.price_data[-1]['price'] if st.session_state.price_data else 30000}. Should we Buy, Sell, or Hold?"
        # Dummy response for now
        return f"AI Suggestion: Hold. Market is sideways."
    except Exception as e:
        return f"Error getting AI recommendation: {str(e)}"

# ------------------ HEADER ------------------
st.title("⚡ High Frequency Trading AI Dashboard")
st.caption("Simulated BTC/USDT Trading with AI Insights")

# ------------------ SIDEBAR CONTROLS ------------------
st.sidebar.header("Trading Panel")
mode = st.sidebar.radio("Mode", ["Simulation", "Live"])
side = st.sidebar.selectbox("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity", min_value=0.001, max_value=5.0, value=0.01, step=0.001)
order_type = st.sidebar.radio("Order Type", ["MARKET", "LIMIT"])
price_input = st.sidebar.number_input("Limit Price", value=30000.0, step=50.0)
submit_order = st.sidebar.button("Submit Order")

# ------------------ PRICE STREAM ------------------
price = generate_fake_price()
st.session_state.price_data.append({"time": datetime.now(), "price": price})

# ------------------ PROCESS ORDER ------------------
if submit_order:
    trade_price = price_input if order_type == "LIMIT" else price
    update_positions(side, qty, trade_price)
    st.session_state.trade_log.append({
        "time": datetime.now(),
        "side": side,
        "qty": qty,
        "price": trade_price
    })
    st.success(f"Order Executed: {side} {qty} BTC at {trade_price}")

# ------------------ MAIN LAYOUT ------------------
col1, col2 = st.columns(2)

# ✅ PRICE CHART
with col1:
    st.subheader("📈 Live BTC Price")
    df_price = pd.DataFrame(st.session_state.price_data[-100:])
    if not df_price.empty:
        fig_price = px.line(df_price, x="time", y="price", title="BTC/USDT Price Trend")
        st.plotly_chart(fig_price, use_container_width=True)

# ✅ TRADE LOG
with col2:
    st.subheader("📜 Trade Log")
    df_trades = pd.DataFrame(st.session_state.trade_log)
    st.dataframe(df_trades.tail(10) if not df_trades.empty else "No trades yet.")

# ✅ PORTFOLIO METRICS
st.subheader("📊 Portfolio & Risk Metrics")
metrics = calculate_metrics()
st.metric("Total Trades", metrics["Total Trades"])
st.metric("PnL (USDT)", metrics["PnL"])
st.metric("ROI", metrics["ROI"])

# ✅ AI RECOMMENDATION
st.subheader("🤖 AI Market Insight")
st.write(get_ai_recommendation())

# ✅ PNL Trend
if len(st.session_state.pnl) > 0:
    st.subheader("💰 Realized PnL Over Time")
    df_pnl = pd.DataFrame(st.session_state.pnl)
    fig_pnl = px.line(df_pnl, x="time", y="pnl", title="PnL Trend")
    st.plotly_chart(fig_pnl, use_container_width=True)

# ✅ AUTO REFRESH
st_autorefresh = st.experimental_rerun
time.sleep(1)
