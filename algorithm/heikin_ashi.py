from math_extention.math_extention import perfectRound

def heikin_ashi(df):
    ha_df = df[['Open','High','Low','Close']].copy()
    ha_df['Close'] = perfectRound(((df['Open']+df['High']+df['Low']+df['Close'])/4),2)

    # Heikin Ashi Open price
    for i in range(len(df)):
        if i==0:
            ha_df.iat[0,0] = perfectRound(((df['Open'].iloc[0]+df['Close'].iloc[0])/2),2)
        else:
            ha_df.iat[i,0] = perfectRound(((ha_df.iat[i-1,0] + ha_df.iat[i-1,3])/2),2)

    # Heikin Ashi High price
    ha_df['High'] = ha_df.loc[:,['Open','Close']].join(df['High']).max(axis=1)

    # Heikin Ashi Low price
    ha_df['Low'] = ha_df.loc[:,['Open','Close']].join(df['Low']).min(axis=1)

    return ha_df