import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 기술적 지표 import
from technical_indicators.ema200 import add_ema_to_dataframe
from technical_indicators.macd import add_macd_to_dataframe
from technical_indicators.parabolic_sar import add_parabolic_sar_to_dataframe

def get_bitcoin_data(start_date: datetime, end_date: datetime) -> pd.DataFrame:
    return yf.download('BTC-USD', start=start_date, end=end_date, interval='1h')
def add_trade_signals(data: pd.DataFrame) -> pd.DataFrame:
    data['LongSignal'] = False
    data['ShortSignal'] = False
    data['LongProfitSignal'] = False
    data['LongLossSignal'] = False
    data['ShortProfitSignal'] = False
    data['ShortLossSignal'] = False
    data['EntryPrice'] = np.nan
    data['ExitPrice'] = np.nan
    data['ProfitPercentage'] = np.nan
    
    in_long_position = False
    in_short_position = False
    entry_price = 0
    stop_loss = 0
    take_profit = 0
    
    for i in range(1, len(data)):
        # Long 조건
        long_condition1 = data['Close'].iloc[i] > data['EMA200'].iloc[i]
        long_condition2 = (data['MACD'].iloc[i] > data['Signal'].iloc[i] and 
                           data['MACD'].iloc[i-1] <= data['Signal'].iloc[i-1])
        long_condition3 = data['ParabolicSAR'].iloc[i] < data['Low'].iloc[i]
        
        # Short 조건
        short_condition1 = data['Close'].iloc[i] < data['EMA200'].iloc[i]
        short_condition2 = (data['MACD'].iloc[i] < data['Signal'].iloc[i] and 
                            data['MACD'].iloc[i-1] >= data['Signal'].iloc[i-1])
        short_condition3 = data['ParabolicSAR'].iloc[i] > data['High'].iloc[i]

        if in_long_position:
            if data['High'].iloc[i] >= take_profit:
                # Long 포지션 익절
                data.loc[data.index[i], 'LongProfitSignal'] = True
                data.loc[data.index[i], 'ExitPrice'] = take_profit
                data.loc[data.index[i], 'ProfitPercentage'] = (take_profit - entry_price) / entry_price * 100
                in_long_position = False
            elif data['Low'].iloc[i] <= stop_loss:
                # Long 포지션 손절
                data.loc[data.index[i], 'LongLossSignal'] = True
                data.loc[data.index[i], 'ExitPrice'] = stop_loss
                data.loc[data.index[i], 'ProfitPercentage'] = (stop_loss - entry_price) / entry_price * 100
                in_long_position = False
            elif short_condition1 and short_condition2 and short_condition3:
                # Long 포지션 청산 후 Short 진입
                data.loc[data.index[i], 'LongExitSignal'] = True
                data.loc[data.index[i], 'ExitPrice'] = data['Close'].iloc[i]
                data.loc[data.index[i], 'ProfitPercentage'] = (data['Close'].iloc[i] - entry_price) / entry_price * 100
                in_long_position = False
                
                # Short 진입
                data.loc[data.index[i], 'ShortSignal'] = True
                data.loc[data.index[i], 'EntryPrice'] = data['Close'].iloc[i]
                in_short_position = True
                entry_price = data['Close'].iloc[i]
                stop_loss = data['ParabolicSAR'].iloc[i]
                take_profit = entry_price - (stop_loss - entry_price)

        elif in_short_position:
            if data['Low'].iloc[i] <= take_profit:
                # Short 포지션 익절
                data.loc[data.index[i], 'ShortProfitSignal'] = True
                data.loc[data.index[i], 'ExitPrice'] = take_profit
                data.loc[data.index[i], 'ProfitPercentage'] = (entry_price - take_profit) / entry_price * 100
                in_short_position = False
            elif data['High'].iloc[i] >= stop_loss:
                # Short 포지션 손절
                data.loc[data.index[i], 'ShortLossSignal'] = True
                data.loc[data.index[i], 'ExitPrice'] = stop_loss
                data.loc[data.index[i], 'ProfitPercentage'] = (entry_price - stop_loss) / entry_price * 100
                in_short_position = False
            elif long_condition1 and long_condition2 and long_condition3:
                # Short 포지션 청산 후 Long 진입
                data.loc[data.index[i], 'ShortExitSignal'] = True
                data.loc[data.index[i], 'ExitPrice'] = data['Close'].iloc[i]
                data.loc[data.index[i], 'ProfitPercentage'] = (entry_price - data['Close'].iloc[i]) / entry_price * 100
                in_short_position = False
                
                # Long 진입
                data.loc[data.index[i], 'LongSignal'] = True
                data.loc[data.index[i], 'EntryPrice'] = data['Close'].iloc[i]
                in_long_position = True
                entry_price = data['Close'].iloc[i]
                stop_loss = data['ParabolicSAR'].iloc[i]
                take_profit = entry_price + (entry_price - stop_loss)

        elif not in_long_position and not in_short_position:
            if long_condition1 and long_condition2 and long_condition3:
                # Long 진입
                data.loc[data.index[i], 'LongSignal'] = True
                data.loc[data.index[i], 'EntryPrice'] = data['Close'].iloc[i]
                in_long_position = True
                entry_price = data['Close'].iloc[i]
                stop_loss = data['ParabolicSAR'].iloc[i]
                take_profit = entry_price + (entry_price - stop_loss)
            elif short_condition1 and short_condition2 and short_condition3:
                # Short 진입
                data.loc[data.index[i], 'ShortSignal'] = True
                data.loc[data.index[i], 'EntryPrice'] = data['Close'].iloc[i]
                in_short_position = True
                entry_price = data['Close'].iloc[i]
                stop_loss = data['ParabolicSAR'].iloc[i]
                take_profit = entry_price - (stop_loss - entry_price)

    return data


def create_chart(data: pd.DataFrame) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, subplot_titles=('BTC/USD', 'MACD'),
                        row_heights=[0.7, 0.3])

    # 캔들스틱 차트
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='BTC/USD'),
                  row=1, col=1)

    # EMA 200
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA200'],
                             line=dict(color='blue', width=1.5),
                             name='EMA 200'),
                  row=1, col=1)

    # Parabolic SAR
    fig.add_trace(go.Scatter(x=data.index, y=data['ParabolicSAR'],
                             mode='markers',
                             marker=dict(size=2, color='purple', symbol='triangle-down'),
                             name='Parabolic SAR'),
                  row=1, col=1)

    # Long 매수 신호
    long_signals = data[data['LongSignal']]
    fig.add_trace(go.Scatter(x=long_signals.index, y=long_signals['Low'],
                             mode='markers',
                             marker=dict(size=10, color='blue', symbol='triangle-up'),
                             name='Long Signal',
                             text=long_signals.apply(lambda row: f"Long 진입: {row['EntryPrice']:.2f}", axis=1),
                             hoverinfo='text+x+y'),
                  row=1, col=1)

    # Short 매수 신호
    short_signals = data[data['ShortSignal']]
    fig.add_trace(go.Scatter(x=short_signals.index, y=short_signals['High'],
                             mode='markers',
                             marker=dict(size=10, color='orange', symbol='triangle-down'),
                             name='Short Signal',
                             text=short_signals.apply(lambda row: f"Short 진입: {row['EntryPrice']:.2f}", axis=1),
                             hoverinfo='text+x+y'),
                  row=1, col=1)

    # Long 익절 신호
    long_profit_signals = data[data['LongProfitSignal']]
    fig.add_trace(go.Scatter(x=long_profit_signals.index, y=long_profit_signals['High'],
                             mode='markers',
                             marker=dict(size=10, color='green', symbol='triangle-up'),
                             name='Long Profit',
                             text=long_profit_signals.apply(lambda row: f"Long 매수: {row['EntryPrice']:.2f}<br>매도: {row['ExitPrice']:.2f}<br>수익률: {row['ProfitPercentage']:.2f}%", axis=1),
                             hoverinfo='text+x+y'),
                  row=1, col=1)

    # Long 손절 신호
    long_loss_signals = data[data['LongLossSignal']]
    fig.add_trace(go.Scatter(x=long_loss_signals.index, y=long_loss_signals['Low'],
                             mode='markers',
                             marker=dict(size=10, color='red', symbol='triangle-down'),
                             name='Long Loss',
                             text=long_loss_signals.apply(lambda row: f"Long 매수: {row['EntryPrice']:.2f}<br>매도: {row['ExitPrice']:.2f}<br>손실률: {row['ProfitPercentage']:.2f}%", axis=1),
                             hoverinfo='text+x+y'),
                  row=1, col=1)

    # Short 익절 신호
    short_profit_signals = data[data['ShortProfitSignal']]
    fig.add_trace(go.Scatter(x=short_profit_signals.index, y=short_profit_signals['Low'],
                             mode='markers',
                             marker=dict(size=10, color='lime', symbol='triangle-down'),
                             name='Short Profit',
                             text=short_profit_signals.apply(lambda row: f"Short 매도: {row['EntryPrice']:.2f}<br>매수: {row['ExitPrice']:.2f}<br>수익률: {row['ProfitPercentage']:.2f}%", axis=1),
                             hoverinfo='text+x+y'),
                  row=1, col=1)

    # Short 손절 신호
    short_loss_signals = data[data['ShortLossSignal']]
    fig.add_trace(go.Scatter(x=short_loss_signals.index, y=short_loss_signals['High'],
                             mode='markers',
                             marker=dict(size=10, color='pink', symbol='triangle-up'),
                             name='Short Loss',
                             text=short_loss_signals.apply(lambda row: f"Short 매도: {row['EntryPrice']:.2f}<br>매수: {row['ExitPrice']:.2f}<br>손실률: {row['ProfitPercentage']:.2f}%", axis=1),
                             hoverinfo='text+x+y'),
                  row=1, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=data.index, y=data['MACD'],
                             line=dict(color='blue', width=1.5),
                             name='MACD'),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['Signal'],
                             line=dict(color='orange', width=1.5),
                             name='Signal'),
                  row=2, col=1)

    # MACD Histogram
    colors = ['green' if val >= 0 else 'red' for val in data['MACD_Histogram']]
    fig.add_trace(go.Bar(x=data.index, y=data['MACD_Histogram'],
                         marker_color=colors,
                         name='Histogram'),
                  row=2, col=1)

    fig.update_layout(
        title='Bitcoin 1-hour Candlestick Chart with Long and Short Signals',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )

    return fig

def main() -> None:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # 30일 데이터

    btc_data = get_bitcoin_data(start_date, end_date)
    btc_data = add_ema_to_dataframe(btc_data, period=200, ema_column_name='EMA200')
    btc_data = add_macd_to_dataframe(btc_data)
    btc_data = add_parabolic_sar_to_dataframe(btc_data)
    btc_data = add_trade_signals(btc_data)

    fig = create_chart(btc_data)
    fig.write_html("bitcoin_chart_with_signals.html")
    print("Chart saved as 'bitcoin_chart_with_signals.html'")
    fig.show()

if __name__ == "__main__":
    main()