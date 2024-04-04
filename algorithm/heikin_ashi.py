import plotly.graph_objects as go
import yfinance as yf
from math_extention.math_extention import perfectRound

symbol = "BTC-USD"
df = yf.download(tickers=symbol, period="1d", interval="1m")


heikin_ashi_df = df[['Open','High','Low','Close']].copy()
heikin_ashi_df['Close'] = perfectRound(((df['Open']+df['High']+df['Low']+df['Close'])/4),2)

for i in range(len(df)):
    if i==0:
        heikin_ashi_df.iat[0,0] = perfectRound(((df['Open'].iloc[0]+df['Close'].iloc[0])/2),2)
    else:
        heikin_ashi_df.iat[i,0] = perfectRound(((heikin_ashi_df.iat[i-1,0] + heikin_ashi_df.iat[i-1,3])/2),2)

heikin_ashi_df['High'] = heikin_ashi_df.loc[:,['Open','Close']].join(df['High']).max(axis=1)

heikin_ashi_df['Low'] = heikin_ashi_df.loc[:,['Open','Close']].join(df['Low']).min(axis=1)

fig = go.Figure(data=[go.Candlestick(x=heikin_ashi_df.index,open=heikin_ashi_df.Open,high=heikin_ashi_df.High,low=heikin_ashi_df.Low,close=heikin_ashi_df.Close)])

fig.update_layout(title="BTC-USD",xaxis_title="BTC-USD",yaxis_title='Price')

fig.show()