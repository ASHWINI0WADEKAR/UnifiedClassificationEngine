"""Core classification engine for reusable backend orchestration."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Mapping, Optional

from classifiers.audio_classifier import AudioClassifier
from classifiers.base import BaseClassifier
from classifiers.image_classifier import ImageClassifier
from classifiers.pdf_classifier import PDFClassifier
from classifiers.text_classifier import TextClassifier
from helpers.logging_config import configure_logging


class ClassificationEngine:
    """Coordinate modality-specific classifiers through a shared interface."""

    def __init__(
        self,
        classifiers: Optional[Mapping[str, BaseClassifier]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize the engine with injectable classifiers and a logger.

        Args:
            classifiers: Optional mapping of modality names to classifier instances.
            logger: Optional logger for comprehensive observability.
        """
        self._logger = logger or configure_logging("classification_engine")
        self._classifiers: Dict[str, BaseClassifier] = dict(classifiers or {})
        self._register_default_classifiers()

    def _register_default_classifiers(self) -> None:
        """Populate the engine with built-in modality classifiers."""
        defaults = {
            "text": TextClassifier(),
            "image": ImageClassifier(),
            "pdf": PDFClassifier(),
            "audio": AudioClassifier(),
        }
        for modality, classifier in defaults.items():
            self._classifiers.setdefault(modality, classifier)

    @property
    def modalities(self) -> list[str]:
        """Return registered modality names."""
        return sorted(self._classifiers.keys())

    def classify(self, input_data: Any, modality: str = "text") -> Dict[str, Any]:
        """Classify input data using the requested modality classifier."""
        self._logger.info("Starting classification for modality=%s", modality)
        classifier = self._classifiers.get(modality)
        if classifier is None:
            self._logger.error("Unsupported modality requested: %s", modality)
            raise KeyError(f"Unsupported modality: {modality}")

        try:
            if not classifier.validate(input_data):
                self._logger.warning("Input validation failed for modality=%s", modality)
                raise ValueError(f"Invalid input for modality: {modality}")
            start = time.perf_counter()
            result = classifier.classify(input_data)
            result["processing_time"] = f"{time.perf_counter() - start:.6f}s"
            result["explanation"] = classifier.explain(result)
            result["modality"] = modality
            self._logger.info("Classification completed for modality=%s", modality)
            return result
        except Exception as exc:  # pragma: no cover - logging guard
            self._logger.exception("Classification failed for modality=%s", modality)
            raise exc

    def register_classifier(self, modality: str, classifier: BaseClassifier) -> None:
        """Register a classifier instance for a modality."""
        self._classifiers[modality] = classifier
        self._logger.info("Registered classifier for modality=%s", modality)
