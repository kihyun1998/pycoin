# technical_indicators/parabolic_sar.py

import pandas as pd
import numpy as np
from typing import Tuple

def calculate_parabolic_sar(data: pd.DataFrame, step: float = 0.02, max_step: float = 0.2) -> pd.Series:
    """
    Parabolic SAR (Stop And Reverse)를 계산합니다.

    :param data: 시계열 데이터 (High, Low 컬럼 필요)
    :param step: SAR 계산에 사용되는 가속 인자의 초기값 (기본값: 0.02)
    :param max_step: 가속 인자의 최대값 (기본값: 0.2)
    :return: Parabolic SAR 값
    """
    high, low = data['High'], data['Low']
    
    sar = low.copy()
    ep = high.copy()  # Extreme Point
    af = pd.Series(step, index=high.index)  # Acceleration Factor
    trend = pd.Series(1, index=high.index)  # 1 for uptrend, -1 for downtrend
    
    for i in range(2, len(data)):
        trend.iloc[i] = trend.iloc[i-1]
        sar.iloc[i] = sar.iloc[i-1] + af.iloc[i-1] * (ep.iloc[i-1] - sar.iloc[i-1])
        
        if trend.iloc[i] > 0:
            if low.iloc[i] > sar.iloc[i]:
                sar.iloc[i] = min(sar.iloc[i], low.iloc[i-1], low.iloc[i-2])
            if high.iloc[i] > ep.iloc[i-1]:
                ep.iloc[i] = high.iloc[i]
                af.iloc[i] = min(af.iloc[i-1] + step, max_step)
            else:
                ep.iloc[i] = ep.iloc[i-1]
                af.iloc[i] = af.iloc[i-1]
            if sar.iloc[i] > low.iloc[i]:
                trend.iloc[i] = -1
                sar.iloc[i] = ep.iloc[i]
                ep.iloc[i] = low.iloc[i]
                af.iloc[i] = step
        else:
            if high.iloc[i] < sar.iloc[i]:
                sar.iloc[i] = max(sar.iloc[i], high.iloc[i-1], high.iloc[i-2])
            if low.iloc[i] < ep.iloc[i-1]:
                ep.iloc[i] = low.iloc[i]
                af.iloc[i] = min(af.iloc[i-1] + step, max_step)
            else:
                ep.iloc[i] = ep.iloc[i-1]
                af.iloc[i] = af.iloc[i-1]
            if sar.iloc[i] < high.iloc[i]:
                trend.iloc[i] = 1
                sar.iloc[i] = ep.iloc[i]
                ep.iloc[i] = high.iloc[i]
                af.iloc[i] = step
    
    return sar

def add_parabolic_sar_to_dataframe(data: pd.DataFrame, step: float = 0.02, max_step: float = 0.2) -> pd.DataFrame:
    """
    주어진 DataFrame에 Parabolic SAR 열을 추가합니다.

    :param data: 시계열 데이터 (High, Low 컬럼 필요)
    :param step: SAR 계산에 사용되는 가속 인자의 초기값 (기본값: 0.02)
    :param max_step: 가속 인자의 최대값 (기본값: 0.2)
    :return: Parabolic SAR 열이 추가된 데이터
    """
    data['ParabolicSAR'] = calculate_parabolic_sar(data, step, max_step)
    return data