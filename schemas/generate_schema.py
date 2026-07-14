"""JSON schema generation entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation import JsonSchemaValidator


def write_contract_schema(path: str | Path = ROOT / "schemas" / "classification_contract_v1.json") -> Path:
    return JsonSchemaValidator().write_schema(path)


if __name__ == "__main__":
    print(write_contract_schema())
