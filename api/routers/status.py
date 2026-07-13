from fastapi import APIRouter

router = APIRouter(
    tags=["Status"]
)


@router.get("/")
def root():
    return {
        "application": "BK Delta Terminal",
        "engine": "Delta Engine",
        "status": "online",
        "version": "2.0"
    }


@router.get("/status")
def status():

    return {

        "running": False,

        "kite": "disconnected",

        "contracts": 0,

        "market": "closed",

        "version": "2.0"

    }