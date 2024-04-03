import pprint

import ccxt

from securite.decrypter import decrypter_les_donnees

data = decrypter_les_donnees()
cle_API = data["api_key"]
clef_screte = data["secret_key"]

# Login
exchange = ccxt.binance(config={
    'apiKey':cle_API,
    'secret':clef_screte,
    'enableRateLimit':True,
    'options':{
        'defaultType':'future'
    }
})

markets = exchange.load_markets()
pprint.pprint(markets)
print(len(markets.keys()))