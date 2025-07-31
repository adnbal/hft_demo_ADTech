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
        change_pct = ((forecast_price - current_price) / current_price) * 100
        reason = f"Price trend bullish. Expected short-term target: ${forecast_price:.2f} ({change_pct:+.2f}%)."
        if current_volume > avg_volume:
            reason += " Volume above average, strong buying."
        return "BUY", reason, forecast_price

    elif trend < -0.002:
        forecast_price = current_price * (1 - abs(trend))
        change_pct = ((forecast_price - current_price) / current_price) * 100
        reason = f"Downward trend detected. Expected short-term target: ${forecast_price:.2f} ({change_pct:+.2f}%)."
        if current_volume > avg_volume:
            reason += " High selling pressure."
        return "SELL", reason, forecast_price

    else:
        return "HOLD", "Market neutral. No strong movement.", current_price

# ---------- Update Price Data ----------
price = get_live_price()
st.session_state.price_data.append((time.strftime('%H:%M:%S'), price, random.randint(10, 100)))
df = pd.DataFrame(st.session_state.price_data, columns=['time', 'price', 'volume'])

# Prepare OHLC data for candlestick (last 15 ticks grouped)
candles = []
for i in range(0, len(df), 3):
    subset = df.iloc[i:i+3]
    if len(subset) >= 3:
        candles.append({
            "time": subset["time"].iloc[-1],
            "open": subset["price"].iloc[0],
            "high": subset["price"].max(),
            "low": subset["price"].min(),
            "close": subset["price"].iloc[-1]
        })
candles_df = pd.DataFrame(candles)

# ---------- Market Depth Simulation ----------
bid_size = random.randint(50, 200)
ask_size = random.randint(50, 200)

# ---------- Get AI Advice ----------
ai_signal, ai_text, forecast_price = ai_market_signal()
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
    st.markdown(f"<div style='text-align:center;font-size:28px;color:{color};'>{ai_signal}</div>", unsafe_allow_html=True)
    st.write(f"**AI Suggestion:** {ai_text}")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Main Panel ----------
with middle:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:22px;font-weight:bold;text-align:center;padding:12px;border-radius:8px;margin-bottom:15px;border:2px solid #FFD700;box-shadow:0 0 15px #FFD700,0 0 30px #FFD700;'>📊 Candlestick Chart & Market Depth</div>", unsafe_allow_html=True)

    # Candlestick Chart
    if not candles_df.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=candles_df['time'],
            open=candles_df['open'],
            high=candles_df['high'],
            low=candles_df['low'],
            close=candles_df['close'],
            increasing_line_color='lime',
            decreasing_line_color='red'
        )])
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Gathering data for candlestick chart...")

    # Market Depth
    st.subheader("📉 Market Depth")
    depth_fig = go.Figure()
    depth_fig.add_trace(go.Bar(x=['Bid'], y=[bid_size], name='Bid', marker=dict(color='green')))
    depth_fig.add_trace(go.Bar(x=['Ask'], y=[ask_size], name='Ask', marker=dict(color='red')))
    depth_fig.update_layout(template="plotly_dark", height=250)
    st.plotly_chart(depth_fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
