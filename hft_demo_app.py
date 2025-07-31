import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ---------- Page Config ----------
st.set_page_config(page_title="AI-Powered High-Frequency Trading", layout="wide")

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

if "selected_side" not in st.session_state:
    st.session_state.selected_side = "BUY"
if "limit_price" not in st.session_state:
    st.session_state.limit_price = 30000.0

# ---------- Mock Price ----------
def get_live_price():
    base_price = 30000
    return base_price + random.uniform(-200, 200)

# ---------- Market Ticker ----------
assets = {"BTC/USD": 30000 + random.uniform(-150, 150), "ETH/USD": 2000 + random.uniform(-20, 20)}
ticker_html = "<div class='ticker-container'><div class='ticker-text'>"
for asset, price_val in assets.items():
    change = random.uniform(-1.5, 1.5)
    color_class = "price-up" if change >= 0 else "price-down"
    ticker_html += f"&nbsp;&nbsp;{asset}: <span class='{color_class}'>{price_val:.2f}</span> ({change:+.2f}%)&nbsp;&nbsp;|"
ticker_html += "</div></div>"
st.markdown(ticker_html, unsafe_allow_html=True)

# ---------- AI Signal ----------
def ai_market_signal():
    if len(st.session_state.price_data) < 10:
        return "HOLD", "Collecting data for prediction.", None, 50, {}
    prices = [p[1] for p in st.session_state.price_data[-10:]]
    volumes = [p[2] for p in st.session_state.price_data[-10:]]
    trend = (prices[-1] - prices[0]) / prices[0]
    avg_volume = sum(volumes) / len(volumes)
    current_volume = volumes[-1]
    current_price = prices[-1]
    trend_strength = abs(trend)
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
    confidence = min(100, int((trend_strength * 5000) + (volume_ratio * 20)))
    forecast_price = current_price
    change_pct = 0
    if trend > 0.002:
        forecast_price = current_price * (1 + trend_strength)
        change_pct = ((forecast_price - current_price) / current_price) * 100
        reason = f"Price trend bullish. Target: ${forecast_price:.2f} ({change_pct:+.2f}%)."
        metrics = {"Trend Strength": f"{trend_strength*100:.2f}%", "Volume Ratio": f"{volume_ratio:.2f}", "Forecast Change": f"{change_pct:+.2f}%"}
        return "BUY", reason, forecast_price, confidence, metrics
    elif trend < -0.002:
        forecast_price = current_price * (1 - trend_strength)
        change_pct = ((forecast_price - current_price) / current_price) * 100
        reason = f"Downtrend detected. Target: ${forecast_price:.2f} ({change_pct:+.2f}%)."
        metrics = {"Trend Strength": f"{trend_strength*100:.2f}%", "Volume Ratio": f"{volume_ratio:.2f}", "Forecast Change": f"{change_pct:+.2f}%"}
        return "SELL", reason, forecast_price, confidence, metrics
    else:
        metrics = {"Trend Strength": f"{trend_strength*100:.2f}%", "Volume Ratio": f"{volume_ratio:.2f}", "Forecast Change": "0.00%"}
        return "HOLD", "Market neutral. No strong movement.", current_price, confidence, metrics

# ---------- Update Price Data ----------
price = get_live_price()
st.session_state.price_data.append((time.strftime('%H:%M:%S'), price, random.randint(10, 100)))
df = pd.DataFrame(st.session_state.price_data, columns=['time', 'price', 'volume'])

# Create Candlestick OHLC
candles = []
for i in range(0, len(df), 3):
    subset = df.iloc[i:i+3]
    if len(subset) >= 3:
        candles.append({"time": subset["time"].iloc[-1], "open": subset["price"].iloc[0],
                        "high": subset["price"].max(), "low": subset["price"].min(),
                        "close": subset["price"].iloc[-1]})
candles_df = pd.DataFrame(candles)

# AI Decision
ai_signal, ai_text, forecast_price, confidence, metrics = ai_market_signal()
if ai_signal != "HOLD" and forecast_price:
    st.session_state.selected_side = ai_signal
    st.session_state.limit_price = round(forecast_price, 2)

# ---------- Layout ----------
left, middle, right = st.columns([1.5, 3, 1.5])

# ---------- AI Panel ----------
with left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:22px;text-align:center;padding:12px;border:2px solid #00FFFF;'>🤖 AI Market Intelligence</div>", unsafe_allow_html=True)

    color = "#39ff14" if ai_signal == "BUY" else "#ff073a" if ai_signal == "SELL" else "#ffff00"
    st.markdown(f"<div style='text-align:center;font-size:28px;color:{color};'>{ai_signal}</div>", unsafe_allow_html=True)
    st.write(f"**AI Suggestion:** {ai_text}")

    # Confidence Gauge
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number", value=confidence,
        title={'text': "Confidence Level"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "green" if confidence > 70 else "yellow" if confidence > 50 else "red"}}
    ))
    gauge_fig.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10), template="plotly_dark")
    st.plotly_chart(gauge_fig, use_container_width=True)

    st.write("### Key Metrics")
    for k, v in metrics.items():
        st.write(f"- {k}: {v}")

    # Collapsible Full Analysis
    with st.expander("📊 Show Full AI Market Analysis"):
        st.markdown("### AI Market Analysis")
        st.write(f"**Signal:** {ai_signal}")
        st.write(f"**Confidence:** {confidence}%")
        st.write(f"**Reasoning:** {ai_text}")
        st.write("**Detailed Breakdown:**")
        st.write(f"- Trend Strength: {metrics.get('Trend Strength', 'N/A')}")
        st.write(f"- Volume Ratio: {metrics.get('Volume Ratio', 'N/A')}")
        st.write(f"- Forecast Change: {metrics.get('Forecast Change', 'N/A')}")
        st.write("**AI Strategy Suggestion:** Enter position as per signal. Monitor volatility. Risk: Trend reversal possible.")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Middle Panel ----------
with middle:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("### 📊 Market Visualization & PnL")

    # Candlestick Chart
    if not candles_df.empty:
        candle_fig = go.Figure(data=[go.Candlestick(
            x=candles_df['time'], open=candles_df['open'], high=candles_df['high'],
            low=candles_df['low'], close=candles_df['close'],
            increasing_line_color='lime', decreasing_line_color='red')])
        candle_fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(candle_fig, use_container_width=True)

    # Market Depth
    bid_size, ask_size = random.randint(50, 200), random.randint(50, 200)
    depth_fig = go.Figure()
    depth_fig.add_trace(go.Bar(x=['Bid'], y=[bid_size], name='Bid', marker=dict(color='green')))
    depth_fig.add_trace(go.Bar(x=['Ask'], y=[ask_size], name='Ask', marker=dict(color='red')))
    depth_fig.update_layout(template="plotly_dark", height=250, title="Market Depth")
    st.plotly_chart(depth_fig, use_container_width=True)

# ---------- Trading Panel ----------
with right:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("### 🛠 Trading Panel")
    mode = st.radio("Mode", ["Simulation", "Live"])
    side = st.radio("Side", ["BUY", "SELL"], index=0 if st.session_state.selected_side == "BUY" else 1)
    qty = st.number_input("Quantity", min_value=1.0, step=1.0, value=1.0)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    limit_price = st.number_input("Limit Price (USD)", value=st.session_state.limit_price, step=0.01)

    if st.button("Submit Order"):
        trade_price = price if order_type == "MARKET" else limit_price
        st.session_state.trade_log.append({"time": time.strftime('%H:%M:%S'), "side": side, "qty": qty, "price": trade_price})
        st.success(f"Order placed: {side} {qty} @ {trade_price}")

    if ai_signal != "HOLD" and forecast_price:
        if st.button("🤖 Take AI Advice"):
            st.session_state.trade_log.append({"time": time.strftime('%H:%M:%S'), "side": ai_signal, "qty": qty, "price": round(forecast_price, 2)})
            st.success(f"✅ Executed AI Advice: {ai_signal} {qty} @ ${forecast_price:.2f}")
