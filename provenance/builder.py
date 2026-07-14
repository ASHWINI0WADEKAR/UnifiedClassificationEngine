"""Provenance metadata builders."""

from __future__ import annotations

from contracts import ProvenanceMetadata, utc_now
from provenance.hashing import stable_json_hash
from versioning import CONTRACT_VERSION


class ProvenanceBuilder:
    """Build model, hash, timestamp, and runtime provenance."""

    def build(
        self,
        *,
        model_name: str,
        classifier: str,
        input_sha256: str,
        output_payload: dict,
        runtime_ms: float,
        model_version: str = "unknown",
    ) -> ProvenanceMetadata:
        return ProvenanceMetadata(
            model_name=model_name,
            model_version=model_version,
            contract_version=CONTRACT_VERSION,
            created_at=utc_now(),
            input_sha256=input_sha256,
            output_sha256=stable_json_hash(output_payload),
            runtime_ms=round(runtime_ms, 3),
            classifier=classifier,
        )
