"""
Zerodha Kite Connect client.
Handles:
- Login
- Instrument lookup
- Live WebSocket
"""

import datetime
from kiteconnect import KiteConnect, KiteTicker
from engine_control.instrument_cache import get_instruments, set_instruments


class KiteClient:

    SPOT_TOKENS = {
        "NIFTY": 256265,
        "BANKNIFTY": 260105,
        "FINNIFTY": 257801,
    }

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

        self.option_tokens = {}
        self.contract_spot_tokens = {}
        self.last_option_ticks = {}
        self.last_spot_ticks = {}

    # -------------------------------------------------

    def download_instruments(self):

        instruments = get_instruments()

        if instruments:
            return instruments

        print("Downloading NFO Instrument Master...")

        instruments = self.kite.instruments("NFO")

        set_instruments(instruments)

        print(f"Cached {len(instruments)} instruments.")

        return instruments

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

    def find_option_tokens(self, contracts):

        instruments = self.download_instruments()

        self.option_tokens = {}
        self.contract_spot_tokens = {}

        for contract_index, contract in enumerate(contracts):

            symbol = contract["instrument"].upper()
            expiry = datetime.datetime.strptime(
                contract["expiry"],
                "%Y-%m-%d"
            ).date()

            option_token = None

            for item in instruments:

                if (
                    item["name"] == symbol
                    and item["expiry"] == expiry
                    and float(item["strike"]) == float(contract["strike"])
                    and item["instrument_type"] == contract["option_type"]
                ):

                    option_token = item["instrument_token"]
                    break

            if option_token is None:
                raise Exception(
                    "Option contract not found: "
                    f"{symbol} {contract['expiry']} "
                    f"{contract['strike']} {contract['option_type']}"
                )

            if symbol not in self.SPOT_TOKENS:
                raise Exception(
                    f"Unsupported underlying: {symbol}"
                )

            self.option_tokens.setdefault(
                option_token,
                []
            ).append(contract_index)
            self.contract_spot_tokens[contract_index] = (
                self.SPOT_TOKENS[symbol]
            )

        print("OPTION TOKENS:", self.option_tokens)
        print("SPOT TOKENS:", self.contract_spot_tokens)

        return {
            contract_index: option_token
            for option_token, contract_indexes
            in self.option_tokens.items()
            for contract_index in contract_indexes
        }

    # -------------------------------------------------

    def connect_multiple(self, on_tick_callback):

        subscribed_tokens = list(
            self.option_tokens.keys()
        ) + list(
            set(self.contract_spot_tokens.values())
        )

        print("\n====================================")
        print("Subscribing to tokens:")
        print(subscribed_tokens)
        print("====================================\n")

        def on_connect(ws, response):

            print("========== WEBSOCKET CONNECTED ==========")
            print("Response:", response)
            print("Subscribing:", subscribed_tokens)

            ws.subscribe(subscribed_tokens)

            ws.set_mode(
                ws.MODE_FULL,
                subscribed_tokens
            )

        def on_ticks(ws, ticks):

            for tick in ticks:

                token = tick["instrument_token"]

                if token in self.option_tokens:

                    for contract_index in self.option_tokens[token]:
                        self.last_option_ticks[contract_index] = tick

                elif token in self.contract_spot_tokens.values():
                    self.last_spot_ticks[token] = tick

            for contract_index, option_tick in (
                self.last_option_ticks.items()
            ):

                spot_token = self.contract_spot_tokens[
                    contract_index
                ]
                spot_tick = self.last_spot_ticks.get(spot_token)

                if spot_tick is not None:
                    on_tick_callback(
                        contract_index,
                        option_tick,
                        spot_tick
                    )

        def on_close(ws, code, reason):

            print("Socket Closed:", reason)

        def on_error(ws, code, reason):
            print("========== WEBSOCKET ERROR ==========")
            print(code)
            print(reason)

        def on_reconnect(ws, attempts):
            print("========== RECONNECT ==========")
            print("Attempt:", attempts)

        def on_noreconnect(ws):
            print("========== NO RECONNECT ==========")

        self.kws.on_connect = on_connect
        self.kws.on_ticks = on_ticks
        self.kws.on_close = on_close
        self.kws.on_error = on_error
        self.kws.on_reconnect = on_reconnect
        self.kws.on_noreconnect = on_noreconnect

        self.kws.connect(threaded=False)

    # -------------------------------------------------

    def connect(self, on_tick_callback):

        def on_connect(ws, response):

            print("========== WEBSOCKET CONNECTED ==========")
            print("Response:", response)
            print("Subscribing:", subscribed_tokens)

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

        def on_error(ws, code, reason):
            print("========== WEBSOCKET ERROR ==========")
            print(code)
            print(reason)

        def on_reconnect(ws, attempts):
            print("========== RECONNECT ==========")
            print("Attempt:", attempts)

        def on_noreconnect(ws):
            print("========== NO RECONNECT ==========")

        self.kws.on_connect = on_connect
        self.kws.on_ticks = on_ticks
        self.kws.on_close = on_close
        self.kws.on_error = on_error
        self.kws.on_reconnect = on_reconnect
        self.kws.on_noreconnect = on_noreconnect

        self.kws.connect(threaded=False)
