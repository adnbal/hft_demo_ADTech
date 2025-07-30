import streamlit as st
import pandas as pd
import numpy as np
import requests
import websocket
import threading
import json
import time
import plotly.express as px

# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(page_title="HFT Prototype Demo", layout="wide")
st.title("⚡ High-Frequency Trading Prototype (Binance Testnet)")

# -------------------------------
# Globals for Live Data
# -------------------------------
price_data = []
trade_log = []

# -------------------------------
# Binance Testnet WebSocket URL
# -------------------------------
BINANCE_TESTNET_WS = "wss://testnet.binance.vision/ws/btcusdt@trade"

# -------------------------------
# Market Making Strategy
# -------------------------------
def market_maker_strategy(current_price):
    """
    Basic strategy:
    - Buy 0.001 BTC if price dips slightly
    - Sell 0.001 BTC if price rises slightly
    """
    qty = 0.001
    bid_price = current_price * 0.999  # Slightly below market
    ask_price = current_price * 1.001  # Slightly above market

    # Simulate execution
    buy_executed = np.random.choice([True, False], p=[0.3, 0.7])
    sell_executed = np.random.choice([True, False], p=[0.3, 0.7])

    trade_details = []
    if buy_executed:
        trade_details.append({"type": "BUY", "price": round(bid_price, 2), "qty": qty})
    if sell_executed:
        trade_details.append({"type": "SELL", "price": round(ask_price, 2), "qty": qty})

    return trade_details

# -------------------------------
# WebSocket Listener
# -------------------------------
def on_message(ws, message):
    global price_data, trade_log
    msg = json.loads(message)
    price = float(msg['p'])
    timestamp = pd.Timestamp.now()

    price_data.append({"time": timestamp, "price": price})

    # Run strategy
    trades = market_maker_strategy(price)
    for t in trades:
        trade_log.append({"time": timestamp, **t})

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_close(ws):
    print("WebSocket Closed")

def on_open(ws):
    print("Connected to Binance Testnet WebSocket")

# -------------------------------
# Start WebSocket in a thread
# -------------------------------
def start_socket():
    ws = websocket.WebSocketApp(BINANCE_TESTNET_WS,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

threading.Thread(target=start_socket, daemon=True).start()

# -------------------------------
# Streamlit Live Dashboard
# -------------------------------
st.sidebar.header("⚙️ Settings")
refresh_rate = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 2)

st.subheader("📈 Live Price Feed (BTC/USDT)")
chart_placeholder = st.empty()
log_placeholder = st.empty()

while True:
    if len(price_data) > 5:
        df_price = pd.DataFrame(price_data[-100:])  # last 100 points
        fig = px.line(df_price, x="time", y="price", title="Live BTC/USDT Price")
        chart_placeholder.plotly_chart(fig, use_container_width=True)

    if len(trade_log) > 0:
        df_trades = pd.DataFrame(trade_log[-20:])  # last 20 trades
        # Calculate P&L (rough simulation)
        buy_sum = df_trades[df_trades["type"] == "BUY"]["price"].sum()
        sell_sum = df_trades[df_trades["type"] == "SELL"]["price"].sum()
        pnl = (sell_sum - buy_sum) * 0.001  # Qty fixed at 0.001
        log_placeholder.subheader(f"💰 Simulated P&L: {pnl:.2f} USDT")
        st.dataframe(df_trades)

    time.sleep(refresh_rate)
