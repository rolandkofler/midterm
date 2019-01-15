from cryptowatch_client import Client
import json

client = Client(timeout=30)
response = client.get_allowance()
print(response.status_code, response.json())
response = client.get_markets_ohlc(exchange='kraken', pair='btcusd') # GET /markets/gdax/btcusd/ohlc

with open("kraken.json", "w") as write_file:
    json.dump(response.json(), write_file)