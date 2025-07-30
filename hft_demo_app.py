import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# ✅ Page Config
st.set_page_config(page_title="HFT Prototype Demo", layout="wide")
st.title("⚡ High-Frequency Trading Prototype (Binance Testnet)")

# ✅ Sidebar Settings
st.sidebar.header("⚙️ Settings")
refresh_rate = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 3)

# ✅ Auto-refresh setup
st_autorefresh(interval=refresh_rate * 1000, key="refresh")

# ✅ Initialize session state
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []

# ✅ Fetch price from Binance Testnet REST API
def fetch_price():
    url = "https://testnet.binance.vision/api/v3/ticker/price?symbol=BTCUSDT"
    try:
        response = requests.get(url)
        data = response.json()
        return float(data["price"])
    except Exception as e:
        st.error(f"Error fetching price: {e}")
        return None

# ✅ Simple Market-Making Simulation
def market_maker_strategy(current_price):
    qty = 0.001
    bid_price = current_price * 0.999
    ask_price = current_price * 1.001
    buy_executed = np.random.choice([True, False], p=[0.3, 0.7])
    sell_executed = np.random.choice([True, False], p=[0.3, 0.7])

    trades = []
    if buy_executed:
        trades.append({"type": "BUY", "price": round(bid_price, 2), "qty": qty})
    if sell_executed:
        trades.append({"type": "SELL", "price": round(ask_price, 2), "qty": qty})
    return trades

# ✅ Update Data
price = fetch_price()
if price:
    st.session_state.price_data.append({"time": pd.Timestamp.now(), "price": price})
    trades = market_maker_strategy(price)
    for t in trades:
        st.session_state.trade_log.append({"time": pd.Timestamp.now(), **t})

# ✅ Price Chart
st.subheader("📈 Live Price Feed (BTC/USDT)")
if len(st.session_state.price_data) > 5:
    df_price = pd.DataFrame(st.session_state.price_data[-100:])
    fig = px.line(df_price, x="time", y="price", title="Live BTC/USDT Price")
    st.plotly_chart(fig, use_container_width=True)

# ✅ Trade Log & P&L
st.subheader("📜 Trade Log & Simulated P&L")
if len(st.session_state.trade_log) > 0:
    df_trades = pd.DataFrame(st.session_state.trade_log[-20:])
    buy_sum = df_trades[df_trades["type"] == "BUY"]["price"].sum()
    sell_sum = df_trades[df_trades["type"] == "SELL"]["price"].sum()
    pnl = (sell_sum - buy_sum) * 0.001
    st.metric("💰 Simulated P&L", f"{pnl:.2f} USDT")
    st.dataframe(df_trades)
