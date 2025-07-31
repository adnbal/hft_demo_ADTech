import streamlit as st
import pandas as pd
import requests
import hmac
import hashlib
import time
import urllib.parse
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ✅ Binance Testnet API Base
BASE_URL = "https://testnet.binance.vision/api"

# ✅ Streamlit Page Config
st.set_page_config(page_title="HFT Trading with P&L", layout="wide")
st.title("⚡ HFT Trading App with Real-Time P&L (Binance Testnet)")

# ✅ Sidebar: Settings & Refresh
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 3)
st_autorefresh(interval=refresh_interval * 1000, key="refresh")

# ✅ Load Binance API keys from secrets
API_KEY = st.secrets["binance"]["api_key"]
API_SECRET = st.secrets["binance"]["api_secret"]

# ✅ Session State Initialization
for key, value in {
    "price_data": [],
    "trade_log": [],
    "pnl_data": [],
    "realized_pnl": 0.0,
    "position_qty": 0.0,
    "avg_buy_price": 0.0,
    "mode": "Simulation"
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ✅ Define update_positions() BEFORE using it
def update_positions(side, qty, trade_price):
    if side == "BUY":
        total_cost = st.session_state.avg_buy_price * st.session_state.position_qty
        total_cost += trade_price * qty
        st.session_state.position_qty += qty
        st.session_state.avg_buy_price = total_cost / st.session_state.position_qty
    elif side == "SELL":
        if st.session_state.position_qty >= qty:
            realized = (trade_price - st.session_state.avg_buy_price) * qty
            st.session_state.realized_pnl += realized
            st.session_state.position_qty -= qty
            if st.session_state.position_qty == 0:
                st.session_state.avg_buy_price = 0.0

# ✅ Utility: Signature for Binance API
def sign(params):
    query_string = urllib.parse.urlencode(params)
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

# ✅ Get Live Price
def fetch_price(symbol="BTCUSDT"):
    try:
        response = requests.get(f"{BASE_URL}/v3/ticker/price", params={"symbol": symbol}, timeout=3)
        if response.status_code == 200:
            return float(response.json()["price"])
    except:
        return None
    return None

# ✅ Get Order Book
def fetch_order_book(symbol="BTCUSDT"):
    try:
        response = requests.get(f"{BASE_URL}/v3/depth", params={"symbol": symbol, "limit": 5}, timeout=3)
        if response.status_code == 200:
            data = response.json()
            bids = [(float(p), float(q)) for p, q in data["bids"]]
            asks = [(float(p), float(q)) for p, q in data["asks"]]
            return bids, asks
    except:
        return [], []
    return [], []

# ✅ Account Info
def fetch_account_info():
    ts = int(time.time() * 1000)
    params = {"timestamp": ts}
    params["signature"] = sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    try:
        res = requests.get(f"{BASE_URL}/v3/account", headers=headers, params=params)
        if res.status_code == 200:
            return res.json()
    except:
        return None
    return None

# ✅ Place Real Order
def place_order(symbol, side, order_type, quantity, price=None):
    ts = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
        "timestamp": ts
    }
    if order_type == "LIMIT":
        params["timeInForce"] = "GTC"
        params["price"] = price
    params["signature"] = sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}
    try:
        res = requests.post(f"{BASE_URL}/v3/order", headers=headers, params=params)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

# ✅ Fetch Live Data
price = fetch_price()
bids, asks = fetch_order_book()
if price:
    st.session_state.price_data.append({"time": datetime.now(), "price": price})

# ✅ Sidebar: Mode Toggle
mode = st.sidebar.radio("Select Mode", ["Simulation", "Live Binance Testnet"])
st.session_state.mode = mode

# ✅ Sidebar: Account Info
if mode == "Live Binance Testnet":
    account = fetch_account_info()
    if account:
        balances = {b["asset"]: b["free"] for b in account["balances"] if float(b["free"]) > 0}
        st.sidebar.subheader("💰 Account Balances")
        for asset, amt in balances.items():
            st.sidebar.write(f"{asset}: {amt}")

# ✅ Order Placement UI
st.sidebar.subheader("🛒 Place Order")
order_type = st.sidebar.selectbox("Order Type", ["MARKET", "LIMIT"])
side = st.sidebar.selectbox("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity (BTC)", min_value=0.0001, value=0.001)
price_input = None
if order_type == "LIMIT":
    price_input = st.sidebar.number_input("Limit Price (USDT)", min_value=10000.0, value=price if price else 30000.0)

if st.sidebar.button("Submit Order"):
    trade_price = price_input if order_type == "LIMIT" else price
    if mode == "Simulation":
        update_positions(side, qty, trade_price)
        st.session_state.trade_log.append({
            "time": datetime.now(),
            "side": side,
            "price": trade_price,
            "qty": qty,
            "status": "SIMULATED"
        })
        st.sidebar.success("✅ Simulated order placed")
    else:
        result = place_order("BTCUSDT", side, order_type, qty, price_input)
        if "orderId" in result:
            update_positions(side, qty, trade_price)
            st.session_state.trade_log.append({
                "time": datetime.now(),
                "side": side,
                "price": trade_price,
                "qty": qty,
                "status": "LIVE"
            })
            st.sidebar.success(f"✅ Order executed: {result['orderId']}")
        else:
            st.sidebar.error(f"Error: {result}")

# ✅ Unrealized P&L Calculation
if st.session_state.position_qty > 0 and price:
    unrealized = (price - st.session_state.avg_buy_price) * st.session_state.position_qty
else:
    unrealized = 0.0

# ✅ Save P&L data for chart
st.session_state.pnl_data.append({
    "time": datetime.now(),
    "unrealized": unrealized,
    "realized": st.session_state.realized_pnl
})

# ✅ Layout: Price & Order Book
col1, col2 = st.columns(2)
with col1:
    st.subheader("📈 Live BTC/USDT Price")
    if len(st.session_state.price_data) > 1:
        df_price = pd.DataFrame(st.session_state.price_data[-100:])
        fig = go.Figure(go.Scatter(x=df_price["time"], y=df_price["price"], mode="lines+markers", line=dict(color="blue")))
        fig.update_layout(title="BTC/USDT Price", xaxis_title="Time", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Waiting for price data...")

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
        st.info("Fetching order book...")

# ✅ P&L Dashboard
st.subheader("💹 Real-Time P&L Dashboard")
st.metric("Position Qty", f"{st.session_state.position_qty:.4f} BTC")
st.metric("Average Buy Price", f"{st.session_state.avg_buy_price:.2f} USDT")
st.metric("Unrealized P&L", f"{unrealized:.2f} USDT")
st.metric("Realized P&L", f"{st.session_state.realized_pnl:.2f} USDT")

# ✅ P&L Chart
if len(st.session_state.pnl_data) > 1:
    df_pnl = pd.DataFrame(st.session_state.pnl_data[-100:])
    fig_pnl = go.Figure()
    fig_pnl.add_trace(go.Scatter(x=df_pnl["time"], y=df_pnl["unrealized"], mode="lines", name="Unrealized P&L", line=dict(color="orange")))
    fig_pnl.add_trace(go.Scatter(x=df_pnl["time"], y=df_pnl["realized"], mode="lines", name="Realized P&L", line=dict(color="green")))
    fig_pnl.update_layout(title="P&L Over Time", xaxis_title="Time", yaxis_title="P&L (USDT)")
    st.plotly_chart(fig_pnl, use_container_width=True)

# ✅ Trade Log
st.subheader("📜 Trade Log")
if st.session_state.trade_log:
    df_trades = pd.DataFrame(st.session_state.trade_log)
    st.dataframe(df_trades)
else:
    st.info("No trades yet.")
