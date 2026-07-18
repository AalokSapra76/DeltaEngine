from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from contract_model import Contract
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
    optionType: str
    condition: str
    threshold: float
    webhookProfileId: str


@router.get("/contracts")
def list_contracts():
    return [c.to_dict() for c in get_contracts()]


@router.post("/contracts")
def create_contract(req: ContractRequest):

    contract = Contract(
        id=str(uuid4()),
        instrument=req.instrument,
        expiry=req.expiry,
        strike=req.strike,
        option_type=req.optionType,
        trigger_direction=req.condition,
        delta_threshold=req.threshold,
        webhook_profile_id=req.webhookProfileId,
    )

    add_contract(contract)

    return contract.to_dict()


@router.put("/contracts/{contract_id}")
def edit_contract(contract_id: str, req: ContractRequest):

    if get_contract(contract_id) is None:
        raise HTTPException(404, "Contract not found")

    contract = Contract(
        id=contract_id,
        instrument=req.instrument,
        expiry=req.expiry,
        strike=req.strike,
        option_type=req.optionType,
        trigger_direction=req.condition,
        delta_threshold=req.threshold,
        webhook_profile_id=req.webhookProfileId,
    )

    update_contract(contract)

    return contract.to_dict()


@router.delete("/contracts/{contract_id}")
def delete_contract(contract_id: str):

    if remove_contract(contract_id):
        return {"status": "deleted"}

    raise HTTPException(404, "Contract not found")