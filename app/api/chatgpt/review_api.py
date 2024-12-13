import uuid
from datetime import datetime
from io import BytesIO
from tempfile import TemporaryFile, NamedTemporaryFile

from fastapi import APIRouter, Depends, Request, UploadFile, HTTPException
from openai import BaseModel

from app.api.chatgpt.converter import bytesio_to_uploadfile
from app.database.model.assistant import *
from app.database.common import *
from app.database.model.lesson_schedule import get_lesson_schedule, get_lesson_schedules
from app.database.model.message import *
from app.database.model.thread import *
from app.database.model.user import *
from app.s3.connection import download_from_s3
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

        # 0. db에 유저 등록
        current_user = get_user(user_id)
        if current_user is None:
            create_user(User(id=user_id))
            current_user = get_user(user_id)

        # 1. 새로운 어시스턴트 생성
        review_assistant_id = await chat_service.create_review_assistant()

        # 2. db에 어시스턴트 등록
        create_assistant(Assistant(id=review_assistant_id,
                                   user_id=user_id,
                                   role="review"))
        # 3. 유저에 어시스턴트 등록
        current_user.review_assistant_id = review_assistant_id
        merge_user(current_user)

        # 3. 커밋
        commit()

        return user_id
    except Exception as e:

        rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 녹음 스크립트 리뷰 생성
@router.post("/{lesson_schedule_id}")
async def create_review(lesson_schedule_id: int,
                        request: Request,
                        chat_service: ChatGptService = Depends(),
                        user_service: UserService = Depends(),
                        email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        find_assistant = get_assistant_by_userid_and_role(user_id, "review")

        new_thread_id = await chat_service.create_thread()

        new_vector_store_id = await chat_service.create_vector_store()

        find_lesson_schedule = get_lesson_schedule(lesson_schedule_id, user_id)
        file_bytes = download_from_s3(find_lesson_schedule.dialogue_url)

        script_file_bytes = download_from_s3(find_lesson_schedule.dialogue_url)
        script_file_bytes.name = str(uuid.uuid4()) + ".txt"
        new_file_id = await chat_service.create_file(script_file_bytes)

        await chat_service.attach_file_to_vector_store(new_file_id, new_vector_store_id)

        await chat_service.attach_vector_store_to_thread(new_thread_id, new_vector_store_id)

        create_thread(Thread(id=new_thread_id,
                             lesson_schedule_id=lesson_schedule_id,
                             assistant_id=find_assistant.id,
                             vector_store_id=new_vector_store_id))

        new_message = await chat_service.create_message(new_thread_id, "요약본을 생성해줘.")

        review = await chat_service.create_run(new_thread_id, find_assistant.id)

        find_lesson_schedule.review = review

        commit()

        return ReviewResponse(content=review)

    except Exception as e:
        rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 리뷰 조회
@router.get("/{lesson_schedule_id}", response_model=ReviewResponse)
async def view_review(lesson_schedule_id: int,
                      request: Request,
                      user_service: UserService = Depends(),
                      email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        # 1. user_id와 lesson_schedule_id로 수업일정 조회
        find_lesson_schedule = get_lesson_schedule(lesson_schedule_id, user_id)
        print(user_id, lesson_schedule_id, find_lesson_schedule)

        # 2. 수업일정의 복습자료 조회
        review = find_lesson_schedule.review

        return ReviewResponse(
            content=review
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{lesson_schedule_id}/complete")
async def complete_review(lesson_schedule_id: int,
                          request: Request,
                          user_service: UserService = Depends(),
                          email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        # 1. user_id와 lesson_schedule_id로 수업일정 조회
        find_lesson_schedule = get_lesson_schedule(lesson_schedule_id, user_id)

        # 2. 복습 완료 반영
        find_lesson_schedule.review_completed = True

        # 3. commit
        commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rate/{user_id}")
async def get_review_rate(request: Request,
                          user_service: UserService = Depends(),
                          email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        # 1. user_id로 수업 일정 모두 조회
        lesson_schedules = get_lesson_schedules(user_id)

        # 2. 완성된 수업 일정 count
        finished_count = 0
        finished_count += sum(1 for ls in lesson_schedules if ls.review_completed)

        # 3. 진행된 수업 일정 count
        schedule_count = len(lesson_schedules)

        # 4. 복습률 계산
        review_rate = 100 * finished_count // schedule_count

        return review_rate

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
