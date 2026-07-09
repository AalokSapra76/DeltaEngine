"""
Zerodha Kite Connect client.
Handles:
- Login
- Instrument lookup
- Live WebSocket
"""

import datetime
from kiteconnect import KiteConnect, KiteTicker


class KiteClient:

    def __init__(self, api_key, access_token):

        self.api_key = api_key
        self.access_token = access_token

        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)

        self.kws = KiteTicker(api_key, access_token)

        self.option_token = None
        self.spot_token = 256265          # NIFTY 50 Index

        self.last_option_tick = None
        self.last_spot_tick = None

    # -------------------------------------------------

    def download_instruments(self):

        return self.kite.instruments("NFO")

    # -------------------------------------------------

    def find_option_token(
        self,
        symbol,
        expiry,
        strike,
        option_type
    ):

        expiry = datetime.datetime.strptime(
            expiry,
            "%Y-%m-%d"
        ).date()

        instruments = self.download_instruments()

        for item in instruments:

            if (
                item["name"] == symbol
                and item["expiry"] == expiry
                and float(item["strike"]) == float(strike)
                and item["instrument_type"] == option_type
            ):

                self.option_token = item["instrument_token"]

                return self.option_token

        raise Exception("Option contract not found.")

    # -------------------------------------------------

    def connect(self, on_tick_callback):

        def on_connect(ws, response):

            print("Connected.")

            ws.subscribe([
                self.option_token,
                self.spot_token
            ])

            ws.set_mode(
                ws.MODE_FULL,
                [
                    self.option_token,
                    self.spot_token
                ]
            )

        def on_ticks(ws, ticks):

            for tick in ticks:

                token = tick["instrument_token"]

                if token == self.option_token:
                    self.last_option_tick = tick

                elif token == self.spot_token:
                    self.last_spot_tick = tick

            if (
                self.last_option_tick is not None
                and self.last_spot_tick is not None
            ):

                on_tick_callback(
                    self.last_option_tick,
                    self.last_spot_tick
                )

        def on_close(ws, code, reason):

            print("Socket Closed:", reason)

        self.kws.on_connect = on_connect
        self.kws.on_ticks = on_ticks
        self.kws.on_close = on_close

        self.kws.connect(threaded=False)