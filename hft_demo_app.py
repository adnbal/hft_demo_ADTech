import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import random
import time

# ---------- Page Config ----------
st.set_page_config(page_title="HFT Dashboard", layout="wide")

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

# ---------- Cached CoinGecko API ----------
@st.cache_data(ttl=60)
def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,binancecoin,cardano,ripple&vs_currencies=usd"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}

data = get_crypto_prices()
price = float(data.get("bitcoin", {}).get("usd", 30000))

ticker_prices = {
    "BTC": float(data.get("bitcoin", {}).get("usd", 30000)),
    "ETH": float(data.get("ethereum", {}).get("usd", 2000)),
    "BNB": float(data.get("binancecoin", {}).get("usd", 300)),
    "ADA": float(data.get("cardano", {}).get("usd", 0.5)),
    "XRP": float(data.get("ripple", {}).get("usd", 0.7))
}

# ---------- Improved AI Market Signal ----------
def ai_market_signal():
    if len(st.session_state.price_data) < 10:
        return "HOLD", "Collecting more data for better prediction."
    prices = [p[1] for p in st.session_state.price_data[-10:]]
    trend = (prices[-1] - prices[0]) / prices[0]
    volatility = max(prices) - min(prices)

    if trend > 0.0005:  # 0.05% change triggers BUY
        reason = f"Uptrend of {trend*100:.3f}% with volatility ${volatility:.2f}."
        return "BUY", f"Strong bullish momentum detected. {reason}"
    elif trend < -0.0005:  # 0.05% down triggers SELL
        reason = f"Downtrend of {trend*100:.3f}% with volatility ${volatility:.2f}."
        return "SELL", f"Bearish trend likely. {reason}"
    else:
        return "HOLD", f"Price stable. Volatility ${volatility:.2f}. Waiting for a clear trend."

# ---------- Ticker ----------
ticker_html = "<div class='ticker-container'><div class='ticker-text'>"
for asset, val in ticker_prices.items():
    change = random.uniform(-1.5, 1.5)
    color = "price-up" if change >= 0 else "price-down"
    ticker_html += f"{asset}: <span class='{color}'>{val:.2f}</span> ({change:+.2f}%) | "
ticker_html += "</div></div>"
st.markdown(ticker_html, unsafe_allow_html=True)

# ---------- Price History ----------
volume = random.randint(50, 500)
# Add small randomness to make AI dynamic
price += random.uniform(-5, 5)
st.session_state.price_data.append((time.strftime('%H:%M:%S'), price, volume))

# ---------- Layout ----------
left, middle, right = st.columns([1.5, 3, 1.5])

# ---------- AI Panel ----------
with left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>🤖 AI Market Intelligence</div>", unsafe_allow_html=True)
    ai_signal, ai_text = ai_market_signal()
    color = "#39ff14" if ai_signal == "BUY" else "#ff073a" if ai_signal == "SELL" else "#ffff00"
    st.markdown(f"<div style='text-align:center;font-size:24px;font-weight:bold;background-color:{color};padding:12px;border-radius:10px;'>{ai_signal}</div>", unsafe_allow_html=True)
    if st.button("🔍 Why this forecast?"):
        st.session_state.show_modal = True
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- AI Modal ----------
if st.session_state.show_modal:
    st.markdown(
        """
        <style>
        .overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7); z-index: 9998;
        }
        .popup {
            background: #1e1e1e; color: white; padding: 20px;
            border-radius: 10px; width: 40%; margin: auto;
            position: fixed; top: 25%; left: 0; right: 0;
            box-shadow: 0 0 30px #39ff14;
            z-index: 9999;
        }
        </style>
        <div class="overlay"></div>
        <div class="popup">
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🤖 AI Market Forecast")
    st.write(f"**Signal:** {ai_signal}")
    st.write(f"**Reason:** {ai_text}")
    st.write("📊 Based on last 10 price points & volatility analysis.")

    if st.button("Close"):
        st.session_state.show_modal = False

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Main Panel ----------
with middle:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>📈 Price, Volume & Order Book</div>", unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.price_data, columns=['time', 'price', 'volume'])

    # Price + Volume Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['price'], name="Price", mode='lines+markers', line=dict(color='lime')))
    fig.add_trace(go.Bar(x=df['time'], y=df['volume'], name="Volume", yaxis="y2", marker=dict(color='blue', opacity=0.5)))
    fig.update_layout(template="plotly_dark", xaxis=dict(title="Time"),
                      yaxis=dict(title="Price (USD)"),
                      yaxis2=dict(title="Volume", overlaying="y", side="right"),
                      height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Bid/Ask Spread Chart
    st.subheader("📊 Bid/Ask Spread")
    bids = sorted([price - random.uniform(0.5, 2) for _ in range(10)], reverse=True)
    asks = sorted([price + random.uniform(0.5, 2) for _ in range(10)])
    bid_volumes = [random.randint(1, 10) for _ in bids]
    ask_volumes = [random.randint(1, 10) for _ in asks]

    ba_fig = go.Figure()
    ba_fig.add_trace(go.Bar(x=bids, y=bid_volumes, name="Bids", marker=dict(color="green")))
    ba_fig.add_trace(go.Bar(x=asks, y=ask_volumes, name="Asks", marker=dict(color="red")))
    ba_fig.update_layout(template="plotly_dark", xaxis_title="Price", yaxis_title="Volume", barmode="overlay", height=300)
    st.plotly_chart(ba_fig, use_container_width=True)

    # PnL Charts
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

    st.subheader("💰 Total Realized Profit")
    st.markdown(f"<div style='font-size:26px;color:#39ff14;text-align:center;'>${cum_pnl:.2f}</div>", unsafe_allow_html=True)

    if pnl:
        pnl_fig = go.Figure()
        pnl_fig.add_trace(go.Scatter(x=[t['time'] for t in st.session_state.trade_log], y=pnl, mode='lines', name='Realized PnL', line=dict(color='cyan')))
        pnl_fig.update_layout(template="plotly_dark", title="Realized PnL Over Time", height=300)
        st.plotly_chart(pnl_fig, use_container_width=True)

    # Unrealized PnL
    current_unrealized = sum((price - pos['price']) * pos['qty'] for pos in st.session_state.positions)
    unrealized_color = "#39ff14" if current_unrealized >= 0 else "#ff073a"
    st.markdown(f"<div style='text-align:center;color:{unrealized_color};font-size:20px;'>Unrealized PnL: ${current_unrealized:.2f}</div>", unsafe_allow_html=True)

    # Trade Log
    st.subheader("📜 Trade Log")
    if st.session_state.trade_log:
        st.dataframe(pd.DataFrame(st.session_state.trade_log))
    else:
        st.write("No trades yet.")

# ---------- Trading Panel ----------
with right:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>🛠 Trading Panel</div>", unsafe_allow_html=True)

    mode = st.radio("Mode", ["Simulation", "Live"])
    side = st.radio("Side", ["BUY", "SELL"])
    qty = st.number_input("Quantity", min_value=0.001, step=0.001, value=0.001)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    limit_price = st.number_input("Limit Price (USD)", value=price, step=0.01)

    if st.button("Submit Order"):
        trade_price = price if order_type == "MARKET" else limit_price
        st.session_state.trade_log.append({"time": time.strftime('%H:%M:%S'), "side": side, "qty": qty, "price": trade_price})
        if side == "BUY":
            st.session_state.positions.append({"qty": qty, "price": trade_price})
        elif st.session_state.positions:
            st.session_state.positions.pop(0)
        st.success(f"Order placed: {side} {qty} @ {trade_price} ({order_type}) [{mode}]")
    st.markdown("</div>", unsafe_allow_html=True)
