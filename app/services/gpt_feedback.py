from openai import AsyncOpenAI
from loguru import logger
from app.schemas.models import PronunciationFeedback


class GPTFeedback:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def get_feedback(self, results: PronunciationFeedback, confidence_threshold: float) -> str:
        prompt = f"""
        당신은 한국어 발음을 가르치는 전문가입니다. 
        발음 인식의 신뢰도를 고려하여 1-2문장으로 핵심적인 피드백만 제공해주세요.

        predicted_text: {results.predicted_text}
        reference_text(ground truth): {results.reference_text}
        전체 인식 신뢰도: {results.avg_confidence:.2f}

        다음 규칙을 따라 피드백을 작성해주세요:
        1. 발음 인식 모델이 예측한 `predicted_text`와 실제 정답 텍스트인 `reference_text(ground truth)`와 비교하여 분석
        2. 교정해야 하는 발음을 어떻게 발음해야 하는지 가이드
        3. 전체 신뢰도가 0.5 이하면 "다시 한 번 말씀해 주세요" 추가
        4. `신뢰도`와 같은 AI 분야에서 쓰이는 전문적인 용어는 피드백 과정에서 지양

        예시:
        - 신뢰도 높은 경우: "ㄹ을 'l'처럼 발음했네요. 혀끝을 살짝 굴려보세요."
        - 신뢰도 낮은 경우: "발음이 명확하지 않았어요. 조금 더 또렷하게 말씀해주세요."

        피드백은 한국어로 작성해주고, 최대한 긍정적으로 표현해주세요.
        """
        logger.debug(prompt)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()
