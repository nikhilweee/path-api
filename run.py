import time
from api.db import get_key_from_db
from api.signalr import SignalRClient


url = get_key_from_db("rt_TokenBrokerUrl_Prod")
token = get_key_from_db("rt_TokenValue_Prod")


stations = {
    "NWK": "Newark",
    "HAR": "Harrison",
    "JSQ": "Journal Square",
    "GRV": "Grove Street",
    "EXP": "Exchange Place",
    "WTC": "World Trade Center",
    "NEW": "Newport",
    "HOB": "Hoboken",
    "CHR": "Christopher Street",
    "09S": "9th Street",
    "14S": "14th Street",
    "23S": "23rd Street",
    "33S": "33rd Street",
}

directions = {
    "ToNY": "New York",
    "ToNJ": "New Jersey",
}

client = SignalRClient(url, token)


hub_conns = []
for station in list(stations.values())[2:3]:
    for direction in list(directions.values())[:]:
        hub_conn = client.start_hub(station, direction)
        hub_conns.append(hub_conn)

time.sleep(60)

for hub_conn in hub_conns:
    hub_conn.stop()


# hub_conn = client.start_hub("Newark", "New York")
# time.sleep(30)
# hub_conn.stop()
