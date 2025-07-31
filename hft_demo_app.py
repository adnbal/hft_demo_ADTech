import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time
import random
from streamlit_autorefresh import st_autorefresh

# ---------- Page Config ----------
st.set_page_config(page_title="HFT Dashboard", layout="wide")

# ---------- Auto-refresh every 15s ----------
st_autorefresh(interval=15000, key="refresh")

# ---------- Custom CSS ----------
st.markdown("""
    <style>
        body { background-color: #0e1117; color: white; }
        .neon {
            font-size: 22px; font-weight: bold; color: white;
            text-align: center; padding: 12px; border-radius: 8px;
            margin-bottom: 15px; border: 2px solid white;
            background-color: #111; box-shadow: 0 0 10px #39ff14, 0 0 20px #39ff14;
            animation: flicker 1.5s infinite alternate;
        }
        @keyframes flicker {
            0% { text-shadow: 0 0 5px #39ff14, 0 0 10px #39ff14; }
            100% { text-shadow: 0 0 20px #39ff14, 0 0 40px #39ff14; }
        }
        .panel {
            background-color: #1e1e1e; border-radius: 10px;
            padding: 15px; border: 2px solid white; height: 100%;
        }
        .ticker-container {
            width: 100%; overflow: hidden; white-space: nowrap;
            background-color: #1a1a1a; border-bottom: 2px solid #39ff14; padding: 8px 0;
        }
        .ticker-text {
            display: inline-block; animation: ticker 20s linear infinite;
            font-size: 18px; color: white;
        }
        @keyframes ticker {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        .price-up { color: #39ff14; font-weight: bold; }
        .price-down { color: #ff073a; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []
if "unrealized_history" not in st.session_state:
    st.session_state.unrealized_history = []
    st.session_state.unrealized_time = []
if "show_modal" not in st.session_state:
    st.session_state.show_modal = False

# ---------- CoinGecko API (one request for all coins) ----------
def get_multiple_crypto_prices(symbols):
    ids = ",".join(symbols)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            st.warning(f"API Error {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching prices: {e}")
    return {}

crypto_ids = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "ADA": "cardano",
    "XRP": "ripple"
}

data = get_multiple_crypto_prices(list(crypto_ids.values()))

# Main price (BTC)
price = float(data.get("bitcoin", {}).get("usd", 30000))

# Ticker prices
ticker_prices = {symbol: float(data.get(cg_id, {}).get("usd", 30000)) for symbol, cg_id in crypto_ids.items()}

# ---------- AI Market Signal ----------
def ai_market_signal():
    if len(st.session_state.price_data) < 10:
        return "HOLD", "Collecting more data for better prediction."
    prices = [p[1] for p in st.session_state.price_data[-10:]]
    trend = (prices[-1] - prices[0]) / prices[0]
    if trend > 0.002:
        return "BUY", "Bullish trend detected. Upward momentum strong."
    elif trend < -0.002:
        return "SELL", "Bearish trend detected. Downward momentum likely."
    else:
        return "HOLD", "Market neutral. No strong signal."

# ---------- Ticker Bar ----------
ticker_html = "<div class='ticker-container'><div class='ticker-text'>"
for asset, val in ticker_prices.items():
    change = random.uniform(-1.5, 1.5)  # mock % change for ticker animation
    color_class = "price-up" if change >= 0 else "price-down"
    ticker_html += f"&nbsp;&nbsp;{asset}: <span class='{color_class}'>{val:.2f}</span> ({change:+.2f}%)&nbsp;&nbsp;|"
ticker_html += "</div></div>"
st.markdown(ticker_html, unsafe_allow_html=True)

# ---------- Update Price History ----------
st.session_state.price_data.append((time.strftime('%H:%M:%S'), price, random.randint(50, 200)))

# ---------- Layout ----------
left, middle, right = st.columns([1.5, 3, 1.5])

# ---------- AI Panel ----------
with left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>🤖 AI Market Intelligence</div>", unsafe_allow_html=True)
    ai_signal, ai_text = ai_market_signal()
    color = "#39ff14" if ai_signal == "BUY" else "#ff073a" if ai_signal == "SELL" else "#ffff00"
    st.markdown(f"""
        <div style='text-align:center;font-size:24px;font-weight:bold;color:white;
        background-color:{color};border-radius:10px;padding:12px;margin-bottom:15px;
        box-shadow:0 0 20px {color},0 0 40px {color};'>{ai_signal}</div>
    """, unsafe_allow_html=True)
    if st.button("🔍 Why this forecast?"):
        st.session_state.show_modal = True
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Modal Popup ----------
if st.session_state.show_modal:
    modal_html = f"""
    <div id="myModal" style="
        position: fixed; z-index: 1000; left: 0; top: 0;
        width: 100%; height: 100%; background-color: rgba(0,0,0,0.7);
        display: flex; justify-content: center; align-items: center;">
        <div style="
            background-color: #1e1e1e; padding: 20px; border-radius: 10px;
            width: 50%; max-width: 600px; color: white;
            box-shadow: 0 0 30px #39ff14;">
            <h2 style="color:#39ff14;">AI Market Forecast Details</h2>
            <p><b>Signal:</b> {ai_signal}</p>
            <p><b>Reason:</b> {ai_text}</p>
            <p>🔍 Based on last 10 interval price trends and market momentum.</p>
            <button onclick="document.getElementById('myModal').style.display='none';"
                style="margin-top: 15px; background:#39ff14; color:black; padding:10px 20px; border:none; border-radius:5px; font-weight:bold;">
                Close
            </button>
        </div>
    </div>
    """
    st.markdown(modal_html, unsafe_allow_html=True)

# ---------- Main Panel ----------
with middle:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>⚡ Live Trading Dashboard</div>", unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.price_data, columns=['time', 'price', 'volume'])

    # Price Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['price'], mode='lines+markers', name='Price', line=dict(color='lime')))
    fig.update_layout(template="plotly_dark", xaxis=dict(title="Time"), yaxis=dict(title="Price (USD)"), height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Total Profit & PnL
    pnl, cum_pnl, open_positions = [], 0, []
    for trade in st.session_state.trade_log:
        if trade["side"] == "BUY":
            open_positions.append((trade["qty"], trade["price"]))
            cum_pnl -= trade["qty"] * trade["price"]
        else:
            if open_positions:
                qty_to_sell = trade["qty"]
                while qty_to_sell > 0 and open_positions:
                    qty_open, price_open = open_positions[0]
                    if qty_open <= qty_to_sell:
                        cum_pnl += qty_open * trade["price"]
                        qty_to_sell -= qty_open
                        open_positions.pop(0)
                    else:
                        cum_pnl += qty_to_sell * trade["price"]
                        open_positions[0] = (qty_open - qty_to_sell, price_open)
                        qty_to_sell = 0
        pnl.append(cum_pnl)

    st.markdown(f"""
        <div style='text-align:center;font-size:30px;font-weight:bold;margin:20px;
        padding:15px;border-radius:10px;background:#111;border:3px solid white;
        box-shadow:0 0 20px #39ff14,0 0 40px #39ff14;color:#39ff14;'>
        💰 TOTAL PROFIT: {cum_pnl:.2f} USD
        </div>
    """, unsafe_allow_html=True)

    if pnl:
        pnl_fig = go.Figure()
        pnl_fig.add_trace(go.Scatter(x=[t["time"] for t in st.session_state.trade_log], y=pnl,
                                     mode='lines', name='Realized PnL', line=dict(color='cyan')))
        pnl_fig.update_layout(template="plotly_dark", title="📊 Realized PnL", height=300)
        st.plotly_chart(pnl_fig, use_container_width=True)

    # Unrealized PnL
    current_unrealized = 0
    if st.session_state.positions:
        for pos in st.session_state.positions:
            current_unrealized += (price - pos["price"]) * pos["qty"]
    st.session_state.unrealized_history.append(current_unrealized)
    st.session_state.unrealized_time.append(time.strftime('%H:%M:%S'))
    unrealized_color = "#39ff14" if current_unrealized >= 0 else "#ff073a"
    st.markdown(f"""
        <div style='text-align:center;font-size:22px;font-weight:bold;margin:10px;
        padding:10px;border-radius:8px;background:#111;border:2px solid {unrealized_color};
        box-shadow:0 0 15px {unrealized_color};color:{unrealized_color};'>
        Unrealized PnL: {current_unrealized:.2f} USD
        </div>
    """, unsafe_allow_html=True)

# ---------- Trading Panel ----------
with right:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>🛠 Trading Panel</div>", unsafe_allow_html=True)
    side = st.radio("Side", ["BUY", "SELL"])
    qty = st.number_input("Quantity", min_value=0.001, step=0.001, value=0.001)
    if st.button("Submit Order"):
        st.session_state.trade_log.append({"time": time.strftime('%H:%M:%S'), "side": side, "qty": qty, "price": price})
        if side == "BUY":
            st.session_state.positions.append({"qty": qty, "price": price})
        else:
            if st.session_state.positions:
                st.session_state.positions.pop(0)
        st.success(f"Order placed: {side} {qty} @ {price}")
    st.markdown("</div>", unsafe_allow_html=True)
