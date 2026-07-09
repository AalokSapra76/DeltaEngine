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

if trigger_text:
    delta_trigger = float(trigger_text)
else:
    delta_trigger = DEFAULT_TRIGGER

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

client.find_option_token(
    symbol,
    expiry,
    strike,
    option_type
)

webhook = Webhook(
    WEBHOOK_URL
)


# ==================================================
# LIVE VALUES
# ==================================================

spot = 0.0
premium = 0.0
delta = 0.0

triggered = False

status = "Monitoring"
webhook_status = "Waiting"

IV = 12.2
# ============================
# main.py
# PART 2 / 3
# DO NOT RUN YET
# ============================

# ==================================================
# DASHBOARD
# ==================================================

def build_dashboard():

    table = Table(
        title="BK DELTA ENGINE v1.0",
        box=box.ROUNDED,
        expand=True
    )

    table.add_column(
        "Field",
        style="cyan",
        width=20
    )

    table.add_column(
        "Value",
        style="bold white"
    )

    table.add_row(
        "Underlying",
        symbol
    )

    table.add_row(
        "Contract",
        f"{int(strike)} {option_type}"
    )

    table.add_row(
        "Expiry",
        expiry
    )

    table.add_section()

    table.add_row(
        "Spot",
        f"{spot:.2f}"
    )

    table.add_row(
        "Premium",
        f"{premium:.2f}"
    )

    table.add_row(
        "Delta",
        f"{delta:.4f}"
    )

    table.add_section()

    table.add_row(
        "Trigger",
        f"{delta_trigger:.4f}"
    )

    table.add_row(
        "Status",
        status
    )

    table.add_row(
        "Webhook",
        webhook_status
    )

    return table


# ==================================================
# TICK CALLBACK
# ==================================================

def tick_handler(option_tick, spot_tick):

    global spot
    global premium
    global delta

    global triggered
    global status
    global webhook_status

    premium = option_tick["last_price"]

    spot = spot_tick["last_price"]

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
        IV,
        days,
        option_type,
        RISK_FREE_RATE
    )

    if (not triggered) and (delta >= delta_trigger):

        triggered = True

        status = "TRIGGERED"

        try:

            webhook.send(
                symbol,
                expiry,
                strike,
                option_type,
                delta,
                premium,
                spot
            )

            webhook_status = "SENT"

        except Exception as e:

            webhook_status = f"FAILED : {e}"
            # ============================
# main.py
# PART 3 / 3
# END OF FILE
# ============================

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

    def live_tick_handler(option_tick, spot_tick):

        tick_handler(
            option_tick,
            spot_tick
        )

        live.update(
            build_dashboard(),
            refresh=True
        )

    client.connect(
        live_tick_handler
    )

print()
print("Engine Stopped.")
print()
