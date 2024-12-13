import torch
import librosa
import numpy as np
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import nlptutti as metrics
import torch.nn.functional as F

from g2pk2 import G2p
from app.schemas.models import PronunciationFeedback
import re

g2p = G2p()


def clean_text(text):
    text = re.sub(r'\([^)]*\)', lambda x: re.sub(r'[^가-힣\s]', '', x.group()), text).rstrip() + " "
    return text.strip()


def post_processing(predictions: str):
    return g2p(clean_text(predictions))


class PronunciationAssessor:
    def __init__(self, model_path="kresnik/wav2vec2-large-xlsr-korean", confidence_threshold=0.7):
        """
        모델과 프로세서를 초기화합니다
        Args:
            model_path: 학습된 모델이 저장된 경로
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = Wav2Vec2Processor.from_pretrained(model_path)
        self.model = Wav2Vec2ForCTC.from_pretrained(model_path).to(self.device)
        self.confidence_threshold = confidence_threshold
        self.model.eval()

    def get_confidence_and_predictions(self, logits):
        probs = F.softmax(logits, dim=-1)
        confidence_scores = torch.max(probs, dim=-1).values
        predicted_ids = torch.argmax(logits, dim=-1)

        avg_confidence = float(confidence_scores.mean())
        low_confidence_mask = confidence_scores < self.confidence_threshold
        predicted_text = self.processor.batch_decode(predicted_ids)[0]

        low_confidence_indices = torch.where(low_confidence_mask)[1].tolist()

        low_confidence_parts = []
        for idx in low_confidence_indices:
            if idx < len(predicted_text):
                low_confidence_parts.append(predicted_text[idx])

        return {
            'predicted_ids': predicted_ids,
            'avg_confidence': avg_confidence,
            'low_confidence_parts': low_confidence_parts
        }

    def load_audio(self, file_path, target_sr=16000):
        """
        오디오 파일을 로드하고 전처리합니다
        Args:
            file_path: 오디오 파일 경로
            target_sr: 목표 샘플링 레이트
        """
        speech, sr = librosa.load(file_path, sr=target_sr)
        return speech

    def compute_error_rates(self, prediction, reference):
        """
        예측값과 참조값 사이의 WER과 CER을 계산합니다
        """
        # 공백 제거하여 문자 단위 비교
        pred_clean = prediction.replace(" ", "")
        ref_clean = reference.replace(" ", "")

        # WER과 CER 계산
        wer = metrics.get_wer(prediction, reference)['wer']
        cer = metrics.get_cer(pred_clean, ref_clean)['cer']

        return wer, cer

    @torch.no_grad()
    def predict(self, audio, reference_text=None) -> PronunciationFeedback:
        """
        오디오의 발음을 평가합니다
        Args:
            audio: 평가할 오디오 파일 또는 파일 경로
            reference_text: 참조 텍스트 (있는 경우)
        Returns:
            평가 결과 딕셔너리
        """
        # 오디오 로드 및 전처리
        if isinstance(audio, str):
            speech = self.load_audio(audio)
        else:
            speech = audio
        inputs = self.processor(speech, sampling_rate=16000, return_tensors="pt")
        input_values = inputs.input_values.to(self.device)

        # 모델 추론
        outputs = self.model(input_values)
        logits = outputs.logits
        confidence_data = self.get_confidence_and_predictions(logits)
        predicted_text = self.processor.batch_decode(confidence_data['predicted_ids'])[0]

        # 참조 텍스트가 있는 경우 오류율 계산
        if reference_text:
            wer, cer = self.compute_error_rates(predicted_text, reference_text)
            return PronunciationFeedback(
                predicted_text=post_processing(predicted_text),
                avg_confidence=confidence_data['avg_confidence'],
                low_confidence_parts=confidence_data['low_confidence_parts'],
                reference_text=reference_text,
                wer=wer,
                cer=cer
            )

        return PronunciationFeedback(
            predicted_text=predicted_text,
            avg_confidence=confidence_data['avg_confidence'],
            low_confidence_parts=confidence_data['low_confidence_parts'],
            reference_text=None,
            wer=None,
            cer=None
        )
