# app/main.py
from contextlib import asynccontextmanager
from app.api.ai_api import init_ai_api

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import google_meet_api, welfare_api, ai_api
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_ai_api()
    yield


app = FastAPI(title="DaYookE API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(google_meet_api.router)
app.include_router(welfare_api.router)
app.include_router(ai_api.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
