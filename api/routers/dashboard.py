"""
Dashboard router.

Consumes the read-only engine snapshot published by main.py via
engine_control.snapshot. Never reads engine internals directly.

Fallback: when the engine has published no snapshot yet (idle/stopped),
returns configured contracts from the store with neutral runtime
defaults so the UI can render the configured set without inventing
live values.
"""

from fastapi import APIRouter

from contract_store import get_contracts
from engine_control.snapshot import get_engine_snapshot

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def get_dashboard():
    snapshot = get_engine_snapshot()
    if snapshot:
        return snapshot

    return [
        {
            "id": c["id"],
            "instrument": c["instrument"],
            "expiry": c["expiry"],
            "strike": c["strike"],
            "option_type": c["option_type"],
            "trigger_direction": c["trigger_direction"],
            "delta_threshold": c["delta_threshold"],
            "webhook_profile_id": c.get("webhook_profile_id", ""),
            "spot": None,
            "premium": None,
            "current_delta": None,
            "status": "idle",
            "triggered": False,
            "last_updated": None,
        }
        for c in get_contracts()
    ]
