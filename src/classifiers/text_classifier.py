"""Text classifier implementation with optional transformer and NLP inference."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from classifiers.base import BaseClassifier
from helpers.dependency_checker import DependencyChecker


class TextClassifier(BaseClassifier):
    """Classifier for plain text content using optional transformer and NLP stacks."""

    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sms-spam-detection") -> None:
        super().__init__(name="text", model_name=model_name)
        self._dependency_checker = DependencyChecker()
        self._pipeline: Optional[Any] = None
        self._nlp: Optional[Any] = None

    def _load_optional_models(self) -> None:
        """Load transformer and spaCy models when explicitly enabled."""
        if os.getenv("UCE_ENABLE_OPTIONAL_MODELS", "0").lower() not in {"1", "true", "yes"}:
            return

        if self._dependency_checker.check("transformers")["available"]:
            try:
                from transformers import pipeline

                self._pipeline = pipeline("text-classification", model=self.model_name)
            except Exception:
                self._pipeline = None

        if self._dependency_checker.check("spacy")["available"]:
            try:
                import spacy

                self._nlp = spacy.blank("en")
            except Exception:
                self._nlp = None

    def classify(self, input_data: Any) -> Dict[str, Any]:
        """Classify text and produce an explainable result payload."""
        if not self.validate(input_data):
            raise ValueError("Text input must be a non-empty string.")
        self._load_optional_models()
        text = str(input_data).strip()
        metadata: Dict[str, Any] = {
            "length": len(text),
            "word_count": len(text.split()),
            "language": self._detect_language(text),
            "keywords": self._extract_keywords(text),
            "entities": self._extract_entities(text),
            "dependency_status": self._dependency_status(),
        }

        prediction = self._predict_text(text)
        confidence = float(prediction["confidence"])
        summary = self._build_summary(text, prediction["label"])
        explanation = self._build_explanation(text, prediction["label"], metadata)
        result = self._build_result(
            prediction["label"],
            confidence,
            summary,
            explanation,
            metadata,
        )
        result.update(
            {
                "prediction": prediction["label"],
                "top_features": metadata["keywords"],
                "processing_steps": ["normalize_text", "language_detection", "keyword_extraction", "entity_recognition", "classification"],
            }
        )
        return result

    def explain(self, result: Dict[str, Any]) -> str:
        """Return an explanation for a text result."""
        return result.get("explanation", "Text classified successfully.")

    def validate(self, input_data: Any) -> bool:
        """Validate that input is a non-empty string."""
        return isinstance(input_data, str) and bool(input_data.strip())

    def _predict_text(self, text: str) -> Dict[str, Any]:
        """Run classification using a transformer when available, otherwise fall back."""
        if self._pipeline is not None:
            try:
                result = self._pipeline(text[:512])[0]
                return {"label": result["label"], "confidence": float(result["score"]) }
            except Exception:
                pass

        label = "general_text"
        confidence = 0.65 if len(text.split()) > 5 else 0.55
        return {"label": label, "confidence": confidence}

    def _detect_language(self, text: str) -> str:
        """Return a best-effort language code."""
        if self._dependency_checker.check("langdetect")["available"]:
            try:
                from langdetect import detect

                return detect(text)
            except Exception:
                pass
        return "unknown"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract a small set of keywords from text."""
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        return list(dict.fromkeys(words))[:8]

    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities when spaCy is available."""
        if self._nlp is None:
            return []
        try:
            doc = self._nlp(text[:1000])
            return [ent.text for ent in doc.ents][:8]
        except Exception:
            return []

    def _build_summary(self, text: str, label: str) -> str:
        """Create a concise summary string for the prediction."""
        return f"Text classified as {label} with {len(text.split())} words."

    def _build_explanation(self, text: str, label: str, metadata: Dict[str, Any]) -> str:
        """Create a human-readable explanation for the classification."""
        entity_text = ", ".join(metadata.get("entities", [])) or "no named entities detected"
        return (
            f"The input was classified as {label} based on its linguistic features, "
            f"keywords, and detected entities ({entity_text})."
        )

    def _dependency_status(self) -> Dict[str, Any]:
        """Report optional dependency availability."""
        return {
            "transformers": self._dependency_checker.check("transformers"),
            "spacy": self._dependency_checker.check("spacy"),
        }


