"""Audio classifier implementation with speech-to-text and language detection."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from classifiers.base import BaseClassifier
from helpers.dependency_checker import DependencyChecker


class AudioClassifier(BaseClassifier):
    """Classifier for audio content using speech-to-text and language heuristics."""

    def __init__(self, model_name: str = "faster-whisper-base") -> None:
        super().__init__(name="audio", model_name=model_name)
        self._dependency_checker = DependencyChecker()
        self._whisper_model: Optional[Any] = None

    def _load_optional_models(self) -> None:
        """Load a speech-to-text backend when explicitly enabled."""
        if os.getenv("UCE_ENABLE_OPTIONAL_MODELS", "0").lower() not in {"1", "true", "yes"}:
            return

        if self._dependency_checker.check("faster_whisper")["available"]:
            try:
                from faster_whisper import WhisperModel

                self._whisper_model = WhisperModel(self.model_name.split("-")[-1] if "-" in self.model_name else "base")
            except Exception:
                self._whisper_model = None

    def classify(self, input_data: Any) -> Dict[str, Any]:
        """Classify audio input and produce an explainable result payload."""
        if not self.validate(input_data):
            raise ValueError("Audio input must be a non-empty string path or object.")
        self._load_optional_models()
        path = str(input_data)
        transcript = self._transcribe_audio(path)
        language = self._detect_language(transcript)
        prediction = self._predict_audio(transcript)
        summary = self._build_summary(path, prediction["label"], transcript)
        explanation = self._build_explanation(prediction["label"], transcript, language)
        result = self._build_result(
            prediction["label"],
            float(prediction["confidence"]),
            summary,
            explanation,
            {"source": path, "language": language, "transcript_length": len(transcript.split())},
        )
        result.update(
            {
                "prediction": prediction["label"],
                "top_features": self._extract_keywords(transcript),
                "processing_steps": ["load_audio", "speech_to_text", "language_detection", "transcript_classification", "explain_result"],
            }
        )
        return result

    def explain(self, result: Dict[str, Any]) -> str:
        """Return an explanation for an audio result."""
        return result.get("explanation", "Audio classified successfully.")

    def validate(self, input_data: Any) -> bool:
        """Validate that input is a non-empty string-like value."""
        return isinstance(input_data, (str, bytes)) and bool(input_data)

    def _transcribe_audio(self, path: str) -> str:
        """Transcribe audio using faster-whisper when available."""
        if self._whisper_model is None:
            return ""
        try:
            segments, _ = self._whisper_model.transcribe(path)
            return " ".join(segment.text for segment in segments)
        except Exception:
            return ""

    def _detect_language(self, transcript: str) -> str:
        """Return a best-effort detected language."""
        if transcript.strip() and self._dependency_checker.check("langdetect")["available"]:
            try:
                from langdetect import detect

                return detect(transcript)
            except Exception:
                pass
        return "unknown"

    def _predict_audio(self, transcript: str) -> Dict[str, Any]:
        """Classify the transcript with a simple heuristic."""
        if not transcript.strip():
            return {"label": "unknown_audio", "confidence": 0.55}
        lowered = transcript.lower()
        if any(token in lowered for token in ["order", "purchase", "buy", "price"]):
            return {"label": "sales_audio", "confidence": 0.79}
        if any(token in lowered for token in ["meeting", "agenda", "schedule", "team"]):
            return {"label": "meeting_audio", "confidence": 0.77}
        return {"label": "general_audio", "confidence": 0.70}

    def _extract_keywords(self, transcript: str) -> List[str]:
        """Extract keywords from the transcript."""
        import re

        words = re.findall(r"\b[a-zA-Z]{3,}\b", transcript.lower())
        return list(dict.fromkeys(words))[:8]

    def _build_summary(self, path: str, label: str, transcript: str) -> str:
        """Create a concise summary for the audio result."""
        return f"Audio {Path(path).name} classified as {label} with {len(transcript.split())} transcript words."

    def _build_explanation(self, label: str, transcript: str, language: str) -> str:
        """Create a human-readable explanation for the audio classification."""
        if transcript.strip():
            return f"The audio was classified as {label} based on the transcribed content and detected language {language}."
        return f"The audio was classified as {label} using a fallback path because speech recognition did not produce a transcript."


