from openai import AsyncOpenAI
from loguru import logger
from dotenv import load_dotenv
import os
from app.schemas.models import PronunciationFeedback
from typing import Optional
from g2pk2 import G2p


class GPTFeedback:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        load_dotenv()
        self.client = AsyncOpenAI(api_key=api_key)
        self.g2p = G2p()
        self.model = model
        self.rules: Optional[str] = None
        self.__FILE = os.getenv('FILE')
        self.init_rules()

    def init_rules(self):
        path = os.path.join(self.__FILE, 'static', "rules.txt")
        with open(path, 'r', encoding='utf-8') as file:
            self.rules = file.read()

    async def get_feedback(self, results: PronunciationFeedback, confidence_threshold: float) -> str:
        prompt = f"""
        당신은 한국어 발음을 가르치는 전문가입니다. 
        발음 인식의 신뢰도를 고려하여 1-2문장으로 핵심적인 피드백만 제공해주세요.

        predicted text: {results.predicted_text} \r\n
        reference text(ground truth reference text): {results.reference_text} \r\n
        pronounced reference text(ground truth pronounced reference text): {self.g2p(results.reference_text)} \r\n
        
        
        전체 인식 신뢰도: {results.avg_confidence:.2f}

        다음 규칙을 따라 피드백을 작성해주세요:
        1. 발음 인식 모델이 예측한 `predicted_text`와 실제 정답 텍스트인 `reference text(ground truth reference text)`, 
        실제 정답 텍스트에 대한 이상적인 발음을 나타내는 pronounced reference text(ground truth pronounced reference text) 비교하여 분석
        2. 교정해야 하는 발음을 어떻게 발음해야 하는지 가이드
            2-1. 발음 가이드는 후술할 `rules`를 참고하여 제공
            2-2. 인식된 텍스트가 실제 텍스트보다 짧은 경우: 누락된 부분에 대해 "좀 더 또렷하게 발음해주세요" 피드백
            2-3. 인식된 텍스트가 실제 텍스트보다 긴 경우: "끝음절을 깔끔하게 마무리해주세요" 피드백
        3. 전체 신뢰도가 0.5 이하면 "다시 한 번 말씀해 주세요" 추가
        4. `신뢰도`와 같은 AI 분야에서 쓰이는 전문적인 용어는 피드백 과정에서 지양
        
        rules: {self.rules}

        피드백은 한국어로 작성해주고, 최대한 긍정적으로 표현해주세요.
        """
        logger.debug(prompt)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()
