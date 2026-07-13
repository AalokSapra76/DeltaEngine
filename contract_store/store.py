from typing import List


_contracts: List[dict] = []


def get_contracts() -> List[dict]:
    return _contracts


def add_contract(contract: dict) -> dict:
    _contracts.append(contract)
    return contract


def remove_contract(contract_id: str) -> bool:
    for contract in _contracts:
        if contract["id"] == contract_id:
            _contracts.remove(contract)
            return True
    return False


def clear_contracts() -> None:
    _contracts.clear()