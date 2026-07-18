from typing import Dict, List

from contract_model import Contract


_contracts: Dict[str, Contract] = {}


def get_contracts() -> List[Contract]:
    return list(_contracts.values())


def get_contract(contract_id: str) -> Contract | None:
    return _contracts.get(contract_id)


def add_contract(contract: Contract) -> Contract:
    _contracts[contract.id] = contract
    return contract


def update_contract(contract: Contract) -> Contract:
    _contracts[contract.id] = contract
    return contract


def remove_contract(contract_id: str) -> bool:
    return _contracts.pop(contract_id, None) is not None


def clear_contracts() -> None:
    _contracts.clear()