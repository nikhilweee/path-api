import asyncio
import logging
import os

from path.db import download_db, fetch_latest_checksum, get_key_from_db
from path.signalr import SignalRClient

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
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
    "ToNJ": "New Jersey",
    "ToNY": "New York",
}


async def listen():
    url = get_key_from_db("rt_TokenBrokerUrl_Prod")
    token = get_key_from_db("rt_TokenValue_Prod")
    client = SignalRClient(url, token)

    for station in stations.values():
        for direction in directions.values():
            client.start_hub(station, direction)

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        client.stop_hubs()


async def refresh():
    while True:
        await asyncio.sleep(60 * 60 * 24)
        checksum = fetch_latest_checksum()
        download_db(checksum=checksum)


async def main():
    if not os.path.isfile("artifacts/db.sqlite"):
        download_db(fetch_latest_checksum())

    try:
        await asyncio.gather(refresh(), listen())
    except asyncio.CancelledError:
        print("Stopped")


if __name__ == "__main__":
    asyncio.run(main())
