from datetime import datetime

from fastapi import APIRouter, Depends, Request, UploadFile, HTTPException
from openai import BaseModel

from app.database.model.assistant import *
from app.database.common import *
from app.database.model.message import *
from app.database.model.thread import *
from app.database.model.user import *
from app.services.chat_gpt_service import ChatGptService
from app.services.user_service import UserService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat"])


class MessageResponse(BaseModel):
    question: str
    answer: str
    created_at: datetime


class MessageListResponse(BaseModel):
    messages: List[MessageResponse]


class MessageRequest(BaseModel):
    content: str


# 챗 어시스턴트 생성
@router.get("/create")
async def create_new_assistant(request: Request,
                               chat_service: ChatGptService = Depends(),
                               user_service: UserService = Depends(),
                               email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        # 1. 새로운 어시스턴트 생성
        chat_assistant_id = await chat_service.create_chat_assistant()

        # 2. db에 어시스턴트 등록
        create_assistant(Assistant(id=chat_assistant_id,
                                   user_id=user_id,
                                   role="chat"))
        # 3. 유저에 어시스턴트 등록
        merge_user(User(id=user_id,
                        chat_assistant_id=chat_assistant_id))

        # 3. 커밋
        commit()

        return user_id
    except Exception as e:

        rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 챗봇 생성
@router.post("/{lesson_schedule_id}")
async def create_chat(lesson_schedule_id: int,
                file: UploadFile,
                request: Request,
                chat_service: ChatGptService = Depends(),
                user_service: UserService = Depends(),
                email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        chat_assistant_id = get_assistant_by_userid_and_role(user_id, "chat")

        new_thread = await chat_service.create_thread()

        new_vector_store = await chat_service.create_vector_store()

        new_file = await chat_service.create_file(file)

        await chat_service.attach_file_to_vector_store(new_file.id, new_vector_store.id)

        await chat_service.attach_vector_store_to_thread(new_thread.id, new_vector_store.id)

        create_thread(Thread(id=new_thread.id,
                             lesson_schedule_id=lesson_schedule_id,
                             assistant_id=chat_assistant_id,
                             vector_store_id=new_vector_store.id))

        commit()

        return new_thread.id

    except Exception as e:
        rollback()
        raise HTTPException(status_code=500, detail=str(e))


# 대화 불러오기
@router.get("/{lesson_schedule_id}", response_model=MessageListResponse)
async def show_dialogue(lesson_schedule_id: int,
                        request: Request,
                        user_service: UserService = Depends(),
                        email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        # 1. user_id로 chat_assistant 조회
        chat_assistant = get_assistant_by_userid_and_role(user_id, "chat")

        # 2. assistant_id와 lesson_schedule_id로 thread 조회
        thread = get_thread(chat_assistant.id, lesson_schedule_id)

        # 3. 스레드에 등록된 모든 메시지 가져오기
        messages = get_messages_by_thread_id(thread.id)

        # 4. messages -> List[MessageResponse]
        message_responses = [MessageResponse(question=m.question, answer=m.answer,
                                             created_at=m.created_at) for m in messages]

        return MessageListResponse(
            messages=message_responses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 챗봇 대화 기능
@router.post("/{lesson_schedule_id}/message", response_model=MessageResponse)
async def send_message(lesson_schedule_id: int,
                       request: Request,
                       message: MessageRequest,
                       chat_service: ChatGptService = Depends(),
                       user_service: UserService = Depends(),
                       email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        # 1. user_id로 assistant 조회
        chat_assistant = get_assistant_by_userid_and_role(user_id, "chat")

        # 2. 활성된 thread 조회
        thread = get_thread(chat_assistant.id, lesson_schedule_id)

        # 3. 메시지 생성
        message_id = await chat_service.create_message(thread.id, message.content)

        # 4. run
        answer = await chat_service.create_run(thread.id, chat_assistant.id)

        # 5. db에 메시지 저장
        create_message(Message(id=message_id, question=message.content, answer=answer, thread_id=thread.id))

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
