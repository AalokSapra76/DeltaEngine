from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from contract_store import (
    add_contract,
    get_contracts,
    remove_contract,
)


router = APIRouter(tags=["Contracts"])


class Contract(BaseModel):
    instrument: str
    expiry: str
    strike: float
    option_type: str
    trigger_direction: str
    delta_threshold: float


@router.get("/contracts")
def list_contracts():
    return get_contracts()


@router.post("/contracts")
def create_contract(contract: Contract):

    new_contract = contract.model_dump()

    new_contract["id"] = str(uuid4())

    add_contract(new_contract)

    return new_contract


@router.delete("/contracts/{contract_id}")
def delete_contract(contract_id: str):

    if remove_contract(contract_id):

        return {
            "status": "deleted"
        }

    raise HTTPException(
        status_code=404,
        detail="Contract not found"
    )