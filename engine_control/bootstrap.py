"""
Bootstrap BK Delta Engine.

Runs once during FastAPI startup.

Responsibilities:
- Authenticate with Kite
- Create Kite client
- Download instrument master
- Populate instrument cache

Does NOT:
- Start websocket
- Start monitoring
"""

import json

from auth import AuthManager
from kite_client import KiteClient
from engine_control.instrument_cache import (
    get_instruments,
)

# ==================================================
# CONFIG
# ==================================================

with open("config.json") as f:
    config = json.load(f)

API_KEY = config["kite"]["api_key"]
API_SECRET = config["kite"]["api_secret"]


# ==================================================
# GLOBAL CLIENT
# ==================================================

_client = None


def get_client():
    return _client


# ==================================================
# BOOTSTRAP
# ==================================================

def bootstrap_kite():

    global _client

    if _client is not None:
        return _client

    print()
    print("=" * 55)
    print("BK DELTA ENGINE BOOTSTRAP")
    print("=" * 55)
    print()

    auth = AuthManager(
        API_KEY,
        API_SECRET
    )

    access_token = auth.get_access_token()

    _client = KiteClient(
        API_KEY,
        access_token
    )

    # Populate instrument cache only if empty
    if get_instruments():

        print(
            f"Using cached instruments ({len(get_instruments())})"
        )

    else:

        _client.download_instruments()

    print("Bootstrap complete.")

    return _client


# ==================================================
# SHUTDOWN
# ==================================================

def disconnect_client():
    global _client

    if _client is None:
        return

    try:
        _client.disconnect()
    except Exception as e:
        print("Client disconnect ignored:", e)
