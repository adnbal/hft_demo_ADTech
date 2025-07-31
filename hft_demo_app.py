import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import random

st.set_page_config(layout="wide")

# --------- Custom CSS for Layout & Neon ---------
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: white;
        }
        .neon {
            font-size: 22px;
            font-weight: bold;
            color: white;
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            border: 2px solid white;
            background-color: #111;
            box-shadow: 0 0 10px #39ff14, 0 0 20px #39ff14;
            animation: flicker 1.5s infinite alternate;
        }
        @keyframes flicker {
            0% { text-shadow: 0 0 5px #39ff14, 0 0 10px #39ff14; }
            100% { text-shadow: 0 0 20px #39ff14, 0 0 40px #39ff14; }
        }
        .panel {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 15px;
            border: 2px solid white;
            height: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# -------- Session State --------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []

# -------- Mock Price Generator --------
def get_live_price():
    base_price = 30000
    return base_price + random.uniform(-200, 200)

# -------- AI Market Signal --------
def ai_market_signal():
    if len(st.session_state.price_data) < 10:
        return "HOLD", "Collecting more data for better prediction."
    prices = [p[1] for p in st.session_state.price_data[-10:]]
    trend = (prices[-1] - prices[0]) / prices[0]
    if trend > 0.002:
        return "BUY", f"Market Signal: BUY Price trend is upward, strong bullish momentum. Expect +0.8% rise in short term."
    elif trend < -0.002:
        return "SELL", f"Market Signal: SELL Price trend is downward, bearish momentum. Expect -0.8% fall soon."
    else:
        return "HOLD", "Market is neutral. Wait for a clear trend."

# -------- Layout --------
left, middle, right = st.columns([1.5, 3, 1.5])

# -------- AI PANEL --------
with left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>🤖 AI Market Intelligence</div>", unsafe_allow_html=True)

    ai_signal, ai_text = ai_market_signal()
    indicator_color = "#39ff14" if ai_signal == "BUY" else "#ff073a" if ai_signal == "SELL" else "#ffff00"

    # BUY/SELL Indicator
    st.markdown(f"""
        <div style='
            text-align:center;
            font-size:24px;
            font-weight:bold;
            color:white;
            background-color:{indicator_color};
            border-radius:10px;
            padding:12px;
            margin-bottom:15px;
            box-shadow:0 0 20px {indicator_color}, 0 0 40px {indicator_color};
        '>{ai_signal}</div>
    """, unsafe_allow_html=True)

    # AI Commentary
    st.markdown(f"<div style='font-size:18px; line-height:1.6; color:white;'>{ai_text}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------- MAIN PANEL (Charts & PnL) --------
with middle:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>⚡ High Frequency Trading Dashboard</div>", unsafe_allow_html=True)

    # Update Price Data
    price = get_live_price()
    st.session_state.price_data.append((time.strftime('%H:%M:%S'), price, random.randint(10, 100)))
    df = pd.DataFrame(st.session_state.price_data, columns=['time', 'price', 'volume'])

    # Price + Volume Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['time'], y=df['price'], mode='lines+markers', name='Price', line=dict(color='lime')))
    fig.add_trace(go.Bar(x=df['time'], y=df['volume'], name='Volume', yaxis='y2', marker=dict(color='blue')))
    fig.update_layout(
        template="plotly_dark",
        xaxis=dict(title="Time"),
        yaxis=dict(title="Price (USD)"),
        yaxis2=dict(title="Volume", overlaying="y", side="right"),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Trade Log
    st.subheader("📜 Trade Log")
    if st.session_state.trade_log:
        st.dataframe(pd.DataFrame(st.session_state.trade_log))
    else:
        st.write("No trades yet.")

    # P&L Chart (line chart for cumulative P&L)
    pnl = [sum(random.uniform(-50, 50) for _ in range(i)) for i in range(len(df))]
    pnl_fig = go.Figure()
    pnl_fig.add_trace(go.Scatter(x=df['time'], y=pnl, mode='lines', name='P&L', line=dict(color='cyan')))
    pnl_fig.update_layout(template="plotly_dark", title="📊 Realized & Unrealized P&L", height=300)
    st.plotly_chart(pnl_fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -------- TRADING PANEL --------
with right:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='neon'>🛠 Trading Panel</div>", unsafe_allow_html=True)

    mode = st.radio("Mode", ["Simulation", "Live"])
    side = st.radio("Side", ["BUY", "SELL"])
    qty = st.number_input("Quantity", min_value=1.0, step=1.0, value=1.0)
    order_type = st.radio("Order Type", ["MARKET", "LIMIT"])
    limit_price = st.number_input("Limit Price", value=30000.0, step=0.01)

    if st.button("Submit Order"):
        st.session_state.trade_log.append({"time": time.strftime('%Y-%m-%d %H:%M:%S'), "side": side, "qty": qty, "price": price})
        if side == "BUY":
            st.session_state.positions.append({"qty": qty, "price": price})
        else:
            if st.session_state.positions:
                st.session_state.positions.pop(0)

    st.markdown("</div>", unsafe_allow_html=True)

# Auto-refresh every 5 sec
time.sleep(5)
st.experimental_rerun()
