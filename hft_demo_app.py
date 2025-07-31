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

# ---------- Mock Price Feed ----------
def get_live_price():
    base_price = 30000
    return base_price + random.uniform(-200, 200)

# ---------- Mock Ticker ----------
assets = {
    "BTC/USD": 30000 + random.uniform(-150, 150),
    "ETH/USD": 2000 + random.uniform(-20, 20),
    "AAPL": 180 + random.uniform(-2, 2),
    "TSLA": 250 + random.uniform(-3, 3),
    "AMZN": 135 + random.uniform(-1, 1)
}

# ---------- AI Signal ----------
def ai_market_signal():
    if len(st.session_state.price_data) < 10:
        return "HOLD", "Collecting more data for better prediction."
    prices = [p[1] for p in st.session_state.price_data[-10:]]
    volumes = [p[2] for p in st.session_state.price_data[-10:]]
    trend = (prices[-1] - prices[0]) / prices[0]
    avg_volume = sum(volumes) / len(volumes)
    current_volume = volumes[-1]
    if trend > 0.002:
        reason = "Price trend bullish with strong momentum."
        if current_volume > avg_volume:
            reason += " Volume above average, strong buying."
        return "BUY", reason
    elif trend < -0.002:
        reason = "Downward trend detected."
        if current_volume > avg_volume:
            reason += " High volume selling pressure."
        return "SELL", reason
    else:
        return "HOLD", "Market neutral. No strong movement."

# ---------- Ticker Bar ----------
ticker_html = "<div class='ticker-container'><div class='ticker-text'>"
for asset, price in assets.items():
    change = random.uniform(-1.5, 1.5)
    color_class = "price-up" if change >= 0 else "price-down"
    ticker_html += f"&nbsp;&nbsp;{asset}: <span class='{color_class}'>{price:.2f}</span> ({change:+.2f}%)&nbsp;&nbsp;|"
ticker_html += "</div></div>"
st.markdown(ticker_html, unsafe_allow_html=True)

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
    st.markdown(f"<div style='font-size:18px;line-height:1.6;'>{ai_text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Main Panel ----------
with middle:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>⚡ High Frequency Trading Dashboard</div>", unsafe_allow_html=True)

    # Update Price Data
    price = get_live_price()
    st.session_state.price_data.append((time.strftime('%H:%M:%S'), price, random.randint(10, 100)))
    df = pd.DataFrame(st.session_state.price_data, columns=['time', 'price', 'volume'])

    # Price & Volume Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['price'], mode='lines+markers', name='Price', line=dict(color='lime')))
    fig.add_trace(go.Bar(x=df['time'], y=df['volume'], name='Volume', yaxis='y2', marker=dict(color='blue')))
    fig.update_layout(template="plotly_dark", xaxis=dict(title="Time"),
                      yaxis=dict(title="Price"), yaxis2=dict(title="Volume", overlaying="y", side="right"), height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Trade Log
    st.subheader("📜 Trade Log")
    if st.session_state.trade_log:
        st.dataframe(pd.DataFrame(st.session_state.trade_log))
    else:
        st.info("No trades yet.")

    # ---------- Realized PnL ----------
    pnl = []
    cum_pnl = 0
    open_positions = []
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

    # ---------- Unrealized PnL ----------
    current_unrealized = 0
    if st.session_state.positions:
        for pos in st.session_state.positions:
            current_unrealized += (price - pos["price"]) * pos["qty"]
    st.session_state.unrealized_history.append(current_unrealized)
    st.session_state.unrealized_time.append(time.strftime('%H:%M:%S'))

    # Alert color
    unrealized_color = "#39ff14" if current_unrealized >= 0 else "#ff073a"
    st.markdown(f"""
        <div style='text-align:center;font-size:22px;font-weight:bold;margin:10px;
        padding:10px;border-radius:8px;background:#111;border:2px solid {unrealized_color};
        box-shadow:0 0 15px {unrealized_color};color:{unrealized_color};'>
        Unrealized PnL: {current_unrealized:.2f} USD
        </div>
    """, unsafe_allow_html=True)

    unrealized_fig = go.Figure()
    unrealized_fig.add_trace(go.Scatter(x=st.session_state.unrealized_time,
                                        y=st.session_state.unrealized_history,
                                        mode='lines+markers', name='Unrealized PnL',
                                        line=dict(color='magenta')))
    unrealized_fig.update_layout(template="plotly_dark", title="📊 Unrealized PnL (Open Positions)", height=300)
    st.plotly_chart(unrealized_fig, use_container_width=True)

    # ---------- Cumulative PnL (Last 5 Hours) ----------
    now = datetime.now()
    five_hours_ago = now - timedelta(hours=5)
    trade_times, cumulative_pnl, cum_pnl_5h = [], [], 0
    open_positions_5h = []
    for trade in st.session_state.trade_log:
        trade_time = datetime.strptime(trade["time"], "%H:%M:%S")
        trade_time = datetime.combine(now.date(), trade_time.time())
        if trade_time >= five_hours_ago:
            if trade["side"] == "BUY":
                open_positions_5h.append((trade["qty"], trade["price"]))
                cum_pnl_5h -= trade["qty"] * trade["price"]
            else:
                if open_positions_5h:
                    qty_to_sell = trade["qty"]
                    while qty_to_sell > 0 and open_positions_5h:
                        qty_open, price_open = open_positions_5h[0]
                        if qty_open <= qty_to_sell:
                            cum_pnl_5h += qty_open * trade["price"]
                            qty_to_sell -= qty_open
                            open_positions_5h.pop(0)
                        else:
                            cum_pnl_5h += qty_to_sell * trade["price"]
                            open_positions_5h[0] = (qty_open - qty_to_sell, price_open)
                            qty_to_sell = 0
            trade_times.append(trade_time)
            cumulative_pnl.append(cum_pnl_5h)

    if trade_times:
        cum_pnl_fig = go.Figure()
        cum_pnl_fig.add_trace(go.Scatter(x=trade_times, y=cumulative_pnl,
                                         mode='lines+markers', name='Cumulative PnL',
                                         line=dict(color='orange')))
        cum_pnl_fig.update_layout(template="plotly_dark", title="💰 Cumulative Profit (Last 5 Hours)",
                                   xaxis_title="Time", yaxis_title="PnL (USD)", height=300)
        st.plotly_chart(cum_pnl_fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Trading Panel ----------
with right:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>🛠 Trading Panel</div>", unsafe_allow_html=True)
    mode = st.radio("Mode", ["Simulation", "Live"])
    side = st.radio("Side", ["BUY", "SELL"])
    qty = st.number_input("Quantity", min_value=1.0, step=1.0, value=1.0)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    limit_price = st.number_input("Limit Price", value=30000.0, step=0.01)

    if st.button("Submit Order"):
        trade_price = price if order_type == "MARKET" else limit_price
        st.session_state.trade_log.append({"time": time.strftime('%H:%M:%S'), "side": side, "qty": qty, "price": trade_price})
        if side == "BUY":
            st.session_state.positions.append({"qty": qty, "price": trade_price})
        else:
            if st.session_state.positions:
                st.session_state.positions.pop(0)
        st.success(f"Order placed: {side} {qty} @ {trade_price}")

    st.markdown("</div>", unsafe_allow_html=True)
