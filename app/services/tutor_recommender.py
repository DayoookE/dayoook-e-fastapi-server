import pandas as pd
import numpy as np
from typing import List, Dict

from app.schemas.models import TutorRecommendRequest


class TutorRecommender:
    def __init__(self, tutors_df: pd.DataFrame):
        # 칼럼명 지정
        tutor_columns = ['ID', '튜터명', '나이', '성별', '구사 언어', '한국어수준', '평점', '선호요일', '선호시간']

        self.tutors = tutors_df
        self.tutors.columns = tutor_columns

        # 가중치 설정
        self.weights = {
            'language_match': 0.3,
            'time_match': 0.25,
            'level_match': 0.2,
            'rating': 0.15,
            'gender_match': 0.1
        }

    def _calculate_language_score(self, tutor_languages: str, tutee_language: str) -> float:
        """언어 매칭 점수 계산"""
        tutor_langs = [lang.strip() for lang in tutor_languages.split(',')]
        return 1.0 if tutee_language in tutor_langs else 0.0

    def _calculate_time_score(self, tutor_time: str, tutor_day: str,
                              tutee_time: str, tutee_day: str) -> float:
        """시간대 매칭 점수 계산"""
        # 요일 매칭
        if tutor_day != tutee_day:
            return 0.0

        # 시간대 매칭
        tutor_times = set(t.strip() for t in tutor_time.split(','))
        tutee_times = set(t.strip() for t in tutee_time.split(','))

        common_times = tutor_times.intersection(tutee_times)
        if not common_times:
            return 0.0

        return len(common_times) / len(tutee_times)

    def _calculate_level_score(self, tutor_level: str, tutee_level: str) -> float:
        """수준 매칭 점수 계산"""
        tutor_level_map = {'BEGINNER': 1, 'INTERMEDIATE': 2, 'ADVANCE': 3}
        tutee_level_map = {'초급': 1, '중급': 2, '고급': 3}
        tutor_level_num = tutor_level_map[tutor_level]
        tutee_level_num = tutee_level_map[tutee_level]

        if tutor_level_num >= tutee_level_num:
            return 1.0
        return 0.5

    def _normalize_rating(self, rating: float) -> float:
        """평점 정규화 (1-5점 scale)"""
        return (rating - 1) / 4

    def get_recommendations(self, request: TutorRecommendRequest, top_n: int = 5) -> List[Dict]:
        recommendations = []

        for _, tutor in self.tutors.iterrows():
            # 각 매칭 요소별 점수 계산
            language_score = self._calculate_language_score(tutor['구사 언어'], request.language)
            time_score = self._calculate_time_score(
                tutor['선호시간'], tutor['선호요일'],
                request.preferred_time, request.preferred_day
            )
            level_score = self._calculate_level_score(tutor['한국어수준'], request.level)
            rating_score = self._normalize_rating(float(tutor['평점']))
            gender_score = 1.0 if tutor['성별'] == request.gender else 0.5

            # 최종 점수 계산
            total_score = (
                    self.weights['language_match'] * language_score +
                    self.weights['time_match'] * time_score +
                    self.weights['level_match'] * level_score +
                    self.weights['rating'] * rating_score +
                    self.weights['gender_match'] * gender_score
            )

            recommendations.append({
                'tutor_id': tutor['ID'],
                'tutor': tutor['튜터명'],
                'score': total_score,
                'matching_details': {
                    'language_match': language_score,
                    'time_match': time_score,
                    'level_match': level_score,
                    'rating': rating_score,
                    'gender_match': gender_score
                }
            })

        # 점수순 정렬
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:top_n]
