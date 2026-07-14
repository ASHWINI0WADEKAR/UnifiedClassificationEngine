"""Input validation helpers for classification requests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

SUPPORTED_MODALITIES = {"text", "image", "pdf", "audio"}
FILE_MODALITIES = {"image", "pdf", "audio"}


class InputValidator:
    """Validate raw classifier inputs before dispatch."""

    def validate(self, input_data: Any, modality: str) -> None:
        if modality == "text":
            if not isinstance(input_data, str) or not input_data.strip():
                raise ValueError("Text input must be a non-empty string.")
            return
        if modality in FILE_MODALITIES:
            if not isinstance(input_data, (str, bytes)) or not input_data:
                raise ValueError(f"{modality} input must be a non-empty file path.")
            path = Path(str(input_data))
            if not path.exists() or not path.is_file():
                raise ValueError(f"{modality} input file does not exist: {path}")
            return
        if input_data is None:
            raise ValueError(f"{modality} input cannot be None.")
