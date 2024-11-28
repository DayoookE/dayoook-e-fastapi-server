import os

from fastapi import APIRouter, UploadFile, Depends, Request, HTTPException
from openai import OpenAI
from pydantic import BaseModel

from app.database.model.assistant import *
from app.database.model.message import *
from app.database.model.thread import *
from app.database.model.common import *

from app.services.chat_gpt_service import ChatGptService
from app.services.user_service import UserService
from app.utils.security import get_current_user

UPLOAD_DIR = os.getenv('UPLOAD_DIR')
router = APIRouter(prefix="/api/chat", tags=["chat"])
client = OpenAI()


class MessageResponse(BaseModel):
    question: str
    answer: str
    created_at: datetime


class DialogueResponse(BaseModel):
    messages: List[MessageResponse]


class MessageRequest(BaseModel):
    question: str


# ChatGPT Assistant 생성 (튜티 당 하나씩 생성)
@router.get("/assistant")
async def create_new_assistant(request: Request,
                               service: ChatGptService = Depends(),
                               email: str = Depends(get_current_user)):
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        # UserService를 사용해 사용자 정보 가져오기
        user_info = UserService.get_user_info(token)

        # 사용자 id 추출
        user_id = user_info['result']['id']

        # 1. 새로운 어시스턴트 생성
        assistant_id = await service.create_assistant()

        # 2. db에 어시스턴트 등록
        create_assistant(Assistant(id=assistant_id, user_id=user_id))

        # 3. 커밋
        commit()

        return assistant_id
    except Exception as e:

        rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 대화 목록 불러오기
@router.get("/{lesson_schedule_id}", response_model=DialogueResponse)
async def show_dialogue(request: Request,
                        lesson_schedule_id: int,
                        service: ChatGptService = Depends(),
                        email: str = Depends(get_current_user)):
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        # UserService를 사용해 사용자 정보 가져오기
        user_info = UserService.get_user_info(token)

        # 사용자 id 추출
        user_id = user_info['result']['id']

        # 1. user_id로 assistant_id 조회
        assistant = get_assistant(user_id)

        # 2. lesson_schedule_id로 thread 조회
        thread = get_thread(lesson_schedule_id)

        # 3. 스레드에 등록된 모든 메시지 가져오기
        messages = get_messages_by_thread_id(thread.id)

        # 4. messages -> List[MessageResponse]
        message_responses = [MessageResponse(question=m.question, answer=m.answer,
                                             created_at=m.created_at) for m in messages]
        return DialogueResponse(
            messages=message_responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 수업이 끝난 후 복습 페이지 생성
@router.post("/{lesson_schedule_id}")
async def create_page(request: Request,
                      lesson_schedule_id: int,
                      file: UploadFile,
                      service: ChatGptService = Depends(),
                      email: str = Depends(get_current_user)):
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        # UserService를 사용해 사용자 정보 가져오기
        user_info = UserService.get_user_info(token)

        # 사용자 id 추출
        user_id = user_info['result']['id']

        # 1. user_id로 assistant 조회
        assistant = get_assistant(user_id)
        print(assistant)

        # 2. 새 스레드 생성
        thread_id = await service.create_thread()
        print(thread_id)

        # 3. 새로운 vector store 생성
        vector_store_id = await service.create_vector_store()
        print(vector_store_id)

        # 3. 파일 생성
        file_id = await service.create_file(file)
        print(file_id)

        # 4. vector store에 파일 업로드
        await service.attach_file_to_vector_store(file_id, vector_store_id)
        print("complete")

        # 5. thread에 vector store attach
        await service.attach_vector_store_to_thread(thread_id, vector_store_id)
        print("complete")

        # 6. db에 스레드 등록
        create_thread(Thread(id=thread_id, vector_store_id=vector_store_id,
                             lesson_schedule_id=lesson_schedule_id, assistant_id=assistant.id))
        print("complete")

        # 7. 커밋
        commit()

        return thread_id

    except Exception as e:
        rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 챗봇 대화 기능
@router.post("/{lesson_schedule_id}/message", response_model=MessageResponse)
async def send_message(request: Request,
                       lesson_schedule_id: int,
                       message: MessageRequest,
                       service: ChatGptService = Depends(),
                       email: str = Depends(get_current_user)):
    token = request.headers.get("Authorization")

    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        # UserService를 사용해 사용자 정보 가져오기
        user_info = UserService.get_user_info(token)

        # 사용자 id 추출
        user_id = user_info['result']['id']

        # 1. user_id로 assistant 조회
        assistant = get_assistant(user_id)
        print(assistant)

        # 2. 활성된 thread 조회
        thread = get_thread(lesson_schedule_id)
        print(thread)

        # 3. 메시지 생성
        message_id = await service.create_message(thread.id, message.question)
        print(message_id)

        # 4. run
        answer = await service.create_run(thread.id, assistant.id)
        print(answer)

        # 5. db에 메시지 저장
        create_message(Message(id=message_id, question=message.question, answer=answer, thread_id=thread.id))

        # 6. 커밋
        commit()

        return MessageResponse(
            question=message.question,
            answer=answer,
            created_at=get_message(message_id).created_at
        )

    except Exception as e:
        rollback()
        raise HTTPException(status_code=500, detail=str(e))
