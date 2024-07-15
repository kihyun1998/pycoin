# Binance Algorithmic Trading System

매매 알고리즘을 활용하여 바이낸스에서 코인 자동매매 시스템을 만드는 것을 목표로 한다.

## 사용 알고리즘

1. 200 EMA
2. MACD
3. Parabolic SAR

## 매매 전략

### Long 매수 & 매도 조건

- **매수**

1. 가격이 200 EMA선 위에 있는가?

2. MACD Line이 Signal Line을 상향 돌파하거나 위에 있을 때  Parabolic SAR가 캔들 아래쪽에 위치하는가?

- **매도**

Parabolic SAR가 위치한 곳과 매수 가격의 비율을 1로 놓았을 때 
Parabolic SAR가 위치한 곳이 손절 지점이고 같은 비율로 위로 1을 가면 익절 지점이다.


### Short 매수 & 매도 조건

- **매수**

1. 가격이 200 EMA선 아래에 있는가?

2. MACD Line이 Signal Line을 하향 돌파하거나 그 이후에 Parabolic SAR가 캔들 위쪽에위치하는가?

- **매도**

Parabolic SAR가 손절 지점이고 1대1 비율로 익절지점을 잡는다.