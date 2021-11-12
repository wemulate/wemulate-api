from fastapi import FastAPI
from api.routers.v1 import router as v1_router

app = FastAPI(title="WEmulate API")
app.include_router(v1_router)
