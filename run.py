import logging
import time

from path.db import get_key_from_db
from path.signalr import SignalRClient

logging.basicConfig(
    format="%(asctime)s %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    force=True,
)
logger = logging.getLogger(__name__)


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


def main():
    url = get_key_from_db("rt_TokenBrokerUrl_Prod")
    token = get_key_from_db("rt_TokenValue_Prod")
    client = SignalRClient(url, token)

    for station in list(stations.values()):
        for direction in list(directions.values()):
            client.start_hub(station, direction)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.stop_hubs()


if __name__ == "__main__":
    main()
