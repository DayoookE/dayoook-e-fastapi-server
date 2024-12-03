import os
from typing import List
import pandas as pd
from dotenv import load_dotenv

from fastapi import APIRouter, Depends

from app.schemas.response import TutorRecommendSchema, TutorMatchingDetails, TutorRecommendResultSchema
from app.services.tutor_recommender import TutorRecommender
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/ai", tags=["AI"])
load_dotenv()
FILE = os.getenv('FILE')
tutor_df_path = os.path.join(FILE, 'static', "tutor.csv")
tutee_df_path = os.path.join(FILE, 'static', "tutee.csv")

tutors_df = pd.read_csv(tutor_df_path, header=None)
tutees_df = pd.read_csv(tutee_df_path, header=None)

recommender = TutorRecommender(tutors_df, tutees_df)


@router.get("/recommend/{student_id}", response_model=TutorRecommendResultSchema)
async def recommend(student_id: int):
    recommendations = recommender.get_recommendations(student_id, top_n=5)
    results = []
    for rank, rec in enumerate(recommendations, 1):
        tutor = recommender.tutors[recommender.tutors['ID'] == rec['tutor_id']].iloc[0]
        print(f"\n추천 {rank}순위:")
        print(f"튜터 ID: {tutor['튜터ID']}")
        print(f"매칭 점수: {rec['score']:.2f}")
        print("매칭 상세:")
        tutor_match = TutorMatchingDetails(**rec['matching_details'])

        result = TutorRecommendSchema(
            tutor_id=tutor['튜터ID'],
            score=rec['score'],
            matching_details=tutor_match
        )
        results.append(result)
    return TutorRecommendResultSchema(recommends=results)
