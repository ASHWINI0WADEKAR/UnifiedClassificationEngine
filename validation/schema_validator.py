"""JSON Schema validation and export utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from contracts import ClassificationContract


class JsonSchemaValidator:
    """Validate payloads against the Pydantic-generated JSON schema."""

    def schema(self) -> Dict[str, Any]:
        if hasattr(ClassificationContract, "model_json_schema"):
            return ClassificationContract.model_json_schema()  # type: ignore[attr-defined]
        return ClassificationContract.schema()

    def validate(self, payload: Dict[str, Any]) -> bool:
        ClassificationContract(**payload)
        return True

    def write_schema(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(self.schema(), indent=2, sort_keys=True), encoding="utf-8")
        return output
