# ============================
# main.py
# PART 1 / 3
# DO NOT RUN YET
# ============================

import json
from datetime import datetime

from rich.live import Live
from rich.table import Table
from rich import box

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
# MONITORED CONTRACTS
# ==================================================

MONITORED_CONTRACTS = [
    {
        "instrument": "NIFTY",
        "expiry": "2026-07-14",
        "strike": 24800,
        "option_type": "CE",
        "delta_threshold": 0.30,
        "trigger_direction": ">",
    },
    {
        "instrument": "NIFTY",
        "expiry": "2026-07-14",
        "strike": 24900,
        "option_type": "CE",
        "delta_threshold": 0.25,
        "trigger_direction": ">",
    },
    {
        "instrument": "NIFTY",
        "expiry": "2026-07-14",
        "strike": 24500,
        "option_type": "PE",
        "delta_threshold": -0.30,
        "trigger_direction": "<",
    },
    {
        "instrument": "NIFTY",
        "expiry": "2026-07-14",
        "strike": 24400,
        "option_type": "PE",
        "delta_threshold": -0.25,
        "trigger_direction": "<",
    },
    {
        "instrument": "NIFTY",
        "expiry": "2026-07-28",
        "strike": 25000,
        "option_type": "CE",
        "delta_threshold": 0.20,
        "trigger_direction": ">",
    },
    {
        "instrument": "NIFTY",
        "expiry": "2026-07-28",
        "strike": 25100,
        "option_type": "CE",
        "delta_threshold": 0.15,
        "trigger_direction": ">",
    },
    {
        "instrument": "NIFTY",
        "expiry": "2026-07-28",
        "strike": 24300,
        "option_type": "PE",
        "delta_threshold": -0.20,
        "trigger_direction": "<",
    },
    {
        "instrument": "NIFTY",
        "expiry": "2026-07-28",
        "strike": 24200,
        "option_type": "PE",
        "delta_threshold": -0.15,
        "trigger_direction": "<",
    },
]


def threshold_reached(delta, threshold, direction):

    if direction == ">":
        return delta > threshold

    if direction == "<":
        return delta < threshold

    raise ValueError(
        f"Unsupported trigger direction: {direction}"
    )


# ==================================================
# STARTUP
# ==================================================

print()
print("=" * 55)
print("              BK DELTA ENGINE v1.0")
print("=" * 55)
print()

print()
print("Searching contracts...")
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

client.find_option_tokens(
    MONITORED_CONTRACTS
)

webhook = Webhook(
    WEBHOOK_URL
)


# ==================================================
# CONTRACT STATE
# ==================================================

IV = 12.2

contract_states = []

for contract in MONITORED_CONTRACTS:

    contract_states.append({
        **contract,
        "spot": 0.0,
        "premium": 0.0,
        "delta": 0.0,
        "triggered": False,
        "status": "Monitoring",
    })


# ==================================================
# DASHBOARD
# ==================================================

def build_dashboard():

    table = Table(
        title="BK DELTA ENGINE v1.0",
        box=box.ROUNDED,
        expand=True
    )

    table.add_column("Instrument", style="cyan")
    table.add_column("Expiry")
    table.add_column("Strike", justify="right")
    table.add_column("Type", justify="center")
    table.add_column("Spot", justify="right")
    table.add_column("Premium", justify="right")
    table.add_column("Delta", justify="right")
    table.add_column("Threshold", justify="right")
    table.add_column("Condition", justify="center")
    table.add_column("Status")
    table.add_column("Triggered", justify="center")

    for contract in contract_states:

        table.add_row(
            contract["instrument"],
            contract["expiry"],
            f"{int(contract['strike'])}",
            contract["option_type"],
            f"{contract['spot']:.2f}",
            f"{contract['premium']:.2f}",
            f"{contract['delta']:.4f}",
            f"{contract['delta_threshold']:.4f}",
            contract["trigger_direction"],
            contract["status"],
            "Yes" if contract["triggered"] else "No",
        )

    return table


# ==================================================
# TICK CALLBACK
# ==================================================

def tick_handler(contract_index, option_tick, spot_tick):

    contract = contract_states[contract_index]

    contract["premium"] = option_tick["last_price"]

    contract["spot"] = spot_tick["last_price"]

    expiry_date = datetime.strptime(
        contract["expiry"],
        "%Y-%m-%d"
    )

    days = max(
        (expiry_date - datetime.now()).days,
        1
    )

    contract["delta"] = Greeks.delta(
        contract["spot"],
        contract["strike"],
        IV,
        days,
        contract["option_type"],
        RISK_FREE_RATE
    )

    if (
        not contract["triggered"]
        and threshold_reached(
            contract["delta"],
            contract["delta_threshold"],
            contract["trigger_direction"]
        )
    ):

        contract["triggered"] = True

        contract["status"] = "TRIGGERED"

        try:

            webhook.send(
                contract["instrument"],
                contract["expiry"],
                contract["strike"],
                contract["option_type"],
                contract["delta"],
                contract["premium"],
                contract["spot"]
            )

        except Exception as e:

            contract["status"] = f"WEBHOOK FAILED: {e}"


# ==================================================
# START ENGINE
# ==================================================

print()
print("Connecting to Kite...")
print()

with Live(
    build_dashboard(),
    refresh_per_second=4,
    screen=True,
    auto_refresh=True,
) as live:

    def live_tick_handler(
        contract_index,
        option_tick,
        spot_tick
    ):

        tick_handler(
            contract_index,
            option_tick,
            spot_tick
        )

        live.update(
            build_dashboard(),
            refresh=True
        )

    client.connect_multiple(
        live_tick_handler
    )

print()
print("Engine Stopped.")
print()
