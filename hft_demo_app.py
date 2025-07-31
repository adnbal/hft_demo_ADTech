import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# ---------- Page Config ----------
st.set_page_config(page_title="HFT Dashboard", layout="wide")

# ---------- Auto-refresh ----------
st_autorefresh(interval=5000, key="refresh")

# ---------- Custom CSS ----------
st.markdown("""
    <style>
        body { background-color: #0e1117; color: white; }
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

# Initialize trading UI state
if "selected_side" not in st.session_state:
    st.session_state.selected_side = "BUY"
if "limit_price" not in st.session_state:
    st.session_state.limit_price = 30000.0

# ---------- Mock Live Price ----------
def get_live_price():
    base_price = 30000
    return base_price + random.uniform(-200, 200)

# ---------- Ticker Bar ----------
assets = {
    "BTC/USD": 30000 + random.uniform(-150, 150),
    "ETH/USD": 2000 + random.uniform(-20, 20),
    "AAPL": 180 + random.uniform(-2, 2),
    "TSLA": 250 + random.uniform(-3, 3),
    "AMZN": 135 + random.uniform(-1, 1)
}
ticker_html = "<div class='ticker-container'><div class='ticker-text'>"
for asset, price_val in assets.items():
    change = random.uniform(-1.5, 1.5)
    color_class = "price-up" if change >= 0 else "price-down"
    ticker_html += f"&nbsp;&nbsp;{asset}: <span class='{color_class}'>{price_val:.2f}</span> ({change:+.2f}%)&nbsp;&nbsp;|"
ticker_html += "</div></div>"
st.markdown(ticker_html, unsafe_allow_html=True)

# ---------- AI Market Signal ----------
def ai_market_signal():
    if len(st.session_state.price_data) < 10:
        return "HOLD", "Collecting more data for better prediction.", None
    
    prices = [p[1] for p in st.session_state.price_data[-10:]]
    volumes = [p[2] for p in st.session_state.price_data[-10:]]
    trend = (prices[-1] - prices[0]) / prices[0]
    avg_volume = sum(volumes) / len(volumes)
    current_volume = volumes[-1]
    current_price = prices[-1]

    if trend > 0.002:
        forecast_price = current_price * (1 + abs(trend))
        reason = f"Price trend bullish. Expected short-term target: ${forecast_price:.2f}."
        if current_volume > avg_volume:
            reason += " Volume above average, strong buying."
        return "BUY", reason, forecast_price

    elif trend < -0.002:
        forecast_price = current_price * (1 - abs(trend))
        reason = f"Downward trend detected. Expected short-term target: ${forecast_price:.2f}."
        if current_volume > avg_volume:
            reason += " High selling pressure."
        return "SELL", reason, forecast_price

    else:
        return "HOLD", "Market neutral. No strong movement.", current_price

# ---------- Update Price Data ----------
price = get_live_price()
st.session_state.price_data.append((time.strftime('%H:%M:%S'), price, random.randint(10, 100)))
df = pd.DataFrame(st.session_state.price_data, columns=['time', 'price', 'volume'])

# Get AI Advice
ai_signal, ai_text, forecast_price = ai_market_signal()

# ✅ Auto-sync AI advice into UI fields
if ai_signal != "HOLD" and forecast_price:
    st.session_state.selected_side = ai_signal
    st.session_state.limit_price = round(forecast_price, 2)

# ---------- Layout ----------
left, middle, right = st.columns([1.5, 3, 1.5])

# ---------- AI Panel ----------
with left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:22px;font-weight:bold;text-align:center;padding:12px;border-radius:8px;margin-bottom:15px;border:2px solid #00FFFF;box-shadow:0 0 15px #00FFFF,0 0 30px #00FFFF;'>🤖 AI Market Intelligence</div>", unsafe_allow_html=True)
    
    color = "#39ff14" if ai_signal == "BUY" else "#ff073a" if ai_signal == "SELL" else "#ffff00"
    
    st.markdown(f"""
        <div style='
            text-align:center;
            font-size:28px;
            font-weight:bold;
            color:{color};
            border: 3px solid {color};
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 15px;
            background: transparent;
            box-shadow: 0 0 15px {color}, 0 0 30px {color};
            animation: pulse 1.5s infinite alternate;
        '>{ai_signal}</div>
        <style>
            @keyframes pulse {{
                0% {{ box-shadow: 0 0 10px {color}, 0 0 20px {color}; }}
                100% {{ box-shadow: 0 0 20px {color}, 0 0 40px {color}; }}
            }}
        </style>
    """, unsafe_allow_html=True)

    if st.button("🔍 Why this forecast?"):
        st.session_state.show_modal = True
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- AI Modal ----------
if st.session_state.show_modal:
    st.markdown("""
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
    """, unsafe_allow_html=True)
    st.markdown("### 🤖 AI Market Forecast")
    st.write(f"**Signal:** {ai_signal}")
    st.write(f"**Reason:** {ai_text}")
    st.write("📊 Based on trend + volume analysis.")
    if st.button("Close"):
        st.session_state.show_modal = False
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Main Panel ----------
with middle:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:22px;font-weight:bold;text-align:center;padding:12px;border-radius:8px;margin-bottom:15px;border:2px solid #FFD700;box-shadow:0 0 15px #FFD700,0 0 30px #FFD700;'>⚡ High Frequency Trading Dashboard</div>", unsafe_allow_html=True)

    # Price + Volume Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['time'], y=df['volume'], name='Volume', yaxis='y2', marker=dict(color='orange', opacity=0.5)))
    fig.add_trace(go.Scatter(x=df['time'], y=df['price'], mode='lines+markers', name='Price', line=dict(color='lime', width=3)))
    fig.update_layout(template="plotly_dark", xaxis=dict(title="Time"),
                      yaxis=dict(title="Price"), yaxis2=dict(title="Volume", overlaying="y", side="right"), height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Trade Log
    st.subheader("📜 Trade Log")
    if st.session_state.trade_log:
        st.dataframe(pd.DataFrame(st.session_state.trade_log))
    else:
        st.info("No trades yet.")

# ---------- Trading Panel ----------
with right:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:22px;font-weight:bold;text-align:center;padding:12px;border-radius:8px;margin-bottom:15px;border:2px solid #FF00FF;box-shadow:0 0 15px #FF00FF,0 0 30px #FF00FF;'>🛠 Trading Panel</div>", unsafe_allow_html=True)

    # Inputs (auto-synced with AI)
    mode = st.radio("Mode", ["Simulation", "Live"])
    side = st.radio("Side", ["BUY", "SELL"], index=0 if st.session_state.selected_side == "BUY" else 1)
    qty = st.number_input("Quantity", min_value=1.0, step=1.0, value=1.0)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    limit_price = st.number_input("Limit Price (USD)", value=st.session_state.limit_price, step=0.01)

    if st.button("Submit Order"):
        trade_price = price if order_type == "MARKET" else limit_price
        st.session_state.trade_log.append({"time": time.strftime('%H:%M:%S'), "side": side, "qty": qty, "price": trade_price})
        if side == "BUY":
            st.session_state.positions.append({"qty": qty, "price": trade_price})
        else:
            if st.session_state.positions:
                st.session_state.positions.pop(0)
        st.success(f"Order placed: {side} {qty} @ {trade_price}")

    if ai_signal != "HOLD" and forecast_price:
        if st.button("🤖 Take AI Advice"):
            st.session_state.trade_log.append({
                "time": time.strftime('%H:%M:%S'),
                "side": ai_signal,
                "qty": qty,
                "price": round(forecast_price, 2)
            })
            if ai_signal == "BUY":
                st.session_state.positions.append({"qty": qty, "price": forecast_price})
            else:
                if st.session_state.positions:
                    st.session_state.positions.pop(0)
            st.success(f"✅ Executed AI Advice: {ai_signal} {qty} @ ${forecast_price:.2f}")

    st.markdown("</div>", unsafe_allow_html=True)
