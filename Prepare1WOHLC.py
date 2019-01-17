import json
import pandas

with open("kraken.json", "r") as file:
    OHLCs= json.load(file)
weeklyCandles = OHLCs["result"]["604800"]
df = pandas.DataFrame(weeklyCandles, columns= ["CloseTime", "OpenPrice", "HighPrice", "LowPrice", "ClosePrice", "?","Volume"])
df['CloseTime'] = pandas.to_datetime(df['CloseTime'],unit='s')
df = df[df["ClosePrice"] > 0]    # remove empty rows
df = df[df["?"]!=198105.7]       # remove strange outlair, TODO: understand column meaning
print (df.describe())
df.to_csv("kraken-1WOLHC-2013-2019.txt", index=False)
