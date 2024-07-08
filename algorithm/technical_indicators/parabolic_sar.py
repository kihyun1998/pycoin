# technical_indicators/parabolicSAR.py

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
        trend[i] = trend[i-1]
        sar[i] = sar[i-1] + af[i-1] * (ep[i-1] - sar[i-1])
        
        if trend[i] > 0:
            if low[i] > sar[i]:
                sar[i] = min(sar[i], low[i-1], low[i-2])
            if high[i] > ep[i-1]:
                ep[i] = high[i]
                af[i] = min(af[i-1] + step, max_step)
            else:
                ep[i] = ep[i-1]
                af[i] = af[i-1]
            if sar[i] > low[i]:
                trend[i] = -1
                sar[i] = ep[i]
                ep[i] = low[i]
                af[i] = step
        else:
            if high[i] < sar[i]:
                sar[i] = max(sar[i], high[i-1], high[i-2])
            if low[i] < ep[i-1]:
                ep[i] = low[i]
                af[i] = min(af[i-1] + step, max_step)
            else:
                ep[i] = ep[i-1]
                af[i] = af[i-1]
            if sar[i] < high[i]:
                trend[i] = 1
                sar[i] = ep[i]
                ep[i] = high[i]
                af[i] = step
    
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