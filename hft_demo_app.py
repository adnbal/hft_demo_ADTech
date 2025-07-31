import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import datetime
import time

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="HFT AI Dashboard", layout="wide")

# -------------------- CUSTOM CSS --------------------
st.markdown("""
    <style>
    .fixed-ai-panel {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: #0e1117;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 10px;
        border: 2px solid #39FF14;
        box-shadow: 0px 0px 20px #39FF14;
    }
    .buy-signal {
        color: #39FF14;
        font-size: 20px;
        font-weight: bold;
        text-shadow: 0 0 10px #39FF14;
    }
    .sell-signal {
        color: #FF3131;
        font-size: 20px;
        font-weight: bold;
        text-shadow: 0 0 10px #FF3131;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
if "price_data" not in st.session_state:
    st.session_state.price_data = []
if "trade_log" not in st.session_state:
    st.session_state.trade_log = []
if "positions" not in st.session_state:
    st.session_state.positions = []

# Simulate live price update
price = 30000 + random.uniform(-100, 100)
volume = random.uniform(50, 200)
st.session_state.price_data.append({
    "time": datetime.now(),
    "price": price,
    "volume": volume
})

# -------------------- AI INTELLIGENCE --------------------
price_trend = "UP" if random.choice([True, False]) else "DOWN"
if price_trend == "UP":
    ai_signal = "BUY"
    ai_message = """
    <p class='buy-signal'>Market Signal: BUY ✅</p>
    Price trend is upward, indicating bullish momentum.<br>
    Buyers dominate order flow.<br>
    Forecast: Price expected to rise by ~0.8% in next few minutes.<br>
    Volatility within normal range, trend supported by strong volume.
    """
else:
    ai_signal = "SELL"
    ai_message = """
    <p class='sell-signal'>Market Signal: SELL ❌</p>
    Price trend is downward, indicating bearish momentum.<br>
    Sellers dominate order book.<br>
    Forecast: Price expected to drop by ~0.7% in next few minutes.<br>
    Caution: Short-term resistance levels breached.
    """

# -------------------- FIXED AI PANEL --------------------
st.markdown('<div class="fixed-ai-panel">', unsafe_allow_html=True)
st.markdown("### 🤖 AI Market Intelligence")
st.markdown(ai_message, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -------------------- DASHBOARD TITLE --------------------
st.title("⚡ High Frequency Trading AI Dashboard")
st.caption("Simulated BTC/USDT Trading with AI Insights")

# -------------------- PRICE & VOLUME CHART --------------------
st.subheader("📈 Live BTC Price & Volume")
df = pd.DataFrame(st.session_state.price_data)

if not df.empty:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Price line
    fig.add_trace(go.Scatter(
        x=df['time'], y=df['price'], mode='lines+markers',
        name='Price', line=dict(color='lime', width=3)
    ), secondary_y=False)

    # Volume bars
    fig.add_trace(go.Bar(
        x=df['time'], y=df['volume'], name='Volume',
        marker=dict(color='rgba(0,150,255,0.5)')
    ), secondary_y=True)

    fig.update_layout(
        template="plotly_dark", margin=dict(l=0, r=0, t=30, b=0),
        showlegend=True, height=400
    )
    fig.update_yaxes(title_text="BTC Price (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Volume", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

# -------------------- TRADING PANEL --------------------
st.subheader("🛠 Trading Panel")
col1, col2, col3, col4 = st.columns(4)
mode = col1.radio("Mode", ["Simulation", "Live"])
side = col2.radio("Side", ["BUY", "SELL"])
qty = col3.number_input("Quantity", min_value=1, value=5)
order_type = col4.radio("Order Type", ["MARKET", "LIMIT"])
limit_price = st.number_input("Limit Price", min_value=0.0, value=price)

if st.button("Submit Order"):
    trade_price = limit_price if order_type == "LIMIT" else price
    st.session_state.trade_log.append({
        "time": datetime.now(), "side": side, "qty": qty, "price": trade_price
    })
    if side == "BUY":
        st.session_state.positions.append({"price": trade_price, "qty": qty})
    elif side == "SELL" and st.session_state.positions:
        st.session_state.positions.pop(0)

# -------------------- TRADE LOG --------------------
st.subheader("📜 Trade Log")
df_trades = pd.DataFrame(st.session_state.trade_log)
st.dataframe(df_trades if not df_trades.empty else pd.DataFrame(columns=["No trades yet."]))

# -------------------- P&L CHART --------------------
st.subheader("📊 Realized & Unrealized P&L")
realized_pnl = 0.0
unrealized_pnl = 0.0
current_price = price
for pos in st.session_state.positions:
    unrealized_pnl += (current_price - pos["price"]) * pos["qty"]

pnl_df = pd.DataFrame({
    "Type": ["Realized", "Unrealized"],
    "Value": [realized_pnl, unrealized_pnl]
})

st.bar_chart(pnl_df.set_index("Type"))

# NEW P&L Trend Chart
if not df_trades.empty:
    df_trades['PnL'] = (df_trades['price'] - df_trades['price'].shift(1)).fillna(0).cumsum()
    st.line_chart(df_trades.set_index('time')['PnL'])

# -------------------- PORTFOLIO METRICS --------------------
st.subheader("📊 Portfolio Metrics")
open_position = sum([p["qty"] for p in st.session_state.positions])
avg_price = sum([p["price"] * p["qty"] for p in st.session_state.positions]) / open_position if open_position > 0 else 0
current_value = open_position * current_price
metrics_df = pd.DataFrame({
    "Metric": ["Open Position (BTC)", "Current Value (USD)", "Average Entry Price"],
    "Value": [open_position, f"${current_value:,.2f}", f"${avg_price:,.2f}"]
})
st.table(metrics_df)

# -------------------- AUTO REFRESH --------------------
st.caption("Refreshing every 5 seconds...")
st_autorefresh = st.experimental_singleton(lambda: None)
time.sleep(5)
st.experimental_rerun()
