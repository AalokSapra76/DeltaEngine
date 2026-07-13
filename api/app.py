from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.contracts import router as contracts_router
from api.routers.status import router as status_router


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

app.include_router(status_router, prefix="/api/v1")
app.include_router(contracts_router, prefix="/api/v1")