def cal_rsi(data,rsi_length=14):
    delta = data['Close'].diff(1)
    delta = delta.dropna()
    
    up = delta.copy()
    down = delta.copy()
    
    up[up<0]=0
    down[down>0]=0

    avg_gain = up.ewm(com=rsi_length-1,min_periods=rsi_length).mean()
    avg_loss = abs(down.ewm(com=rsi_length-1,min_periods=rsi_length).mean())
    
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0/(1.0+rs))
    
    return rsi


def stochastic_rsi(rsi, k=3, d=3, stoch_length=14):
    min_val = rsi.rolling(window=stoch_length, center=False).min()
    max_val = rsi.rolling(window=stoch_length, center=False).max()
    stoch_rsi = ( (rsi - min_val) / (max_val - min_val) ) * 100
    k = stoch_rsi.rolling(window=k,center=False).mean()
    d = k.rolling(window=d,center=False).mean()
    
    return k,d

