# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import google_meet_api, welfare_api

app = FastAPI(title="Dayook API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(google_meet_api.router)
app.include_router(welfare_api.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)