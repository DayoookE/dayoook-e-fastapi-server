from datetime import datetime

from fastapi import APIRouter, Depends, Request, UploadFile, HTTPException
from openai import BaseModel

from app.database.model.assistant import *
from app.database.common import *
from app.database.model.lesson_schedule import get_lesson_schedule
from app.database.model.message import *
from app.database.model.thread import *
from app.database.model.user import *
from app.services.chat_gpt_service import ChatGptService
from app.services.user_service import UserService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/review", tags=["review"])


class ReviewResponse(BaseModel):
    content: str


class MessageResponse(BaseModel):
    question: str
    answer: str
    created_at: datetime


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]


class MessageRequest(BaseModel):
    content: str


# 리뷰 어시스턴트 생성
@router.get("/create")
async def create_new_assistant(request: Request,
                               chat_service: ChatGptService = Depends(),
                               user_service: UserService = Depends(),
                               email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        # 1. 새로운 어시스턴트 생성
        review_assistant_id = await chat_service.create_review_assistant()

        # 2. db에 어시스턴트 등록
        create_assistant(Assistant(id=review_assistant_id,
                                   user_id=user_id,
                                   role="review"))
        # 3. 유저에 어시스턴트 등록
        merge_user(User(id=user_id,
                        review_assistant_id=review_assistant_id))

        # 3. 커밋
        commit()

        return user_id
    except Exception as e:

        rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 녹음 스크립트 리뷰 생성
@router.post("/{lesson_schedule_id}")
def create_review(lesson_schedule_id: int,
                  script: UploadFile,
                  request: Request,
                  chat_service: ChatGptService = Depends(),
                  user_service: UserService = Depends(),
                  email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        review_assistant_id = get_assistant_by_userid_and_role(user_id, "review")

        new_thread = await chat_service.create_thread()

        new_vector_store = await chat_service.create_vector_store()

        new_file = await chat_service.create_file(script)

        await chat_service.attach_file_to_vector_store(new_file.id, new_vector_store.id)

        await chat_service.attach_vector_store_to_thread(new_thread.id, new_vector_store.id)

        create_thread(Thread(id=new_thread.id,
                             lesson_schedule_id=lesson_schedule_id,
                             assistant_id=review_assistant_id,
                             vector_store_id=new_vector_store.id))

        new_message = await chat_service.create_message(new_thread.id, None)

        review = await chat_service.create_run(new_thread.id, review_assistant_id)

        commit()

        return ReviewResponse(content=review)

    except Exception as e:
        rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 리뷰 조회
@router.get("/{lesson_schedule_id}", response_model=MessageListResponse)
async def view_review(lesson_schedule_id: int,
                      request: Request,
                      user_service: UserService = Depends(),
                      email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        # 1. user_id와 lesson_schedule_id로 수업일정 조회
        find_lesson_schedule = get_lesson_schedule(user_id, lesson_schedule_id)

        # 2. 수업일정의 복습자료 조회
        review_url = find_lesson_schedule.review_url

        # 3. // 복습자료 다운로드 추후 구현
        review = None

        return ReviewResponse(
            content=review
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
