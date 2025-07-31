import streamlit as st
import pandas as pd
import requests
import hmac, hashlib, time, urllib.parse
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ✅ Binance Testnet API
BASE_URL = "https://testnet.binance.vision/api"

# ✅ Streamlit Config
st.set_page_config(page_title="HFT + AI Signals", layout="wide")
st.title("⚡ HFT Trading App with AI Signals & Real-Time P&L")

# ✅ Sidebar: Refresh Interval
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 3)
st_autorefresh(interval=refresh_interval * 1000, key="refresh")

# ✅ Secrets
API_KEY = st.secrets.get("binance", {}).get("api_key", "")
API_SECRET = st.secrets.get("binance", {}).get("api_secret", "")
OPENAI_KEY = st.secrets.get("openai", {}).get("api_key", "")

# ✅ Initialize Session State
for key, val in {
    "price_data": [],
    "trade_log": [],
    "realized_pnl": 0.0,
    "position_qty": 0.0,
    "avg_buy_price": 0.0,
    "ai_signal": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ✅ Utility Functions
def update_positions(side, qty, price):
    if side == "BUY":
        total_cost = st.session_state.avg_buy_price * st.session_state.position_qty
        total_cost += price * qty
        st.session_state.position_qty += qty
        st.session_state.avg_buy_price = total_cost / st.session_state.position_qty
    else:  # SELL
        if st.session_state.position_qty >= qty:
            pnl = (price - st.session_state.avg_buy_price) * qty
            st.session_state.realized_pnl += pnl
            st.session_state.position_qty -= qty
            if st.session_state.position_qty == 0:
                st.session_state.avg_buy_price = 0.0

def sign(params):
    query = urllib.parse.urlencode(params)
    return hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()

def fetch_price():
    try:
        r = requests.get(f"{BASE_URL}/v3/ticker/price", params={"symbol": "BTCUSDT"}, timeout=3)
        if r.status_code == 200:
            return float(r.json()["price"])
    except:
        return None
    return None

# ✅ Fetch Price
price = fetch_price()
if price:
    st.session_state.price_data.append({"time": datetime.now(), "price": price})

# ✅ Place Order (Simulation Only for Now)
order_type = st.sidebar.selectbox("Order Type", ["MARKET"])
side = st.sidebar.selectbox("Side", ["BUY", "SELL"])
qty = st.sidebar.number_input("Quantity (BTC)", value=0.001, min_value=0.0001)
if st.sidebar.button("Submit Order"):
    update_positions(side, qty, price)
    st.session_state.trade_log.append({"time": datetime.now(), "side": side, "price": price, "qty": qty})
    st.sidebar.success(f"Simulated {side} at {price:.2f}")

# ✅ Charts
col1, col2 = st.columns(2)
with col1:
    st.subheader("📈 Price Chart")
    if len(st.session_state.price_data) > 1:
        df = pd.DataFrame(st.session_state.price_data[-50:])
        fig = go.Figure(go.Scatter(x=df["time"], y=df["price"], mode="lines"))
        st.plotly_chart(fig, use_container_width=True)
with col2:
    st.subheader("💹 P&L")
    st.metric("Position Qty", f"{st.session_state.position_qty:.4f}")
    st.metric("Avg Buy Price", f"{st.session_state.avg_buy_price:.2f}")
    st.metric("Realized P&L", f"{st.session_state.realized_pnl:.2f}")

# ✅ AI Recommendation
st.subheader("🤖 AI Trading Signal")
if OPENAI_KEY:
    if st.button("Get AI Recommendation"):
        st.write("🔍 Fetching AI signal...")
        try:
            prompt = f"BTC price: {price}, history: {[p['price'] for p in st.session_state.price_data[-10:]]}. Suggest BUY, SELL or HOLD with price."
            headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100
            }
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            if r.status_code == 200:
                st.session_state.ai_signal = r.json()["choices"][0]["message"]["content"]
            else:
                st.session_state.ai_signal = f"Error: {r.text}"
        except Exception as e:
            st.session_state.ai_signal = f"Error: {str(e)}"
else:
    st.warning("⚠️ No OpenAI API key in secrets.")

if st.session_state.ai_signal:
    st.write(f"**AI Suggestion:** {st.session_state.ai_signal}")
