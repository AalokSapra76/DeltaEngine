from enum import Enum
from threading import Thread

import main
from contract_store import get_contracts


class EngineState(str, Enum):
    STOPPED = "Stopped"
    RUNNING = "Running"
    PAUSED = "Paused"


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

    def reset(self):
        self._state = EngineState.STOPPED

    def status(self):
        return {
            "state": self._state.value.lower(),
            "connected": self._thread is not None and self._thread.is_alive(),
            "broker": "kite",
        }


controller = EngineController()