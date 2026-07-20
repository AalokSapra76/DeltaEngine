"""
Status router.

Delegates to the engine controller — never returns hardcoded values.
The frontend `EngineStatus` type consumes {state, connected, broker}.
"""

from fastapi import APIRouter

from engine_control import controller

router = APIRouter(tags=["Status"])


@router.get("/")
def root():
    return {
        "application": "BK Delta Terminal",
        "version": "2.0",
    }


@router.get("/status")
def status():
    return controller.status()
