import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from heikin_ashi import heikin_ashi
from math_extention.math_extention import perfectRound
from plotly.subplots import make_subplots
from rsi import cal_rsi, stochastic_rsi

# Download BTC-USD data for the last 5 days with 15-minute intervals
symbol = "BTC-USD"
df = yf.download(tickers=symbol, period="5d", interval="15m")

# Heikin Ashi calculation
ha_df = heikin_ashi(df)

# EMA 200 calculation
ema200 = df['Close'].ewm(span=200, adjust=False).mean()

# Stochastic RSI calculation
ha_df['RSI'] = cal_rsi(df)
ha_df['K'], ha_df['D'] = stochastic_rsi(ha_df['RSI'])

# Create figure with subplots
fig = make_subplots(
    rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02,
    subplot_titles=('BTC-USD with 200-Minute EMA', 'Stochastic RSI'), row_heights=[0.7, 0.3]
)

# Plot Heikin Ashi candlestick chart
fig.add_trace(
    go.Candlestick(
        x=ha_df.index, open=ha_df['Open'], high=ha_df['High'],
        low=ha_df['Low'], close=ha_df['Close'], name='Heikin Ashi'
    ), row=1, col=1
)

# Plot 200-minute EMA
fig.add_trace(
    go.Scatter(
        x=df.index, y=ema200, mode='lines',
        name='200-Minute EMA', line=dict(color='purple', width=2)
    ), row=1, col=1
)

# Plot Stochastic RSI %K line
fig.add_trace(
    go.Scatter(
        x=df.index, y=ha_df['K'], mode='lines',
        name='StochRSI %K', line=dict(color='blue', width=1.5)
    ), row=2, col=1
)

# Plot Stochastic RSI %D line
fig.add_trace(
    go.Scatter(
        x=df.index, y=ha_df['D'], mode='lines',
        name='StochRSI %D', line=dict(color='orange', width=1.5)
    ), row=2, col=1
)

# Add horizontal lines for overbought (80) and oversold (20) levels
fig.add_trace(
    go.Scatter(
        x=df.index, y=[80] * len(df.index), mode='lines',
        name='Overbought', line=dict(color='grey', dash='dash')
    ), row=2, col=1
)
fig.add_trace(
    go.Scatter(
        x=df.index, y=[20] * len(df.index), mode='lines',
        name='Oversold', line=dict(color='grey', dash='dash')
    ), row=2, col=1
)

# Update layout and axes
fig.update_layout(
    xaxis_rangeslider_visible=False,
    height=700,
    title_text="BTC-USD Analysis with Heikin Ashi, 200-Minute EMA, and Stochastic RSI"
)
fig.update_xaxes(title_text="Time", row=2, col=1)
fig.update_yaxes(title_text="Price", row=1, col=1)
fig.update_yaxes(title_text="StochRSI Value", row=2, col=1, range=[0, 100])

# Show plot
fig.show()
