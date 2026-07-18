from fastapi import APIRouter

from contract_store import get_contracts

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def get_dashboard():

    dashboard = []

    for c in get_contracts():

        dashboard.append(
            {
                "id": c.id,
                "instrument": c.instrument,
                "expiry": c.expiry,
                "strike": c.strike,
                "optionType": c.option_type,
                "condition": c.trigger_direction,
                "threshold": c.delta_threshold,
                "webhookProfileId": c.webhook_profile_id,
                "spot": c.spot,
                "premium": c.premium,
                "currentDelta": c.delta,
                "status": c.status.lower(),
                "triggered": c.triggered,
                "lastUpdated": None,
            }
        )

    return dashboard