"""
Engine controller.

Owns the lifecycle of the monitoring engine thread. On stop/reset also
clears the dashboard snapshot so consumers immediately fall back to
idle defaults instead of showing stale last-tick data.
"""

from enum import Enum
from threading import Thread

import main
from contract_store import get_contracts
from engine_control.snapshot import clear_snapshot


class EngineState(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


class EngineController:

    def __init__(self):
        self._state = EngineState.STOPPED
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return

        engine_contracts = get_contracts()

        self._thread = Thread(
            target=lambda: main.start_engine(engine_contracts),
            daemon=True,
        )
        self._thread.start()
        self._state = EngineState.RUNNING

    def pause(self):
        self._state = EngineState.PAUSED

    def stop(self):
        self._state = EngineState.STOPPED
        clear_snapshot()

    def reset(self):
        self._state = EngineState.STOPPED
        clear_snapshot()

    def status(self):
        return {
            "state": self._state.value,
            "connected": bool(
                self._thread is not None and self._thread.is_alive()
            ),
            "broker": "kite",
        }


controller = EngineController()
