# app/api/google_meet_api.py
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime
from app.services.google_meet_service import GoogleMeetService
from app.services.user_service import UserService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/meet", tags=["meet"])


class CreateMeetingRequest(BaseModel):
    tutor_email: str
    tutee_email: str


class MeetingResponse(BaseModel):
    meeting_uri: str
    created_at: str
    status: str
    event_id: str


@router.post("/create", response_model=MeetingResponse)
async def create_meeting(
        request: Request,
        meeting_request: CreateMeetingRequest,
        service: GoogleMeetService = Depends(),
        email: str = Depends(get_current_user)):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        user_info = UserService.get_user_info(token)
        user_id = user_info['result']['id']
        user_role = user_info['result']['role']

        meeting = await service.create_meeting(meeting_request.tutor_email, meeting_request.tutee_email)

        return MeetingResponse(
            meeting_uri=meeting["meeting_uri"],
            event_id=meeting["event_id"],
            created_at=datetime.now().isoformat(),
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))