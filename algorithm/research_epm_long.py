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
    data['BuySignal'] = False
    data['ProfitSignal'] = False
    data['LossSignal'] = False
    data['EntryPrice'] = np.nan
    data['ExitPrice'] = np.nan
    data['ProfitPercentage'] = np.nan
    
    in_position = False
    entry_price = 0
    entry_index = 0
    stop_loss = 0
    take_profit = 0
    
    for i in range(1, len(data)):
        if not in_position:
            condition1 = data['Close'].iloc[i] > data['EMA200'].iloc[i]
            condition2 = (data['MACD'].iloc[i] > data['Signal'].iloc[i] and 
                          data['MACD'].iloc[i-1] <= data['Signal'].iloc[i-1])
            condition3 = data['ParabolicSAR'].iloc[i] < data['Low'].iloc[i]
            
            if condition1 and condition2 and condition3:
                data.loc[data.index[i], 'BuySignal'] = True
                data.loc[data.index[i], 'EntryPrice'] = data['Close'].iloc[i]
                in_position = True
                entry_price = data['Close'].iloc[i]
                entry_index = i
                stop_loss = data['ParabolicSAR'].iloc[i]
                take_profit = entry_price + (entry_price - stop_loss)
        else:
            if data['High'].iloc[i] >= take_profit:
                data.loc[data.index[i], 'ProfitSignal'] = True
                data.loc[data.index[i], 'ExitPrice'] = take_profit
                data.loc[data.index[i], 'ProfitPercentage'] = (take_profit - entry_price) / entry_price * 100
                # 매수 가격 정보 유지
                data.loc[data.index[i], 'EntryPrice'] = entry_price
                in_position = False
            elif data['Low'].iloc[i] <= stop_loss:
                data.loc[data.index[i], 'LossSignal'] = True
                data.loc[data.index[i], 'ExitPrice'] = stop_loss
                data.loc[data.index[i], 'ProfitPercentage'] = (stop_loss - entry_price) / entry_price * 100
                # 매수 가격 정보 유지
                data.loc[data.index[i], 'EntryPrice'] = entry_price
                in_position = False
    
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

    # 매수 신호
    buy_signals = data[data['BuySignal']]
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Low'],
                             mode='markers',
                             marker=dict(size=10, color='blue', symbol='triangle-up'),
                             name='Buy Signal',
                             text=buy_signals.apply(lambda row: f"매수 가격: {row['EntryPrice']:.2f}", axis=1),
                             hoverinfo='text+x+y'),
                  row=1, col=1)

    # 익절 신호
    profit_signals = data[data['ProfitSignal']]
    fig.add_trace(go.Scatter(x=profit_signals.index, y=profit_signals['High'],
                             mode='markers',
                             marker=dict(size=10, color='green', symbol='triangle-up'),
                             name='Profit Signal',
                             text=profit_signals.apply(lambda row: f"매수: {row['EntryPrice']:.2f}<br>매도: {row['ExitPrice']:.2f}<br>수익률: {row['ProfitPercentage']:.2f}%", axis=1),
                             hoverinfo='text+x+y'),
                  row=1, col=1)

    # 손절 신호
    loss_signals = data[data['LossSignal']]
    fig.add_trace(go.Scatter(x=loss_signals.index, y=loss_signals['Low'],
                             mode='markers',
                             marker=dict(size=10, color='red', symbol='triangle-down'),
                             name='Loss Signal',
                             text=loss_signals.apply(lambda row: f"매수: {row['EntryPrice']:.2f}<br>매도: {row['ExitPrice']:.2f}<br>손실률: {row['ProfitPercentage']:.2f}%", axis=1),
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
        title='Bitcoin 1-hour Candlestick Chart with Indicators and Signals',
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