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
    owner_id: str


@router.post("/create", response_model=MeetingResponse)
async def create_meeting(
        request: Request,
        service: GoogleMeetService = Depends(),
        email: str = Depends(get_current_user)):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        # UserService를 사용해 사용자 정보 가져오기
        user_info = UserService.get_user_info_by_email(email, token)
        user_id = user_info['result']['id']
        user_role = user_info['result']['role']

        # TUTEE인 경우 방 생성 불가능
        if user_role == "TUTEE":
            raise HTTPException(
                status_code=403,
                detail="Tutees are not allowed to create meetings"
            )

        # user_id를 기반으로 고유한 credentials 파일 경로 생성
        credentials_path = f"credentials_{user_id}.json"

        # 미팅 생성 시 owner_id와 credentials_path 전달
        meeting = await service.create_meeting(
            owner_id=user_id,
            credentials_path=credentials_path
        )

        return MeetingResponse(
            meeting_uri=meeting["meeting_uri"],
            created_at=datetime.now().isoformat(),
            status="success",
            owner_id=user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))