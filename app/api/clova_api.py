"""
복습 자료 생성을 위해 수업 녹음을 텍스트로 변환하는 ClOVA Speech API
"""
import json
import os
import uuid
from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, Request, UploadFile, HTTPException
from pydantic import BaseModel

from app.database.common import rollback, commit
from app.database.model.lesson_schedule import get_lesson_schedule, merge_lesson_schedule, LessonSchedule, \
    get_lesson_schedule_by_userid
from app.s3.connection import download_from_s3, upload_to_s3
from app.services.clova_service import ClovaService
from app.services.user_service import UserService
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/speech", tags=["speech"])
script_upload_dir = os.getenv("S3_SCRIPT_UPLOAD_DIR")
record_upload_dir = os.getenv("S3_RECORD_UPLOAD_DIR")
bucket_name = os.getenv("S3_BUCKET_NAME")


class Dialogue(BaseModel):
    label: str
    text: str


class Dialogues(BaseModel):
    content: List[Dialogue]


@router.post("/{lesson_schedule_id}/upload")
async def upload_records(request: Request,
                         file: UploadFile,
                         lesson_schedule_id: str,
                         user_service: UserService = Depends(),
                         email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        lesson_schedule = get_lesson_schedule_by_userid(lesson_schedule_id, user_id)
        if lesson_schedule is None:
            lesson_schedule = merge_lesson_schedule(LessonSchedule(id=lesson_schedule_id,
                                                                   user_id=user_id))

        audio_file_name = str(uuid.uuid4())
        bytes_io = BytesIO(await file.read())
        audio_url = upload_to_s3(bytes_io, bucket_name, record_upload_dir + "/" + audio_file_name)
        lesson_schedule.audio_url = audio_url

        commit()

        return audio_url

    except Exception as e:

        rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{lesson_schedule_id}/transcription", response_model=Dialogues)
async def make_dialogue(request: Request,
                        lesson_schedule_id: int,
                        user_service: UserService = Depends(),
                        clova_service: ClovaService = Depends(),
                        email: str = Depends(get_current_user)):
    try:
        token = request.headers.get("Authorization")
        user_id = user_service.get_user_id(token)

        lesson_schedule = get_lesson_schedule_by_userid(lesson_schedule_id, user_id)
        audio_url = lesson_schedule.audio_url

        response = await clova_service.speech_to_text(audio_url)
        segments = response["segments"]

        dialogues = [Dialogue(label=s["speaker"]["label"], text=s["textEdited"]) for s in segments]

        script_file_name = str(uuid.uuid4())
        script_url = upload_to_s3(BytesIO(str(dialogues).encode('utf-8')), bucket_name, script_upload_dir +"/"+ script_file_name)
        lesson_schedule.dialogue_url = script_url

        commit()

        return Dialogues(
            content=dialogues
        )
    except Exception as e:

        rollback()
        raise HTTPException(status_code=500, detail=str(e))


def make_dialogue_test(service: ClovaService = Depends()):
    file = "C:/Users/82109/Desktop/dayoook-e-fastapi-server/uploads/test_audio.m4a"
    response = service.speech_to_text_local(file)
    segments = response["segments"]
    dialogues = [Dialogue(label=s["speaker"]["label"], text=s["textEdited"], ) for s in segments]
    return Dialogues(
        content=dialogues
    )
