"""
Plain-dict contract store — single canonical shape shared by:
  - api/routers/contracts.py       (HTTP -> store)
  - contract_source/console.py     (console wizard -> store)
  - main.py                         (store -> engine tick loop)

No dataclass. No camelCase translation layer. The dict IS the contract.

Canonical keys:

    id                   : str      (auto-assigned on insert if missing/None)
    instrument           : str      ("NIFTY" | "BANKNIFTY" | "FINNIFTY")
    expiry               : str      ("YYYY-MM-DD")
    strike               : float
    option_type          : str      ("CE" | "PE")
    trigger_direction    : str      (">" | "<")   -- enforced by engine
    delta_threshold      : float
    webhook_profile_id   : str      (UI-only; engine ignores)

Console wizard sets id=None; store fills in a uuid on insert so both
paths (HTTP + console) produce uniquely keyed rows without either side
knowing about the other.
"""

from typing import Dict, List, Optional
from uuid import uuid4


Contract = Dict[str, object]


_contracts: "Dict[str, Contract]" = {}


def get_contracts() -> List[Contract]:
    return list(_contracts.values())


def get_contract(contract_id: str) -> Optional[Contract]:
    return _contracts.get(contract_id)


def add_contract(contract: Contract) -> Contract:
    cid = contract.get("id")
    if not cid:
        cid = str(uuid4())
        contract["id"] = cid
    _contracts[cid] = contract
    return contract


def update_contract(contract: Contract) -> Contract:
    cid = contract.get("id")
    if not cid:
        raise ValueError("update_contract requires contract['id']")
    _contracts[cid] = contract
    return contract


def remove_contract(contract_id: str) -> bool:
    return _contracts.pop(contract_id, None) is not None


def clear_contracts() -> None:
    _contracts.clear()
