
import pandas as pd
from typing import Union

def calculate_ema(data: pd.DataFrame, period: int, column: str = 'Close') -> pd.Series:
    """
    지수 이동 평균(EMA)을 계산합니다.
    
    :param data: 시계열 데이터
    :param period: EMA 기간
    :param column: EMA를 계산할 열 이름 (기본값: 'Close')
    :return: 계산된 EMA 값
    """
    return data[column].ewm(span=period, adjust=False).mean()

def add_ema_to_dataframe(
    data: pd.DataFrame, 
    period: int, 
    column: str = 'Close', 
    ema_column_name: Union[str, None] = None
) -> pd.DataFrame:
    """
    주어진 DataFrame에 EMA 열을 추가합니다.
    
    :param data: 시계열 데이터
    :param period: EMA 기간
    :param column: EMA를 계산할 열 이름 (기본값: 'Close')
    :param ema_column_name: 추가할 EMA 열의 이름 (기본값: None)
    :return: EMA 열이 추가된 데이터
    """
    if ema_column_name is None:
        ema_column_name = f'EMA{period}'
    
    data[ema_column_name] = calculate_ema(data, period, column)
    return data