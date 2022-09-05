import uvicorn
from fastapi import FastAPI
from api.routers.v1 import router as v1_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="WEmulate API")
app.include_router(v1_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")


if __name__ == "__main__":
    main()
