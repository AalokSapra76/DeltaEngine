from enum import Enum


class EngineState(str, Enum):

    STOPPED = "Stopped"

    RUNNING = "Running"

    PAUSED = "Paused"


class EngineController:

    def __init__(self):

        self._state = EngineState.STOPPED

    def start(self):

        self._state = EngineState.RUNNING

    def pause(self):

        self._state = EngineState.PAUSED

    def stop(self):

        self._state = EngineState.STOPPED

    def reset(self):

        self._state = EngineState.STOPPED

    def status(self):

        return {

            "state": self._state,

            "running": self._state == EngineState.RUNNING

        }


controller = EngineController()