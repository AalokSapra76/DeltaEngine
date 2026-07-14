from fastapi import APIRouter

from engine_control import controller

router = APIRouter(tags=["Engine Control"])


@router.post("/start")
def start_engine():
    controller.start()
    return controller.status()


@router.post("/stop")
def stop_engine():
    controller.stop()
    return controller.status()


@router.post("/pause")
def pause_engine():
    controller.pause()
    return controller.status()


@router.post("/reset")
def reset_engine():
    controller.reset()
    return controller.status()