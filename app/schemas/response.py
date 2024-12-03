from typing import List

from pydantic import BaseModel, Field


class TutorMatchingDetails(BaseModel):
    language_match: float = Field(..., description="구사 언어 매칭")
    time_match: float = Field(..., description="시간 매칭")
    level_match: float = Field(..., description="수준 매칭")
    rating: float = Field(..., description="평점 반영")
    gender_match: float = Field(..., description="성별 매칭")


class TutorRecommendSchema(BaseModel):
    tutor_id: str = Field(..., description="튜터 id")
    score: float = Field(..., description="매칭 점수")
    matching_details: TutorMatchingDetails = Field(..., description="종합 점수")


class TutorRecommendResultSchema(BaseModel):
    recommends: List[TutorRecommendSchema]

    class Config:
        json_schema_extra = {
            "example": {
                "recommends": [
                    {
                        "tutor_id": "Tutor0436",
                        "score": 0.9924999999999999,
                        "matching_details": {
                            "language_match": 1,
                            "time_match": 1,
                            "level_match": 1,
                            "rating": 0.95,
                            "gender_match": 1
                        }
                    },
                    {
                        "tutor_id": "Tutor0797",
                        "score": 0.98875,
                        "matching_details": {
                            "language_match": 1,
                            "time_match": 1,
                            "level_match": 1,
                            "rating": 0.925,
                            "gender_match": 1
                        }
                    },
                    {
                        "tutor_id": "Tutor0248",
                        "score": 0.985,
                        "matching_details": {
                            "language_match": 1,
                            "time_match": 1,
                            "level_match": 1,
                            "rating": 0.8999999999999999,
                            "gender_match": 1
                        }
                    },
                    {
                        "tutor_id": "Tutor0291",
                        "score": 0.985,
                        "matching_details": {
                            "language_match": 1,
                            "time_match": 1,
                            "level_match": 1,
                            "rating": 0.8999999999999999,
                            "gender_match": 1
                        }
                    },
                    {
                        "tutor_id": "Tutor0545",
                        "score": 0.9774999999999999,
                        "matching_details": {
                            "language_match": 1,
                            "time_match": 1,
                            "level_match": 1,
                            "rating": 0.8500000000000001,
                            "gender_match": 1
                        }
                    }
                ]
            }
        }


class SpeechFeedbackSchema(BaseModel):
    predicted: str = Field(..., description="인식된 발음")
    ground_truth: str = Field(..., description="정답 발음 텍스트")
    confidence: float = Field(..., description="발음 인식 신뢰도")
    feedback: str = Field(..., description="발음 피드백")

    class Config:
        json_schema_extra = {
            "example": {
                "result": {
                    'predicted': '인식된 발음',
                    'ground_truth': '정답 발음 텍스트',
                    'confidence': 0.85,
                    'feedback': '피드백 메시지'
                }
            }
        }
