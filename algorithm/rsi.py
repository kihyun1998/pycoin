def cal_rsi(data,time_period=14):
    delta = data['Close'].diff(1)
    delta = delta.dropna()
    
    up = delta.copy()
    down = delta.copy()
    
    up[up<0]=0
    down[down>0]=0

    avg_gain = up.ewm(com=time_period-1,min_periods=time_period).mean()
    avg_loss = abs(down.ewm(com=time_period-1,min_periods=time_period).mean())
    
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0/(1.0+rs))
    
    return rsi


def cal_stochastic_rsi(data, k_windw=3, d_windw=3, window=14):
    min_val = data.rolling(window=window, center=False).min()
    max_val = data.rolling(window=window, center=False).max()
    stoch = ( (data-min_val) / (max_val - min_val) ) * 100
    k = stoch.rolling(window=k_windw,center=False).mean()
    d = k.rolling(window=d_windw,center=False).mean()
    
    return k,d