"""Hashing and input reference helpers for provenance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from contracts import InputReference


def stable_json_hash(payload: Any) -> str:
    """Create a deterministic SHA-256 hash for JSON-compatible data."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def input_reference(input_data: Any, modality: str) -> InputReference:
    """Build normalized input metadata and hash."""
    if modality == "text":
        text = str(input_data)
        data = text.encode("utf-8")
        return InputReference(modality=modality, input_type="text", size_bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

    if isinstance(input_data, (str, bytes)):
        path = Path(str(input_data))
        if path.exists() and path.is_file():
            data = path.read_bytes()
            return InputReference(
                modality=modality,
                input_type=path.suffix.lstrip(".").lower() or "file",
                size_bytes=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
                source=str(path.resolve()),
            )

    encoded = json.dumps(input_data, sort_keys=True, default=str).encode("utf-8")
    return InputReference(
        modality=modality,
        input_type=type(input_data).__name__,
        size_bytes=len(encoded),
        sha256=hashlib.sha256(encoded).hexdigest(),
    )
