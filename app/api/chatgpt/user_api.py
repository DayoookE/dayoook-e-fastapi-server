from fastapi import APIRouter, Request, HTTPException
from openai import BaseModel

from app.database.common import commit, rollback
from app.database.model.user import User, create_user

router = APIRouter(prefix="/api/user", tags=["user"])


class CreateUserRequest(BaseModel):
    id: int
    chat_assistant_id: str
    review_assistant_id: str


# 리뷰 어시스턴트 생성
@router.post("/create", status_code=201)
async def create_new_user(request: CreateUserRequest):
    try:
        user = User(id=request.id,
                    chat_assistant_id=request.chat_assistant_id,
                    review_assistant_id=request.review_assistant_id)

        create_user(user)
        commit()

    except Exception as e:
        rollback()
        raise HTTPException(status_code=500, detail=str(e))
