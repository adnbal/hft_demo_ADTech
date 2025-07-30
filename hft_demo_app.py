import streamlit as st
import pandas as pd
import numpy as np
import json
import threading
import websocket
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# ✅ Page Config
st.set_page_config(page_title="Advanced HFT Prototype", layout="wide")
st.title("⚡ Advanced High-Frequency Trading Prototype (Binance Testnet)")

# ✅ Sidebar Settings
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 5, 2)

# ✅ Auto-refresh
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
if "pending_order" not in st.session_state:
    st.session_state.pending_order = None

# ✅ WebSocket URLs for Binance Testnet
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

if "ws_started" not in st.session_state:
    start_ws()
    st.session_state.ws_started = True

# ✅ Market-Making Simulation
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

# ✅ Dummy Order Feature
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

# ✅ Check if Dummy Order Can Execute
if st.session_state.pending_order and st.session_state.pending_order["status"] == "OPEN":
    latest_price = st.session_state.price_data[-1]["price"] if st.session_state.price_data else None
    if latest_price:
        if (st.session_state.pending_order["type"] == "BUY" and latest_price <= st.session_state.pending_order["price"]) or \
           (st.session_state.pending_order["type"] == "SELL" and latest_price >= st.session_state.pending_order["price"]):

            # Execute Order
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
