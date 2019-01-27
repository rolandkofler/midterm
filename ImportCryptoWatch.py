from cryptowatch_client import Client
import json
import pandas

pairs = (('kraken', 'xmrusd')) #('kraken', 'btceur'))
client = Client(timeout=30)
response = client.get_allowance()
print(response.status_code, response.json())
for pair in pairs:
    exchangeName = pair[0]
    pairName = pair[1]
    print ('import {:s} {:s}'.format(exchangeName, pairName))
    response = client.get_markets_ohlc(exchange=exchangeName, pair=pairName)
    with open("{:s}-{:s}.json".format(exchangeName, pairName), "w") as write_file:
        json.dump(response.json(), write_file)
    with open("{:s}-{:s}.json".format(exchangeName, pairName), "r") as file:
        OHLCs= json.load(file)
    weeklyCandles = OHLCs["result"]["604800"]
    df = pandas.DataFrame(weeklyCandles, columns= ["CloseTime", "OpenPrice", "HighPrice", "LowPrice", "ClosePrice", "?","Volume"])
    df['CloseTime'] = pandas.to_datetime(df['CloseTime'],unit='s')
    df = df[df["ClosePrice"] > 0]    # remove empty rows
    df = df[df["?"]!=198105.7]       # remove strange outlair, TODO: understand column meaning
    print (df.describe())
    df.to_csv("{:s}-{:s}.csv".format(exchangeName, pairName), index=False)
