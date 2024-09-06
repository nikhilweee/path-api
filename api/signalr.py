import json
import time
import logging
import requests
from functools import partial
from signalrcore.hub_connection_builder import HubConnectionBuilder

logger = logging.getLogger(__name__)

stations = {
    "Newark": "NWK",
    "Harrison": "HAR",
    "Journal Square": "JSQ",
    "Grove Street": "GRV",
    "Exchange Place": "EXP",
    "World Trade Center": "WTC",
    "Newport": "NEW",
    "Hoboken": "HOB",
    "Christopher Street": "CHR",
    "9th Street": "09S",
    "14th Street": "14S",
    "23rd Street": "23S",
    "33rd Street": "33S",
}

directions = {
    "New York": "ToNY",
    "New Jersey": "ToNJ",
}


class SignalRClient:
    def __init__(self, broker_url, broker_token):
        self.broker_url = broker_url
        self.broker_token = broker_token
        self.results = []

    def _fetch_creds(self, station, direction):
        headers = {
            "Authorization": f"Bearer {self.broker_token}",
        }

        json_data = {
            "station": station,
            "direction": direction,
        }

        response = requests.post(
            self.broker_url,
            headers=headers,
            json=json_data,
        )
        res_json = response.json()

        return res_json

    def _build_hub(self, hub_url, hub_token):
        hub_conn = (
            HubConnectionBuilder()
            .with_url(
                hub_url,
                options={
                    "access_token_factory": lambda: hub_token,
                },
            )
            # .configure_logging(logging.DEBUG)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 5,
                }
            )
            .build()
        )

        return hub_conn

    def handle_message(self, messages, station, direction):
        json_message = json.loads(messages[1])

        result = None
        for x in self.results:
            if x["consideredStation"] == stations[station]:
                result = x
        if not result:
            result = {"consideredStation": stations[station], "destinations": []}
            self.results.append(result)

        destination = None
        for x in result["destinations"]:
            if x["label"] == directions[direction]:
                destination = x
        if not destination:
            destination = {"label": directions[direction], "messages": []}
            result["destinations"].append(destination)

        # for message in json_message["messages"]:
        #     message["target"] = json_message["target"]

        destination["messages"] = json_message["messages"]

        with open("artifacts/data.json", "w") as f:
            json.dump(self.results, f, indent=2)

    def start_hub(self, station="Newark", direction="New York"):
        hub_creds = self._fetch_creds(station, direction)
        hub_conn = self._build_hub(hub_creds["url"], hub_creds["accessToken"])

        hub_conn.on_open(
            lambda: print("hub opened", stations[station], directions[direction])
        )
        hub_conn.on_close(
            lambda: print("hub closed", stations[station], directions[direction])
        )
        handler = partial(self.handle_message, station=station, direction=direction)
        hub_conn.on("SendMessage", handler)
        hub_conn.start()
        # hub_conn.stop()
        return hub_conn
