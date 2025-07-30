import streamlit as st
import pandas as pd
import numpy as np
import json
import threading
import websocket
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import time

# ✅ Page Config
st.set_page_config(page_title="Advanced HFT Prototype", layout="wide")
st.title("⚡ Advanced High-Frequency Trading Prototype (Binance Testnet)")

# ✅ Sidebar Controls
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 5, 2)
mode = st.sidebar.radio("Mode", ["Simulation", "Live Testnet (Fake Money)"])
st.sidebar.info("Live Testnet mode requires API keys in Streamlit secrets.")

# ✅ Auto-refresh UI
st_autorefresh(interval=refresh_interval * 1000, key="refresh")

# ✅ Initialize Session State
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "order_book" not in st.session_state:
    st.session_state.order_book = {"bids": [], "asks": []}
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "pnl" not in st.session_state:
    st.session_state.pnl = 0.0

# ✅ Binance Testnet WebSocket URLs
TRADE_WS = "wss://testnet.binance.vision/ws/btcusdt@trade"
DEPTH_WS = "wss://testnet.binance.vision/ws/btcusdt@depth5@100ms"

# ✅ WebSocket Functions
def on_trade(ws, message):
    data = json.loads(message)
    price = float(data['p'])
    st.session_state.price_data.append({"time": pd.Timestamp.now(), "price": price})

def on_depth(ws, message):
    data = json.loads(message)
    bids = [(float(b[0]), float(b[1])) for b in data["bids"]]
    asks = [(float(a[0]), float(a[1])) for a in data["asks"]]
    st.session_state.order_book = {"bids": bids, "asks": asks}

def start_ws():
    # Trade Stream
    ws_trade = websocket.WebSocketApp(TRADE_WS, on_message=on_trade)
    threading.Thread(target=ws_trade.run_forever, daemon=True).start()

    # Depth Stream
    ws_depth = websocket.WebSocketApp(DEPTH_WS, on_message=on_depth)
    threading.Thread(target=ws_depth.run_forever, daemon=True).start()

# ✅ Start WebSocket once
if "ws_started" not in st.session_state:
    start_ws()
    st.session_state.ws_started = True

# ✅ Market-Making Simulation Logic
def market_maker():
    if len(st.session_state.price_data) < 1:
        return
    latest_price = st.session_state.price_data[-1]["price"]
    qty = 0.001
    bid_price = latest_price * 0.999
    ask_price = latest_price * 1.001

    buy_executed = np.random.choice([True, False], p=[0.3, 0.7])
    sell_executed = np.random.choice([True, False], p=[0.3, 0.7])

    trades = []
    if buy_executed:
        trades.append({"type": "BUY", "price": round(bid_price, 2), "qty": qty})
        st.session_state.pnl -= bid_price * qty
    if sell_executed:
        trades.append({"type": "SELL", "price": round(ask_price, 2), "qty": qty})
        st.session_state.pnl += ask_price * qty

    for t in trades:
        t["time"] = pd.Timestamp.now()
        st.session_state.trade_log.append(t)

market_maker()

# ✅ UI Layout
col1, col2 = st.columns(2)

# ✅ Price Chart
with col1:
    st.subheader("📈 Live BTC/USDT Price")
    if len(st.session_state.price_data) > 5:
        df_price = pd.DataFrame(st.session_state.price_data[-100:])
        fig = go.Figure(go.Scatter(x=df_price["time"], y=df_price["price"], mode="lines", name="Price"))
        fig.update_layout(title="BTC/USDT Price", xaxis_title="Time", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)

# ✅ Order Book Visualization
with col2:
    st.subheader("📊 Order Book Depth")
    ob = st.session_state.order_book
    if ob["bids"] and ob["asks"]:
        bid_prices, bid_qty = zip(*ob["bids"])
        ask_prices, ask_qty = zip(*ob["asks"])
        fig_ob = go.Figure()
        fig_ob.add_trace(go.Bar(x=bid_prices, y=bid_qty, name="Bids", marker_color="green"))
        fig_ob.add_trace(go.Bar(x=ask_prices, y=ask_qty, name="Asks", marker_color="red"))
        fig_ob.update_layout(barmode="overlay", title="Order Book Depth", xaxis_title="Price", yaxis_title="Qty")
        st.plotly_chart(fig_ob, use_container_width=True)

# ✅ Trade Log and P&L
st.subheader("📜 Trade Log & P&L")
if len(st.session_state.trade_log) > 0:
    df_trades = pd.DataFrame(st.session_state.trade_log[-20:])
    st.metric("💰 Simulated P&L", f"{st.session_state.pnl:.2f} USDT")
    st.dataframe(df_trades)
