"""Base abstractions for classification modules."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict

from helpers.result_formatter import ResultFormatter


class BaseClassifier(ABC):
    """Base interface for all modality-specific classifiers."""

    def __init__(self, name: str, model_name: str) -> None:
        self.name: str = name
        self.model_name: str = model_name

    @abstractmethod
    def classify(self, input_data: Any) -> Dict[str, Any]:
        """Classify input data and return a standardized result payload.

        Args:
            input_data: Raw input content for the modality.

        Returns:
            A standardized classification result mapping.
        """

    @abstractmethod
    def explain(self, result: Dict[str, Any]) -> str:
        """Generate an explanation string from a classification result.

        Args:
            result: The standardized classification result payload.

        Returns:
            A human-readable explanation.
        """

    @abstractmethod
    def validate(self, input_data: Any) -> bool:
        """Validate whether the provided input is acceptable for this classifier.

        Args:
            input_data: Raw input content for the modality.

        Returns:
            True when input is acceptable, otherwise False.
        """

    def _build_result(
        self,
        category: str,
        confidence: float,
        summary: str,
        explanation: str,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Create a standardized result payload.

        Args:
            category: The predicted category name.
            confidence: Confidence score in the range 0.0 to 1.0.
            summary: Short descriptive summary of the result.
            explanation: Explanation of the prediction.
            metadata: Additional metadata for the result.

        Returns:
            A standardized dictionary payload.
        """
        return ResultFormatter.build_result(
            category=category,
            confidence=confidence,
            summary=summary,
            explanation=explanation,
            metadata=metadata,
            model_used=self.model_name,
            processing_time=f"{time.perf_counter():.6f}s",
        )
