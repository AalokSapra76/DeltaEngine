from fastapi import APIRouter

from contract_store import get_contracts

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def get_dashboard():

    dashboard = []

    for c in get_contracts():

        dashboard.append(
            {
                "id": c["id"],
                "instrument": c["instrument"],
                "expiry": c["expiry"],
                "strike": c["strike"],
                "optionType": c["optionType"],
                "condition": c["condition"],
                "threshold": c["threshold"],
                "webhookProfileId": c["webhookProfileId"],
                "spot": None,
                "premium": None,
                "currentDelta": None,
                "status": "idle",
                "triggered": False,
                "lastUpdated": None,
            }
        )

    return dashboard