from dataclasses import dataclass
from typing import Optional, List

from pydantic import BaseModel, Field


@dataclass
class PronunciationFeedback:
    predicted_text: str
    avg_confidence: float
    low_confidence_parts: List[str]
    reference_text: Optional[str]
    wer: Optional[float]
    cer: Optional[float]


class TutorRecommendRequest(BaseModel):
    language: List[str] = Field(..., description="구사 언어")
    preferred_time: List[str] = Field(..., description="선호 시간대")
    preferred_day: List[str] = Field(..., description="선호 요일")
    level: str = Field(..., description="한국어 구사 수준")
    gender: str = Field(..., description="성별")
