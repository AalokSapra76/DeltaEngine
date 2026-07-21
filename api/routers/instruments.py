from fastapi import APIRouter, HTTPException

from engine_control.instrument_cache import get_instruments as get_cached_instruments

router = APIRouter(tags=["Instruments"])


@router.get("/instruments")
def get_instruments():
    instruments = get_cached_instruments()
    if not instruments:
        raise HTTPException(503, "Instrument cache not initialized. Start the engine first.")

    symbols = sorted({i["name"] for i in instruments if i.get("segment") == "NFO-OPT"})
    return symbols


@router.get("/instruments/{instrument}/expiries")
def get_expiries(instrument: str):
    instruments = get_cached_instruments()
    if not instruments:
        raise HTTPException(503, "Instrument cache not initialized. Start the engine first.")

    instrument = instrument.upper()
    expiries = sorted({
        str(i["expiry"])
        for i in instruments
        if i.get("segment") == "NFO-OPT" and i.get("name") == instrument
    })

    if not expiries:
        raise HTTPException(404, "Instrument not found")

    return expiries


@router.get("/instruments/{instrument}/expiries/{expiry}/strikes")
def get_strikes(instrument: str, expiry: str):
    instruments = get_cached_instruments()
    if not instruments:
        raise HTTPException(503, "Instrument cache not initialized. Start the engine first.")

    instrument = instrument.upper()

    strikes = sorted({
        int(i["strike"])
        for i in instruments
        if i.get("segment") == "NFO-OPT"
        and i.get("name") == instrument
        and str(i.get("expiry")) == expiry
    })

    if not strikes:
        raise HTTPException(404, "Expiry not found")

    return strikes
