"""Helpers for building and normalizing classification results."""

from __future__ import annotations

from typing import Any, Dict, Optional


class ResultFormatter:
    """Normalize classification outputs into a shared schema."""

    @staticmethod
    def build_result(
        category: str,
        confidence: float,
        summary: str,
        explanation: str,
        metadata: Optional[Dict[str, Any]] = None,
        model_used: str = "",
        processing_time: str = "",
    ) -> Dict[str, Any]:
        """Build a standardized classification result payload.

        Args:
            category: The predicted category.
            confidence: Confidence score.
            summary: Short summary text.
            explanation: Human-readable explanation.
            metadata: Optional metadata payload.
            model_used: Model identifier.
            processing_time: Processing duration string.

        Returns:
            A normalized result mapping.
        """
        return {
            "success": True,
            "category": category,
            "confidence": confidence,
            "summary": summary,
            "explanation": explanation,
            "metadata": metadata or {},
            "processing_time": processing_time,
            "model_used": model_used,
        }
