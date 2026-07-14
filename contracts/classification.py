"""Pydantic models for the canonical BHIV classification contract."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from versioning import CONTRACT_VERSION


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    """Return a dict for Pydantic v1 or v2 models without warnings."""
    if hasattr(model, "model_dump"):
        return model.model_dump()  # type: ignore[attr-defined]
    return model.dict()


class InputReference(BaseModel):
    """Normalized input metadata without storing raw payload bytes."""

    modality: str
    input_type: str
    size_bytes: int = Field(ge=0)
    sha256: str
    source: Optional[str] = None


class ClassificationOutput(BaseModel):
    """Normalized prediction payload shared by all classifiers."""

    prediction: str
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    summary: str
    top_features: List[str] = Field(default_factory=list)
    processing_steps: List[str] = Field(default_factory=list)


class ProvenanceMetadata(BaseModel):
    """Model and runtime provenance for reproducibility."""

    model_name: str
    model_version: str = "unknown"
    contract_version: str = CONTRACT_VERSION
    created_at: str
    input_sha256: str
    output_sha256: str
    runtime_ms: float = Field(ge=0.0)
    engine: str = "UnifiedClassificationEngine"
    classifier: str


class TraceEvent(BaseModel):
    """Single execution trace event."""

    step: str
    status: str
    timestamp: str
    duration_ms: float = Field(default=0.0, ge=0.0)
    detail: Dict[str, Any] = Field(default_factory=dict)


class ReplayArtifact(BaseModel):
    """Replay artifact pointer and integrity hash."""

    artifact_id: str
    path: str
    sha256: str


class ErrorDetail(BaseModel):
    """Production error contract."""

    code: str
    message: str
    recoverable: bool = True
    detail: Dict[str, Any] = Field(default_factory=dict)


class ClassificationContract(BaseModel):
    """Canonical classification contract v1.0.0."""

    success: bool = True
    contract_version: str = CONTRACT_VERSION
    request_id: str
    modality: str
    input: InputReference
    output: ClassificationOutput
    provenance: ProvenanceMetadata
    trace: List[TraceEvent]
    replay: Optional[ReplayArtifact] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[ErrorDetail] = None

    @validator("contract_version")
    def contract_version_must_match(cls, value: str) -> str:
        if value != CONTRACT_VERSION:
            raise ValueError(f"Unsupported contract version: {value}")
        return value

    def to_legacy_dict(self) -> Dict[str, Any]:
        """Return canonical data plus legacy flat keys used by earlier tasks."""
        payload = model_to_dict(self)
        payload.update(
            {
                "category": self.output.prediction,
                "prediction": self.output.prediction,
                "confidence": self.output.confidence,
                "summary": self.output.summary,
                "explanation": self.output.explanation,
                "processing_time": f"{self.provenance.runtime_ms / 1000:.6f}s",
                "model_used": self.provenance.model_name,
                "top_features": self.output.top_features,
                "processing_steps": self.output.processing_steps,
            }
        )
        return payload


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()
