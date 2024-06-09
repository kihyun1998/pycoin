import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from heikin_ashi import heikin_ashi
from math_extention.math_extention import perfectRound
from plotly.subplots import make_subplots
from rsi import cal_rsi, stochastic_rsi

# This file is about studying buying timing tracking.

# Download BTC-USD data for the last 5 days with 15-minute intervals
symbol = "ETH-USD"
df = yf.download(tickers=symbol, period="30d", interval="1h")

# Heikin Ashi calculation
ha_df = heikin_ashi(df)

# EMA 200 calculation
ema200 = df['Close'].ewm(span=200, adjust=False).mean()

# Stochastic RSI calculation
ha_df['RSI'] = cal_rsi(df)
ha_df['K'], ha_df['D'] = stochastic_rsi(ha_df['RSI'])

# Create a new column to indicate where %K crosses above %D and should continue to be True until %D crosses above %K
ha_df['k_above_d'] = (ha_df['K'].shift(1) < ha_df['D'].shift(1)) & (ha_df['K'] > ha_df['D'])

# Initialize the extended k_above_d signal
extended_k_above_d = ha_df['k_above_d'].copy()
extended_k_above_d.iloc[0] = ha_df['k_above_d'].iloc[0]  # Initialize first value

for i in range(1, len(ha_df)):
    if extended_k_above_d.iloc[i - 1]:  # If previous signal was True
        if ha_df['D'].iloc[i] > ha_df['K'].iloc[i]:
            extended_k_above_d.iloc[i] = False
        else:
            extended_k_above_d.iloc[i] = True
    elif ha_df['k_above_d'].iloc[i]:  # Reset to True if new k_above_d signal is True
        extended_k_above_d.iloc[i] = True

ha_df['extended_k_above_d'] = extended_k_above_d

# Calculate initial Buy signals, including extended_k_above_d
init_buy_signal = (ha_df['Close'] > ema200) & (ha_df['K'] < 20) & (ha_df['D'] < 20) & (ha_df['extended_k_above_d'])

# Create extended buy signal column with condition to reset to False
buy_signal = init_buy_signal.copy()
buy_signal.iloc[0] = init_buy_signal.iloc[0]  # Initialize first value

for i in range(1, len(init_buy_signal)):
    if buy_signal.iloc[i - 1]:  # If previous signal was True
        if (ha_df['K'].iloc[i] >= 80) or (ha_df['Close'].iloc[i] < ema200.iloc[i]) or (ha_df['K'].iloc[i] < ha_df['D'].iloc[i]):
            buy_signal.iloc[i] = False
        else:
            buy_signal.iloc[i] = True
    elif init_buy_signal.iloc[i]:  # Reset to True if new buy signal is True
        buy_signal.iloc[i] = True

ha_df['buy_signal'] = buy_signal

# Calculate actual buy signals when %K crosses above 20 while buy_signal is True
actual_buy_signal = buy_signal & (ha_df['K'] > 20)
ha_df['actual_buy_signal'] = actual_buy_signal

# Debugging output
print("Condition 1 (Close > EMA200):\n", ha_df['Close'] > ema200)
print("Condition 2 (K < 20):\n", ha_df['K'] < 20)
print("Condition 3 (D < 20):\n", ha_df['D'] < 20)
print("K above D condition:\n", ha_df['k_above_d'])
print("Extended K above D Signal:\n", ha_df['extended_k_above_d'])
print("Combined Condition (Initial Buy Signal):\n", init_buy_signal)
print("Extended Buy Signal:\n", ha_df['buy_signal'])
print("Actual Buy Signal:\n", ha_df['actual_buy_signal'])

# Create figure with subplots
fig = make_subplots(
    rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02,
    subplot_titles=('BTC-USD with 200-Minute EMA and Buy Signals', 'Stochastic RSI'), row_heights=[0.7, 0.3]
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

# Plot extended Buy signals
fig.add_trace(
    go.Scatter(
        x=ha_df.index[ha_df['buy_signal']], y=ha_df['Close'][ha_df['buy_signal']],
        mode='markers', name='Extended Buy Signal',
        marker=dict(color='green', size=10, symbol='triangle-up')
    ), row=1, col=1
)

# Plot actual Buy signals (%K crosses above 20 while extended_buy_signal is True)
fig.add_trace(
    go.Scatter(
        x=ha_df.index[ha_df['actual_buy_signal']], y=ha_df['Close'][ha_df['actual_buy_signal']],
        mode='markers', name='Actual Buy Signal',
        marker=dict(color='mediumturquoise', size=10, symbol='triangle-up')
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
    title_text="BTC-USD Analysis with Heikin Ashi, 200-Minute EMA, and Stochastic RSI",
    hovermode='x unified'  # Enable unified hover mode
)
fig.update_xaxes(title_text="Time", row=2, col=1)
fig.update_yaxes(title_text="Price", row=1, col=1)
fig.update_yaxes(title_text="StochRSI Value", row=2, col=1, range=[0, 100])

# Show plot
fig.show()
