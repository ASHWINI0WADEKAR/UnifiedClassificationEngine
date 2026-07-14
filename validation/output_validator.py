"""Output validation helpers for canonical contracts."""

from __future__ import annotations

from typing import Any, Dict

from contracts import ClassificationContract


class OutputValidator:
    """Validate normalized classifier output with Pydantic."""

    def validate(self, payload: Dict[str, Any]) -> ClassificationContract:
        return ClassificationContract(**payload)
