# technical_indicators/macd.py

import pandas as pd
from typing import Tuple

def calculate_macd(
    data: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    column: str = 'Close'
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    MACD(Moving Average Convergence Divergence)를 계산합니다.

    :param data: 시계열 데이터
    :param fast_period: 빠른 EMA의 기간 (기본값: 12)
    :param slow_period: 느린 EMA의 기간 (기본값: 26)
    :param signal_period: 시그널 라인의 기간 (기본값: 9)
    :param column: MACD를 계산할 열 이름 (기본값: 'Close')
    :return: MACD 라인, 시그널 라인, MACD 히스토그램
    """
    fast_ema = data[column].ewm(span=fast_period, adjust=False).mean()
    slow_ema = data[column].ewm(span=slow_period, adjust=False).mean()
    
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    macd_histogram = macd_line - signal_line
    
    return macd_line, signal_line, macd_histogram

def add_macd_to_dataframe(
    data: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    column: str = 'Close'
) -> pd.DataFrame:
    """
    주어진 DataFrame에 MACD 관련 열을 추가합니다.

    :param data: 시계열 데이터
    :param fast_period: 빠른 EMA의 기간 (기본값: 12)
    :param slow_period: 느린 EMA의 기간 (기본값: 26)
    :param signal_period: 시그널 라인의 기간 (기본값: 9)
    :param column: MACD를 계산할 열 이름 (기본값: 'Close')
    :return: MACD 열이 추가된 데이터
    """
    macd_line, signal_line, macd_histogram = calculate_macd(
        data, fast_period, slow_period, signal_period, column
    )
    
    data['MACD'] = macd_line
    data['Signal'] = signal_line
    data['MACD_Histogram'] = macd_histogram
    
    return data