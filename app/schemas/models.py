from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PronunciationFeedback:
    predicted_text: str
    avg_confidence: float
    low_confidence_parts: List[str]
    reference_text: Optional[str]
    wer: Optional[float]
    cer: Optional[float]
