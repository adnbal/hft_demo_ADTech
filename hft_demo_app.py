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

# ✅ Streamlit Config
st.set_page_config(page_title="HFT + AI Signals", layout="wide")
st.title("⚡ HFT Trading App with AI Signals & Real-Time P&L (Binance Testnet)")

# ✅ Sidebar: Refresh Interval
st.sidebar.header("⚙️ Settings")
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 3)
st_autorefresh(interval=refresh_interval * 1000, key="refresh")

# ✅ Load Secrets
API_KEY = st.secrets["binance"]["api_key"]
API_SECRET = st.secrets["binance"]["api_secret"]
AI_API_KEY = st.secrets.get("openai", {}).get("api_key", None)

# ✅ Session State Initialization
for key, value in {
    "price_data": [],
    "trade_log": [],
    "pnl_data": [],
    "realized_pnl": 0.0,
    "position_qty": 0.0,
    "avg_buy_price": 0.0,
    "mode": "Simulation",
    "ai_signal": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ✅ Position Update Logic
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

# ✅ Binance Utilities
def sign(params):
    query_string = urllib.parse.urlencode(params)
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

def fetch_price(symbol="BTCUSDT"):
    try:
        response = requests.get(f"{BASE_URL}/v3/ticker/price", params={"symbol": symbol}, timeout=3)
        if response.status_code == 200:
            return float(response.json()["price"])
    except:
        return None
    return None

def fetch_order_book(symbol="BTCUSDT"):
    try:
        response = requests.get(f"{BASE_URL}/v3/depth", params={"symbol": symbol, "limit": 20}, timeout=3)
        if response.status_code == 200:
            data = response.json()
            bids = [(float(p), float(q)) for p, q in data["bids"]]
            asks = [(float(p), float(q)) for p, q in data["asks"]]
            return bids, asks
    except:
        return [], []
    return [], []

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

# ✅ Sidebar Mode
mode = st.sidebar.radio("Select Mode", ["Simulation", "Live Binance Testnet"])
st.session_state.mode = mode

# ✅ Account Info if Live
if mode == "Live Binance Testnet":
    account = fetch_account_info()
    if account:
        st.sidebar.subheader("💰 Account Balances")
        balances = {b["asset"]: b["free"] for b in account["balances"] if float(b["free"]) > 0}
        for asset, amt in balances.items():
            st.sidebar.write(f"{asset}: {amt}")

# ✅ Order Placement
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
        st.session_state.trade_log.append({"time": datetime.now(), "side": side, "price": trade_price, "qty": qty, "status": "SIMULATED"})
        st.sidebar.success("✅ Simulated order placed")
    else:
        result = place_order("BTCUSDT", side, order_type, qty, price_input)
        if "orderId" in result:
            update_positions(side, qty, trade_price)
            st.session_state.trade_log.append({"time": datetime.now(), "side": side, "price": trade_price, "qty": qty, "status": "LIVE"})
            st.sidebar.success(f"✅ Order executed: {result['orderId']}")
        else:
            st.sidebar.error(f"Error: {result}")

# ✅ P&L Calculation
if st.session_state.position_qty > 0 and price:
    unrealized = (price - st.session_state.avg_buy_price) * st.session_state.position_qty
else:
    unrealized = 0.0
st.session_state.pnl_data.append({"time": datetime.now(), "unrealized": unrealized, "realized": st.session_state.realized_pnl})

# ✅ RULE-BASED SIGNAL
signal = "HOLD"
suggested_price = price
reason = "Stable trend."
if len(st.session_state.price_data) > 10:
    df = pd.DataFrame(st.session_state.price_data)
    sma = df["price"].rolling(10).mean().iloc[-1]
    if price > sma:
        signal = "BUY"
        suggested_price = price * 0.999
        reason = "Price above 10-SMA (uptrend)."
    elif price < sma:
        signal = "SELL"
        suggested_price = price * 1.001
        reason = "Price below 10-SMA (downtrend)."

# ✅ AI SIGNAL (On-Demand)
st.subheader("🤖 AI Trading Signal")
if AI_API_KEY:
    if st.button("Get AI Recommendation"):
        with st.spinner("Fetching AI recommendation..."):
            try:
                history = [p["price"] for p in st.session_state.price_data[-20:]]
                ai_prompt = f"""
                You are an expert crypto trader. Current BTC price: {price}.
                Last 20 prices: {history}.
                Current position: {st.session_state.position_qty} BTC at avg {st.session_state.avg_buy_price}.
                Should I BUY, SELL, or HOLD? Suggest an entry/exit price in USDT and explain briefly.
                """
                headers = {"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}
                payload = {"model": "gpt-4", "messages": [{"role": "user", "content": ai_prompt}], "max_tokens": 100}
                r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
                if r.status_code == 200:
                    st.session_state.ai_signal = r.json()["choices"][0]["message"]["content"]
                else:
                    st.session_state.ai_signal = f"Error: {r.text}"
            except Exception as e:
                st.session_state.ai_signal = f"Error fetching AI signal: {e}"
    if st.session_state.ai_signal:
        st.write(f"**AI Suggestion:** {st.session_state.ai_signal}")
else:
    st.warning("No AI API key found. Add it in Streamlit secrets to enable AI recommendations.")

# ✅ Layout: Price & Depth Chart
col1, col2 = st.columns(2)
with col1:
    st.subheader("📈 Live BTC/USDT Price")
    if len(st.session_state.price_data) > 1:
        df_price = pd.DataFrame(st.session_state.price_data[-100:])
        fig = go.Figure(go.Scatter(x=df_price["time"], y=df_price["price"], mode="lines+markers", line=dict(color="blue")))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Order Book Depth (Cumulative)")
    if bids and asks:
        bids_sorted = sorted(bids, key=lambda x: x[0], reverse=True)
        asks_sorted = sorted(asks, key=lambda x: x[0])

        # Cumulative sum for bids
        bid_prices = [p for p, _ in bids_sorted]
        bid_qty_cum = []
        cum = 0
        for _, q in bids_sorted:
            cum += q
            bid_qty_cum.append(cum)

        # Cumulative sum for asks
        ask_prices = [p for p, _ in asks_sorted]
        ask_qty_cum = []
        cum = 0
        for _, q in asks_sorted:
            cum += q
            ask_qty_cum.append(cum)

        fig_depth = go.Figure()
        fig_depth.add_trace(go.Scatter(x=bid_prices, y=bid_qty_cum, mode='lines+markers', name='Bids', line=dict(color='green')))
        fig_depth.add_trace(go.Scatter(x=ask_prices, y=ask_qty_cum, mode='lines+markers', name='Asks', line=dict(color='red')))
        fig_depth.update_layout(title="Cumulative Depth", xaxis_title="Price (USDT)", yaxis_title="Cumulative Qty (BTC)", hovermode="x unified")
        st.plotly_chart(fig_depth, use_container_width=True)
    else:
        st.info("Fetching order book...")

# ✅ P&L Dashboard
st.subheader("💹 P&L Dashboard")
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
    st.plotly_chart(fig_pnl, use_container_width=True)

# ✅ Rule-Based Trading Signal
st.subheader("📢 Rule-Based Signal")
st.write(f"**Signal:** {signal} at ~{suggested_price:.2f} USDT ({reason})")

# ✅ Trade Log
st.subheader("📜 Trade Log")
if st.session_state.trade_log:
    st.dataframe(pd.DataFrame(st.session_state.trade_log))
else:
    st.info("No trades yet.")
