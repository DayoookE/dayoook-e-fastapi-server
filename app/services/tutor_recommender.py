import pandas as pd
import numpy as np
from typing import List, Dict


class TutorRecommender:
    def __init__(self, tutors_df: pd.DataFrame, tutees_df: pd.DataFrame):
        # 칼럼명 지정
        tutor_columns = ['ID', '튜터ID', '나이', '성별', '구사 언어', '평점', '한국어수준', '선호요일', '선호시간']
        tutee_columns = ['ID', '튜티ID', '나이', '성별', '구사언어', '한국어수준', '선호요일', '선호시간']

        self.tutors = tutors_df
        self.tutors.columns = tutor_columns

        self.tutees = tutees_df
        self.tutees.columns = tutee_columns

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
        level_map = {'초급': 1, '중급': 2, '고급': 3}
        tutor_level_num = level_map[tutor_level]
        tutee_level_num = level_map[tutee_level]

        if tutor_level_num >= tutee_level_num:
            return 1.0
        return 0.5

    def _normalize_rating(self, rating: float) -> float:
        """평점 정규화 (1-5점 scale)"""
        return (rating - 1) / 4

    def get_recommendations(self, tutee_id: int, top_n: int = 5) -> List[Dict]:
        tutee = self.tutees[self.tutees['ID'] == tutee_id].iloc[0]

        recommendations = []
        for _, tutor in self.tutors.iterrows():
            # 각 매칭 요소별 점수 계산
            language_score = self._calculate_language_score(tutor['구사 언어'], tutee['구사언어'])
            time_score = self._calculate_time_score(
                tutor['선호시간'], tutor['선호요일'],
                tutee['선호시간'], tutee['선호요일']
            )
            level_score = self._calculate_level_score(tutor['한국어수준'], tutee['한국어수준'])
            rating_score = self._normalize_rating(float(tutor['평점']))
            gender_score = 1.0 if tutor['성별'] == tutee['성별'] else 0.5

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
