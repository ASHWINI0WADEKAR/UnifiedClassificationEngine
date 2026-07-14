"""Strict upload validation for API file classifiers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, FrozenSet


@dataclass(frozen=True)
class UploadPolicy:
    """Allowed extensions and MIME types for a modality."""

    extensions: FrozenSet[str]
    mime_types: FrozenSet[str]


UPLOAD_POLICIES: Dict[str, UploadPolicy] = {
    "image": UploadPolicy(
        extensions=frozenset({".png", ".jpg", ".jpeg", ".bmp"}),
        mime_types=frozenset({"image/png", "image/jpeg", "image/bmp", "image/x-ms-bmp"}),
    ),
    "pdf": UploadPolicy(
        extensions=frozenset({".pdf"}),
        mime_types=frozenset({"application/pdf"}),
    ),
    "audio": UploadPolicy(
        extensions=frozenset({".wav", ".mp3", ".flac"}),
        mime_types=frozenset({"audio/wav", "audio/x-wav", "audio/wave", "audio/mpeg", "audio/mp3", "audio/flac", "audio/x-flac"}),
    ),
}


class UploadValidationError(ValueError):
    """Raised when an uploaded file violates modality policy."""

    def __init__(self, message: str, detail: dict[str, object]) -> None:
        super().__init__(message)
        self.detail = detail


class FileUploadValidator:
    """Validate upload filename extension, MIME type, and non-empty content."""

    def validate(self, *, filename: str | None, content_type: str | None, contents: bytes, modality: str) -> None:
        policy = UPLOAD_POLICIES.get(modality)
        if policy is None:
            raise UploadValidationError(
                f"Unsupported upload modality: {modality}",
                {"modality": modality},
            )

        if not contents:
            raise UploadValidationError(
                "Uploaded file is empty.",
                {
                    "modality": modality,
                    "filename": filename,
                    "received_mime_type": content_type,
                    "allowed_extensions": sorted(policy.extensions),
                    "allowed_mime_types": sorted(policy.mime_types),
                },
            )

        extension = Path(filename or "").suffix.lower()
        normalized_mime = (content_type or "").split(";", 1)[0].strip().lower()
        errors: list[str] = []

        if extension not in policy.extensions:
            errors.append(f"Extension '{extension or '<missing>'}' is not allowed for {modality}.")
        if normalized_mime not in policy.mime_types:
            errors.append(f"MIME type '{normalized_mime or '<missing>'}' is not allowed for {modality}.")
        if not self._contents_match_policy(contents, modality):
            errors.append(f"Uploaded file contents appear corrupt or invalid for {modality}.")

        if errors:
            raise UploadValidationError(
                "Invalid upload for classification modality.",
                {
                    "modality": modality,
                    "filename": filename,
                    "received_extension": extension or None,
                    "received_mime_type": normalized_mime or None,
                    "allowed_extensions": sorted(policy.extensions),
                    "allowed_mime_types": sorted(policy.mime_types),
                    "violations": errors,
                },
            )

    def _contents_match_policy(self, contents: bytes, modality: str) -> bool:
        if modality == "image":
            return self._looks_like_image(contents)
        if modality == "pdf":
            return contents.startswith(b"%PDF")
        if modality == "audio":
            return self._looks_like_audio(contents)
        return True

    def _looks_like_image(self, contents: bytes) -> bool:
        if not contents:
            return False
        if contents.startswith(b"\x89PNG\r\n\x1a\n"):
            return True
        if contents.startswith(b"\xff\xd8\xff"):
            return True
        if contents.startswith(b"BM"):
            return True
        return False

    def _looks_like_audio(self, contents: bytes) -> bool:
        if not contents:
            return False
        if len(contents) >= 12 and contents.startswith(b"RIFF") and contents[8:12] == b"WAVE":
            return True
        if contents.startswith(b"ID3"):
            return True
        if contents.startswith(b"fLaC"):
            return True
        if contents.startswith((b"\xff\xf3", b"\xff\xf2", b"\xff\xfb")):
            return True
        return False
