# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import google_meet_api, welfare_api, chat_gpt_api, clova_api
from app.database.model.common import create_db_and_tables
from app.services.clova_service import ClovaService

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
app.include_router(chat_gpt_api.router)
app.include_router(clova_api.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    create_db_and_tables()

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

