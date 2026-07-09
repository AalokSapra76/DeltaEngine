# main.py

"""
BK DELTA ENGINE v1.0
"""

import json
from datetime import datetime

from auth import AuthManager
from kite_client import KiteClient
from greeks import Greeks
from webhook import Webhook


# ==================================================
# CONFIG
# ==================================================

with open("config.json") as f:
    config = json.load(f)

API_KEY = config["kite"]["api_key"]
API_SECRET = config["kite"]["api_secret"]

RISK_FREE_RATE = config["market"]["risk_free_rate"]

WEBHOOK_URL = config["webhook"]["url"]

DEFAULT_TRIGGER = config["delta_rule"]["default_trigger"]


# ==================================================
# STARTUP
# ==================================================

print()
print("=========================================")
print("        BK DELTA ENGINE v1.0")
print("=========================================")
print()

symbol = input(
    "Underlying (NIFTY/BANKNIFTY/FINNIFTY) : "
).strip().upper()

expiry = input(
    "Expiry (YYYY-MM-DD) : "
).strip()

strike = float(
    input("Strike : ").strip()
)

option_type = input(
    "Option Type (CE/PE) : "
).strip().upper()

trigger_text = input(
    f"Delta Trigger [{DEFAULT_TRIGGER}] : "
).strip()

if trigger_text == "":
    delta_trigger = DEFAULT_TRIGGER
else:
    delta_trigger = float(trigger_text)

print()
print("Searching contract...")
print()


# ==================================================
# LOGIN
# ==================================================

auth = AuthManager(
    API_KEY,
    API_SECRET
)

access_token = auth.get_access_token()


# ==================================================
# CLIENT
# ==================================================

client = KiteClient(
    API_KEY,
    access_token
)

option_token = client.find_option_token(
    symbol,
    expiry,
    strike,
    option_type
)

print(f"Option Token : {option_token}")
print(f"Spot Token   : {client.spot_token}")
print()

webhook = Webhook(WEBHOOK_URL)

triggered = False


# ==================================================
# LIVE CALLBACK
# ==================================================

def tick_handler(option_tick, spot_tick):

    global triggered

    premium = option_tick["last_price"]
    spot = spot_tick["last_price"]

    #
    # v1.0
    # Fixed IV
    #

    iv = 12.2

    expiry_date = datetime.strptime(
        expiry,
        "%Y-%m-%d"
    )

    days = max(
        (expiry_date - datetime.now()).days,
        1
    )

    delta = Greeks.delta(
        spot,
        strike,
        iv,
        days,
        option_type,
        RISK_FREE_RATE
    )

    print(
        f"Spot={spot:.2f}   "
        f"Premium={premium:.2f}   "
        f"Delta={delta:.4f}"
    )

    if (not triggered) and (delta >= delta_trigger):

        triggered = True

        print()
        print("=========================================")
        print("         DELTA TRIGGERED")
        print("=========================================")
        print()

        webhook.send(
            symbol,
            expiry,
            strike,
            option_type,
            delta,
            premium,
            spot
        )


# ==================================================
# START
# ==================================================

print()
print("Connecting to Kite...")
print()

client.connect(
    tick_handler
)