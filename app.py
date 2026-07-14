"""REST API for the Unified Classification Engine."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, Form, Request, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from engine import ClassificationEngine  # noqa: E402
from contracts.errors import ProductionErrorBuilder  # noqa: E402
from validation import FileUploadValidator, UploadValidationError  # noqa: E402
from versioning import CONTRACT_VERSION  # noqa: E402

API_VERSION = CONTRACT_VERSION

app = FastAPI(
    title="Unified Classification Engine",
    description="REST API for text, image, PDF, and audio classification.",
    version=API_VERSION,
)

engine = ClassificationEngine()
upload_validator = FileUploadValidator()
error_builder = ProductionErrorBuilder()


def _contract_error_response(payload: Dict[str, Any], status_code: int = 400) -> JSONResponse:
    """Return a canonical error contract payload as an HTTP response."""
    return JSONResponse(status_code=status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Convert FastAPI request validation failures into canonical error contracts."""
    path = request.url.path
    if path.startswith("/classify/image") or path.startswith("/classify/pdf") or path.startswith("/classify/audio"):
        return _contract_error_response(
            error_builder.from_message(
                code="INVALID_UPLOAD",
                message="No upload file was provided.",
                modality=path.split("/")[-1],
                recoverable=True,
                detail={"errors": exc.errors(), "reason": "missing_file"},
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return _contract_error_response(
        error_builder.from_message(
            code="INVALID_REQUEST",
            message="Request validation failed.",
            modality="unknown",
            recoverable=True,
            detail={"errors": exc.errors()},
        ),
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@app.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "success": True,
        "status": "ok",
        "service": "unified-classification-engine",
        "version": API_VERSION,
        "contract_version": CONTRACT_VERSION,
    }


@app.get("/version")
def version() -> Dict[str, Any]:
    """Version endpoint for deployment and contract checks."""
    return {
        "success": True,
        "service": "unified-classification-engine",
        "version": API_VERSION,
        "contract_version": CONTRACT_VERSION,
        "modalities": engine.modalities,
        "compatibility": engine.check_contract_compatibility(CONTRACT_VERSION),
    }


@app.get("/schema")
def schema() -> Dict[str, Any]:
    """Return the canonical classification JSON schema."""
    return engine.contract_schema()


@app.post(
    "/classify/text",
    summary="Classify text",
    description="Classify plain text input using the canonical contract response format.",
    response_model=None,
    responses={
        200: {"description": "Successful text classification", "content": {"application/json": {"example": {"success": True, "modality": "text"}}}},
        400: {"description": "Validation failure", "content": {"application/json": {"example": {"success": False, "error": {"code": "INVALID_REQUEST"}}}}},
    },
)
def classify_text(text: str = Form(..., description="Plain text content to classify.")) -> Any:
    """Classify plain text input."""
    result = engine.classify_safe(text, modality="text")
    if not result.get("success", False):
        return _contract_error_response(result)
    return result


@app.post(
    "/classify/image",
    summary="Classify an uploaded image",
    description="Accepts only image files with supported extensions and MIME types. Supported formats: .png, .jpg, .jpeg, .bmp, .gif, .webp.",
    response_model=None,
    responses={
        200: {"description": "Successful image classification", "content": {"application/json": {"example": {"success": True, "modality": "image"}}}},
        400: {"description": "Invalid or corrupted upload", "content": {"application/json": {"example": {"success": False, "error": {"code": "INVALID_UPLOAD"}}}}},
        415: {"description": "Unsupported media type", "content": {"application/json": {"example": {"success": False, "error": {"code": "INVALID_UPLOAD"}}}}},
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "examples": {
                        "valid_jpeg": {
                            "summary": "Valid JPEG image",
                            "value": {"file": "examples/sample.jpg"},
                        }
                    }
                }
            }
        }
    },
)
async def classify_image(
    file: UploadFile = File(
        ...,
        description="Image upload only. Allowed extensions: .png, .jpg, .jpeg, .bmp, .gif, .webp. MIME type must be image/* for the matching format.",
    )
) -> Any:
    """Classify an uploaded image file."""
    return await _classify_upload(file, "image")


@app.post(
    "/classify/pdf",
    summary="Classify an uploaded PDF",
    description="Accepts only PDF files with .pdf extension and application/pdf MIME type.",
    response_model=None,
    responses={
        200: {"description": "Successful PDF classification", "content": {"application/json": {"example": {"success": True, "modality": "pdf"}}}},
        400: {"description": "Invalid or corrupted upload", "content": {"application/json": {"example": {"success": False, "error": {"code": "INVALID_UPLOAD"}}}}},
        415: {"description": "Unsupported media type", "content": {"application/json": {"example": {"success": False, "error": {"code": "INVALID_UPLOAD"}}}}},
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "examples": {
                        "valid_pdf": {
                            "summary": "Valid PDF document",
                            "value": {"file": "examples/sample.pdf"},
                        }
                    }
                }
            }
        }
    },
)
async def classify_pdf(
    file: UploadFile = File(
        ...,
        description="PDF upload only. Allowed extension: .pdf. MIME type must be application/pdf.",
    )
) -> Any:
    """Classify an uploaded PDF file."""
    return await _classify_upload(file, "pdf")


@app.post(
    "/classify/audio",
    summary="Classify an uploaded audio file",
    description="Accepts only audio files with supported extensions and MIME types. Supported formats: .wav, .mp3, .flac, .ogg, .m4a.",
    response_model=None,
    responses={
        200: {"description": "Successful audio classification", "content": {"application/json": {"example": {"success": True, "modality": "audio"}}}},
        400: {"description": "Invalid or corrupted upload", "content": {"application/json": {"example": {"success": False, "error": {"code": "INVALID_UPLOAD"}}}}},
        415: {"description": "Unsupported media type", "content": {"application/json": {"example": {"success": False, "error": {"code": "INVALID_UPLOAD"}}}}},
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "examples": {
                        "valid_wav": {
                            "summary": "Valid WAV audio",
                            "value": {"file": "examples/sample.wav"},
                        }
                    }
                }
            }
        }
    },
)
async def classify_audio(
    file: UploadFile = File(
        ...,
        description="Audio upload only. Allowed extensions: .wav, .mp3, .flac, .ogg, .m4a. MIME type must match the audio format.",
    )
) -> Any:
    """Classify an uploaded audio file."""
    return await _classify_upload(file, "audio")


async def _classify_upload(file: UploadFile, modality: str) -> Any:
    """Save an uploaded file temporarily and classify it."""
    suffix = Path(file.filename or "upload").suffix or f".{modality}"
    tmp_path: str | None = None
    try:
        contents = await file.read()
        try:
            upload_validator.validate(
                filename=file.filename,
                content_type=file.content_type,
                contents=contents,
                modality=modality,
            )
        except UploadValidationError as exc:
            detail_violations = exc.detail.get("violations", []) if isinstance(exc.detail, dict) else []
            has_unsupported_type = any(
                "extension" in str(item).lower() or "mime type" in str(item).lower()
                for item in detail_violations
            )
            is_corrupt = any("corrupt" in str(item).lower() for item in detail_violations)
            status_code = (
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
                if has_unsupported_type
                else status.HTTP_400_BAD_REQUEST
            )
            message = str(exc)
            if is_corrupt and not has_unsupported_type:
                message = "Uploaded file contents appear corrupt or invalid."
            return _contract_error_response(
                error_builder.from_message(
                    code="INVALID_UPLOAD",
                    message=message,
                    modality=modality,
                    recoverable=True,
                    detail=exc.detail,
                ),
                status_code=status_code,
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        result = engine.classify_safe(tmp_path, modality=modality)
        if not result.get("success", False):
            return _contract_error_response(result)
        return result
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
