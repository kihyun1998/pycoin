import plotly.graph_objects as go
import yfinance as yf
from math_extention.math_extention import perfectRound
from heikin_ashi import heikin_ashi
from plotly.subplots import make_subplots
from rsi import cal_rsi, stochastic_rsi
import pandas as pd



symbol = "BTC-USD"
df = yf.download(tickers=symbol, period="5d", interval="15m")

"""
Heikin Ashi
"""
ha_df = heikin_ashi(df)
print(ha_df)


"""
EMA 200
"""
# EMA 200 line by minute 
ema200 = df['Close'].ewm(span=200,adjust=False).mean()


"""
Stoch RSI
"""
ha_df['RSI'] = cal_rsi(df)
ha_df['K'],ha_df['D'] = stochastic_rsi(ha_df['RSI'])

"""
Ploting
"""

# Creating figure with subplots
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, subplot_titles=('BTC-USD with 200-Minute EMA', 'Stochastic RSI'),row_heights=[0.7,0.3])

# Plot Heikin Ashi
fig.add_trace(go.Candlestick(x=ha_df.index, open=ha_df['Open'], high=ha_df['High'], low=ha_df['Low'], close=ha_df['Close'], name='Heikin Ashi'), row=1, col=1)

# Plot 200-minute EMA
fig.add_trace(
    go.Scatter(
        x=df.index, 
        y=ema200, mode='lines', 
        name='200-Minute EMA', 
        line=dict(color='purple', width=2)
    ), 
    row=1, col=1
)

# Plot StochRSI D line
fig.add_trace(
    go.Scatter(
        x=df.index, 
        y=ha_df['D'], 
        mode='lines', 
        name='StochRSI D', 
        line=dict(color='orange', width=1.5)
    ), 
    row=2, col=1
)

# Plot StochRSI K line
fig.add_trace(
    go.Scatter(
        x=df.index, 
        y=ha_df['K'], 
        mode='lines', 
        name='StochRSI K', 
        line=dict(color='blue', width=1.5)
    ), 
    row=2, col=1
)

# Add horizontal line at y=80 for overbought level
fig.add_trace(
    go.Scatter(
        x=df.index, 
        y=[80]*len(df.index), 
        mode='lines', 
        name='Overbought', 
        line=dict(color='grey', dash='dash')
    ), 
    row=2, col=1
)

# Add horizontal line at y=20 for oversold level
fig.add_trace(
    go.Scatter(
        x=df.index, 
        y=[20]*len(df.index), 
        mode='lines', 
        name='Oversold', 
        line=dict(color='grey', dash='dash')
        ), 
    row=2, col=1
)

# Update layout
fig.update_layout(xaxis_rangeslider_visible=False)
fig.update_layout(height=700, title_text="BTC-USD Analysis with Heikin Ashi, 200-Minute EMA, and Stochastic RSI")
fig.update_xaxes(title_text="Time", row=2, col=1)
fig.update_yaxes(title_text="Price", row=1, col=1)
fig.update_yaxes(title_text="StochRSI Value", row=2, col=1)
fig.update_yaxes(range=[0,100],row=2,col=1)

# Show plot
fig.show()