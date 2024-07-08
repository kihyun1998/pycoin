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
    """
    지정된 기간 동안의 비트코인 데이터를 가져옵니다.

    :param start_date: 데이터 시작 날짜
    :param end_date: 데이터 종료 날짜
    :return: 비트코인 데이터
    """
    return yf.download('BTC-USD', start=start_date, end=end_date, interval='5m')

def create_chart(data: pd.DataFrame) -> go.Figure:
    """
    Plotly를 사용하여 캔들스틱 차트, MACD 서브플롯, Parabolic SAR를 생성합니다.

    :param data: 차트 데이터
    :return: Plotly Figure 객체
    """
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
                             marker=dict(size=2, color='green', symbol='triangle-up'),
                             name='Parabolic SAR'),
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

    # 레이아웃 업데이트
    fig.update_layout(
        title='Bitcoin 5-minute Candlestick Chart with 200 EMA, MACD, and Parabolic SAR (3 days)',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

def main() -> None:
    # 현재 날짜로부터 3일 전 데이터부터 가져오기
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)

    # 비트코인 데이터 가져오기
    btc_data = get_bitcoin_data(start_date, end_date)

    # EMA 200 계산
    btc_data = add_ema_to_dataframe(btc_data, period=200, ema_column_name='EMA200')

    # MACD 계산
    btc_data = add_macd_to_dataframe(btc_data)

    # Parabolic SAR 계산
    btc_data = add_parabolic_sar_to_dataframe(btc_data)

    # 차트 생성
    fig = create_chart(btc_data)

    # 차트 표시
    fig.show()

if __name__ == "__main__":
    main()