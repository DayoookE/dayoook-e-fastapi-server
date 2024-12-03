"""
복습 자료 생성을 위해 수업 녹음을 텍스트로 변환하는 ClOVA Speech API
"""
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.clova_service import ClovaService

router = APIRouter(prefix="/api/speech", tags=["speech"])


class Dialogue(BaseModel):
    label: str
    text: str


class Dialogues(BaseModel):
    content: List[Dialogue]


@router.post("/transcription", response_model=Dialogues)
async def make_dialogue(url: str,
                        service: ClovaService = Depends()):
    response = await service.speech_to_text(url)
    segments = response["segments"]
    dialogues = [Dialogue(label=s["speaker"]["label"], text=s["textEdited"], ) for s in segments]
    return Dialogues(
        content=dialogues
    )


def make_dialogue_test(service: ClovaService = Depends()):
    file = "C:/Users/82109/Desktop/dayoook-e-fastapi-server/uploads/test_audio.m4a"
    response = service.speech_to_text_local(file)
    segments = response["segments"]
    dialogues = [Dialogue(label=s["speaker"]["label"], text=s["textEdited"], ) for s in segments]
    return Dialogues(
        content=dialogues
    )
