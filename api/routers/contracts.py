from typing import List
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(
    tags=["Contracts"]
)


class Contract(BaseModel):

    instrument: str

    expiry: str

    strike: float

    option_type: str

    trigger_direction: str

    delta_threshold: float


contracts: List[dict] = []


@router.get("/contracts")
def get_contracts():

    return contracts


@router.post("/contracts")
def add_contract(contract: Contract):

    new_contract = contract.model_dump()

    new_contract["id"] = str(uuid4())

    contracts.append(new_contract)

    return new_contract


@router.delete("/contracts/{contract_id}")
def delete_contract(contract_id: str):

    global contracts

    for contract in contracts:

        if contract["id"] == contract_id:

            contracts.remove(contract)

            return {
                "status": "deleted"
            }

    raise HTTPException(

        status_code=404,

        detail="Contract not found"

    )