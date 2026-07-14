"""Production error contract helpers."""

from __future__ import annotations

from typing import Any, Dict

from contracts import ErrorDetail, model_to_dict
from versioning import CONTRACT_VERSION


class ProductionErrorBuilder:
    """Map runtime exceptions into stable production error details."""

    def build(self, exc: Exception, code: str = "CLASSIFICATION_ERROR", recoverable: bool = True) -> ErrorDetail:
        return ErrorDetail(
            code=code,
            message=str(exc),
            recoverable=recoverable,
            detail={"exception_type": exc.__class__.__name__},
        )

    def response(self, exc: Exception, *, request_id: str = "unavailable", modality: str = "unknown") -> Dict[str, Any]:
        error = self.build(exc)
        return self.from_error(error, request_id=request_id, modality=modality)

    def from_message(
        self,
        *,
        code: str,
        message: str,
        modality: str,
        request_id: str = "unavailable",
        recoverable: bool = True,
        detail: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Build a structured production error response from validated details."""
        error = ErrorDetail(
            code=code,
            message=message,
            recoverable=recoverable,
            detail=detail or {},
        )
        return self.from_error(error, request_id=request_id, modality=modality)

    def from_error(
        self,
        error: ErrorDetail,
        *,
        request_id: str = "unavailable",
        modality: str = "unknown",
    ) -> Dict[str, Any]:
        """Build the stable production error envelope."""
        return {
            "success": False,
            "contract_version": CONTRACT_VERSION,
            "request_id": request_id,
            "modality": modality,
            "error": model_to_dict(error),
        }

