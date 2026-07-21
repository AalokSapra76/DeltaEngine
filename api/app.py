from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.contracts import router as contracts_router
from api.routers.status import router as status_router
from api.routers.instruments import router as instruments_router
from api.routers.dashboard import router as dashboard_router
from api.routers.profiles import router as profiles_router
from api.routers.control import router as control_router
from engine_control.bootstrap import bootstrap_kite

app = FastAPI(

    title="BK Delta Terminal API",

    description="HTTP Bridge for BK Delta Engine",

    version="2.0.0"

)

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)


@app.on_event("startup")
def startup():

    bootstrap_kite()

app.include_router(status_router, prefix="/api/v1")
app.include_router(contracts_router, prefix="/api/v1")
app.include_router(instruments_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(profiles_router, prefix="/api/v1")
app.include_router(control_router, prefix="/api/v1")