"""
Contracts router.

Accepts and returns the canonical snake_case contract dict — same shape
the monitoring engine and console source use. No dataclass, no camelCase
translation layer.
"""

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from contract_store import (
    add_contract,
    get_contract,
    get_contracts,
    remove_contract,
    update_contract,
)

router = APIRouter(tags=["Contracts"])


class ContractRequest(BaseModel):
    instrument: str
    expiry: str
    strike: float
    option_type: str
    trigger_direction: str
    delta_threshold: float
    webhook_profile_id: str = ""


def _to_dict(req: ContractRequest, contract_id: str) -> dict:
    return {
        "id": contract_id,
        "instrument": req.instrument,
        "expiry": req.expiry,
        "strike": req.strike,
        "option_type": req.option_type,
        "trigger_direction": req.trigger_direction,
        "delta_threshold": req.delta_threshold,
        "webhook_profile_id": req.webhook_profile_id,
    }


@router.get("/contracts")
def list_contracts():
    return get_contracts()


@router.post("/contracts")
def create_contract(req: ContractRequest):
    contract = _to_dict(req, str(uuid4()))
    add_contract(contract)
    return contract


@router.put("/contracts/{contract_id}")
def edit_contract(contract_id: str, req: ContractRequest):
    if get_contract(contract_id) is None:
        raise HTTPException(404, "Contract not found")
    contract = _to_dict(req, contract_id)
    update_contract(contract)
    return contract


@router.delete("/contracts/{contract_id}")
def delete_contract(contract_id: str):
    if remove_contract(contract_id):
        return {"status": "deleted"}
    raise HTTPException(404, "Contract not found")
