# app/api/google_meet_api.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from app.services.google_meet_service import GoogleMeetService

router = APIRouter(prefix="/api/meet", tags=["meet"])


class MeetingResponse(BaseModel):
    meeting_uri: str
    created_at: str
    status: str


@router.post("/create", response_model=MeetingResponse)
async def create_meeting(service: GoogleMeetService = Depends()):
    try:
        meeting = await service.create_meeting()
        return MeetingResponse(
            meeting_uri=meeting["meeting_uri"],
            created_at=datetime.now().isoformat(),
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))