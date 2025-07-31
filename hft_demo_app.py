import streamlit as st
import pandas as pd
import numpy as np
import json
import threading
import websocket
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import requests
import time

# ✅ Page Config
st.set_page_config(page_title="Advanced HFT Prototype", layout="wide")
st.title("⚡ Advanced High-Frequency Trading Prototype (Binance Testnet)")

# ✅ Sidebar Settings
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 5, 2)

# ✅ Auto-refresh UI
st_autorefresh(interval=refresh_interval * 1000, key="refresh")

# ✅ Initialize Session State
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "pnl" not in st.session_state:
    st.session_state.pnl = 0.0
if "pending_order" not in st.session_state:
    st.session_state.pending_order = None
if "last_data_time" not in st.session_state:
    st.session_state.last_data_time = time.time()

# ✅ Binance API URLs
TRADE_WS = "wss://testnet.binance.vision/ws/btcusdt@trade"
ORDER_BOOK_API = "https://testnet.binance.vision/api/v3/depth?symbol=BTCUSDT&limit=5"

# ✅ WebSocket Callbacks for Price
def on_trade(ws, message):
    data = json.loads(message)
    price = float(data['p'])
    st.session_state.price_data.append({"time": pd.Timestamp.now(), "price": price})
    st.session_state.last_data_time = time.time()

def start_ws():
    try:
        ws_trade = websocket.WebSocketApp(TRADE_WS, on_message=on_trade)
        threading.Thread(target=ws_trade.run_forever, daemon=True).start()
    except Exception as e:
        print(f"WebSocket error: {e}")

# ✅ Reconnect WebSocket if dead
if time.time() - st.session_state.last_data_time > 5:
    st.sidebar.warning("Reconnecting WebSocket...")
    start_ws()

# ✅ Ensure WebSocket started
if "ws_started" not in st.session_state:
    start_ws()
    st.session_state.ws_started = True

# ✅ Get Real Order Book from Binance REST API
def fetch_order_book():
    try:
        response = requests.get(ORDER_BOOK_API, timeout=3)
        if response.status_code == 200:
            data = response.json()
            bids = [(float(price), float(qty)) for price, qty in data["bids"]]
            asks = [(float(price), float(qty)) for price, qty in data["asks"]]
            return bids, asks
    except:
        return [], []

bids, asks = fetch_order_book()

# ✅ Market-Making Simulation
def market_maker():
    if len(st.session_state.price_data) < 1:
        # Inject dummy price if WebSocket is slow
        st.session_state.price_data.append({"time": pd.Timestamp.now(), "price": 100000.0})
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

# ✅ Dummy Order UI
st.sidebar.subheader("🛒 Place Dummy Order")
order_type = st.sidebar.selectbox("Order Type", ["BUY", "SELL"])
preferred_price = st.sidebar.number_input("Preferred Price (USDT)", min_value=10000.0, value=100000.0)
order_qty = st.sidebar.number_input("Order Quantity (BTC)", min_value=0.0001, value=0.001)

if st.sidebar.button("Submit Order"):
    st.session_state.pending_order = {
        "type": order_type,
        "price": preferred_price,
        "qty": order_qty,
        "status": "OPEN",
        "time": pd.Timestamp.now()
    }
    st.sidebar.success(f"Order placed: {order_type} {order_qty} BTC at {preferred_price} USDT")

# ✅ Check Dummy Order Execution
if st.session_state.pending_order and st.session_state.pending_order["status"] == "OPEN":
    latest_price = st.session_state.price_data[-1]["price"] if st.session_state.price_data else None
    if latest_price:
        if (st.session_state.pending_order["type"] == "BUY" and latest_price <= st.session_state.pending_order["price"]) or \
           (st.session_state.pending_order["type"] == "SELL" and latest_price >= st.session_state.pending_order["price"]):
            executed_order = st.session_state.pending_order
            executed_order["status"] = "FILLED"
            executed_order["execution_price"] = latest_price
            st.session_state.trade_log.append(executed_order)

            # Update P&L
            if executed_order["type"] == "BUY":
                st.session_state.pnl -= latest_price * executed_order["qty"]
            else:
                st.session_state.pnl += latest_price * executed_order["qty"]

            st.sidebar.success(f"✅ Order executed at {latest_price} USDT")
            st.session_state.pending_order = None

# ✅ Debug Info
st.write(f"DEBUG: Price ticks received = {len(st.session_state.price_data)}")

# ✅ Layout: Price Chart and Order Book
col1, col2 = st.columns(2)

# ✅ Price Chart
with col1:
    st.subheader("📈 Live BTC/USDT Price")
    if len(st.session_state.price_data) > 0:
        df_price = pd.DataFrame(st.session_state.price_data[-100:])
        fig = go.Figure(go.Scatter(x=df_price["time"], y=df_price["price"], mode="lines+markers", line=dict(color="blue")))
        fig.update_layout(title="BTC/USDT Price", xaxis_title="Time", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⏳ Waiting for price data from Binance Testnet...")

# ✅ Order Book Visualization (Real via REST)
with col2:
    st.subheader("📊 Order Book Depth")
    if bids and asks:
        bid_prices, bid_qty = zip(*bids)
        ask_prices, ask_qty = zip(*asks)
        fig_ob = go.Figure()
        fig_ob.add_trace(go.Bar(x=bid_prices, y=bid_qty, name="Bids", marker_color="green"))
        fig_ob.add_trace(go.Bar(x=ask_prices, y=ask_qty, name="Asks", marker_color="red"))
        fig_ob.update_layout(barmode="overlay", title="Order Book Depth", xaxis_title="Price", yaxis_title="Qty")
        st.plotly_chart(fig_ob, use_container_width=True)
    else:
        st.info("⏳ Fetching order book data...")

# ✅ Trade Log and P&L
st.subheader("📜 Trade Log & P&L")
if len(st.session_state.trade_log) > 0:
    df_trades = pd.DataFrame(st.session_state.trade_log[-20:])
    st.metric("💰 Simulated P&L", f"{st.session_state.pnl:.2f} USDT")
    st.dataframe(df_trades)
