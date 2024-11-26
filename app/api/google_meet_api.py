# app/api/google_meet_api.py
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime
from app.services.google_meet_service import GoogleMeetService
from app.services.user_service import UserService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/meet", tags=["meet"])


class MeetingResponse(BaseModel):
    meeting_uri: str
    created_at: str
    status: str


@router.post("/create", response_model=MeetingResponse)
async def create_meeting(
        request: Request,
        service: GoogleMeetService = Depends(),
        email: str = Depends(get_current_user)):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        # UserService를 사용해 사용자 정보 가져오기, 토큰을 헤더에 포함
        user_info = UserService.get_user_info(token)
        # 사용자 정보를 출력하거나 추가 로직 작성 가능
        user_id = user_info['result']['id']
        user_role = user_info['result']['role']
        print(user_id)
        print(user_role)

       # meeting = await service.create_meeting()
        return MeetingResponse(
            meeting_uri="meeting",
            created_at=datetime.now().isoformat(),
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))