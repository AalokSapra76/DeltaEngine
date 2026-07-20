from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Instruments"])


INSTRUMENTS = {
    "NIFTY": {
        "2026-07-21": [
            24000,
            24050,
            24100,
            24150,
            24200,
            24250,
            24300,
            24350,
            24400,
            24450,
            24500,
        ]
    },
    "BANKNIFTY": {
        "2026-07-16": [
            56000,
            56100,
            56200,
            56300,
            56400,
            56500,
        ]
    },
    "FINNIFTY": {
        "2026-07-14": [
            27000,
            27050,
            27100,
            27150,
            27200,
        ]
    },
}


@router.get("/instruments")
def get_instruments():
    return list(INSTRUMENTS.keys())


@router.get("/instruments/{instrument}/expiries")
def get_expiries(instrument: str):

    instrument = instrument.upper()

    if instrument not in INSTRUMENTS:
        raise HTTPException(404, "Instrument not found")

    return list(INSTRUMENTS[instrument].keys())


@router.get("/instruments/{instrument}/expiries/{expiry}/strikes")
def get_strikes(instrument: str, expiry: str):

    instrument = instrument.upper()

    if instrument not in INSTRUMENTS:
        raise HTTPException(404, "Instrument not found")

    expiries = INSTRUMENTS[instrument]

    if expiry not in expiries:
        raise HTTPException(404, "Expiry not found")

    return expiries[expiry]