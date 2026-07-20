"""
Read-only engine snapshot.

The monitoring engine (main.py) remains the sole owner of runtime state
(`contract_states`). After each tick it calls
`publish_snapshot(contract_states)`. This module keeps a per-tick
immutable projection filtered to the fields the dashboard is allowed to
see — nothing more, nothing less.

Rules enforced here:
- Never mutated in place. Each publish replaces the whole list.
- Never fed back into the engine. Read-only for consumers.
- Never a source of truth. On stop/reset the snapshot is cleared and
  the dashboard falls back to configured contracts with idle defaults.
"""

from __future__ import annotations

from threading import Lock
from typing import Any, Iterable


# Exactly the fields the dashboard is allowed to see. Anything else
# published by the engine is dropped here — the snapshot never leaks
# additional runtime state.
_DASHBOARD_FIELDS: tuple[str, ...] = (
    "id",
    "instrument",
    "expiry",
    "strike",
    "option_type",
    "trigger_direction",
    "delta_threshold",
    "spot",
    "premium",
    "current_delta",
    "status",
    "triggered",
    "last_updated",
)

# Map alternative engine keys onto canonical dashboard keys. The engine
# stores its computed delta as `delta`; the dashboard consumes it as
# `current_delta` (matches the frontend LiveContract type).
_ALIASES = {
    "current_delta": ("current_delta", "delta"),
}

_lock = Lock()
_snapshot: list[dict[str, Any]] = []


def _project(state: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for field in _DASHBOARD_FIELDS:
        if field in _ALIASES:
            value = None
            for source in _ALIASES[field]:
                if source in state and state[source] is not None:
                    value = state[source]
                    break
            out[field] = value
        else:
            out[field] = state.get(field)

    # Normalize status casing so the frontend can rely on lowercase enum
    # values ("monitoring" | "triggered" | ...).
    status = out.get("status")
    if isinstance(status, str):
        out["status"] = status.lower()

    return out


def publish_snapshot(states: Iterable[dict[str, Any]]) -> None:
    """Called by the engine at the end of each tick cycle.

    Builds a brand new list of brand new dicts filtered to the
    whitelisted dashboard fields, then atomically replaces storage.
    No references to the engine's `contract_states` entries are kept.
    """
    projected = [_project(s) for s in states]
    with _lock:
        global _snapshot
        _snapshot = projected


def get_engine_snapshot() -> list[dict[str, Any]]:
    """Read-only accessor for consumers (e.g. dashboard router).

    Returns a fresh outer list so callers cannot mutate internal storage.
    """
    with _lock:
        return list(_snapshot)


def clear_snapshot() -> None:
    """Called by the engine controller on stop/reset."""
    with _lock:
        global _snapshot
        _snapshot = []
