import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

# MACD calculation function
def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    df['EMA12'] = df['Close'].ewm(span=short_window, adjust=False).mean()
    df['EMA26'] = df['Close'].ewm(span=long_window, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['Signal Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
    df['MACD Histogram'] = df['MACD'] - df['Signal Line']
    return df

# Download BTC-USD data for the last 5 days with 15-minute intervals
symbol = "BTC-USD"
df = yf.download(tickers=symbol, period="5d", interval="15m")

# Calculate MACD and Signal Line
df = calculate_macd(df)

# Calculate 200-period EMA
df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

# Create subplots with shared x-axis
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    subplot_titles=('Candlestick Chart', 'MACD'), 
                    vertical_spacing=0.15)  # Adjust vertical spacing to reduce subplot size

# Add candlestick chart to the first subplot with reduced wick thickness
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name='Candlestick',
    increasing=dict(line=dict(width=0.5)),
    decreasing=dict(line=dict(width=0.5))
), row=1, col=1)

# Add EMA200 line to the first subplot
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['EMA200'],
    line=dict(color='purple', width=1),
    name='EMA 200'
), row=1, col=1)

# Add MACD line to the second subplot
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['MACD'],
    line=dict(color='blue', width=1),
    name='MACD'
), row=2, col=1)

# Add Signal line to the second subplot
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['Signal Line'],
    line=dict(color='red', width=1),
    name='Signal Line'
), row=2, col=1)

# Add MACD histogram to the second subplot with pseudo-3D effect
colors = ['red' if val < 0 else 'green' for val in df['MACD Histogram']]
fig.add_trace(go.Bar(
    x=df.index,
    y=df['MACD Histogram'],
    name='MACD Histogram',
    marker=dict(
        color=colors,
        line=dict(color='black', width=0.5),
        opacity=0.6
    )
), row=2, col=1)

# Update layout
fig.update_layout(
    title=f'{symbol} Candlestick Chart with MACD',
    xaxis_title='Date',
    yaxis_title='Price',
    xaxis2_title='Date',
    yaxis2_title='MACD',
    xaxis_rangeslider_visible=False
)

# Show the plot
fig.show()
