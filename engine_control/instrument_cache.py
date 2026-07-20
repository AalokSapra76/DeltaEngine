"""
Shared instrument cache.

The monitoring engine refreshes this cache from Kite.
The FastAPI instrument router serves metadata from here.

This module is intentionally simple: it owns no Kite
connection and performs no downloads.
"""

from typing import List, Dict, Any

_instruments: List[Dict[str, Any]] = []


def set_instruments(instruments: List[Dict[str, Any]]) -> None:
    """Replace the cached instrument master."""
    global _instruments
    _instruments = instruments


def get_instruments() -> List[Dict[str, Any]]:
    """Return the cached instrument master."""
    return _instruments


def clear_instruments() -> None:
    """Clear the cache."""
    global _instruments
    _instruments = []