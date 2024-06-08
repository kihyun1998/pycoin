def cal_rsi(data, rsi_length=14):
    delta = data['Close'].diff(1)
    up = delta.where(delta > 0, 0)
    down = -delta.where(delta < 0, 0)
    
    avg_gain = up.ewm(com=rsi_length-1, min_periods=rsi_length).mean()
    avg_loss = down.ewm(com=rsi_length-1, min_periods=rsi_length).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    
    return rsi


#     return k,d
def stochastic_rsi(rsi, k_period=3, d_period=3, stoch_length=14):
    min_val = rsi.rolling(window=stoch_length).min()
    max_val = rsi.rolling(window=stoch_length).max()
    stoch_rsi = ((rsi - min_val) / (max_val - min_val)) * 100
    
    k = stoch_rsi.rolling(window=k_period).mean()
    d = k.rolling(window=d_period).mean()
    
    return k, d

