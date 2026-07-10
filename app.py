"""REST API for the Unified Classification Engine."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from engine import ClassificationEngine  # noqa: E402

API_VERSION = "1.0.0"

app = FastAPI(
    title="Unified Classification Engine",
    description="REST API for text, image, PDF, and audio classification.",
    version=API_VERSION,
)

engine = ClassificationEngine()


def _format_response(result: Dict[str, Any], modality: str) -> Dict[str, Any]:
    """Return a consistent API response."""
    return {
        "success": result.get("success", True),
        "modality": modality,
        "prediction": result.get("prediction", result.get("category")),
        "confidence": result.get("confidence"),
        "explanation": result.get("explanation"),
        "model_used": result.get("model_used"),
        "processing_time": result.get("processing_time"),
        "metadata": result.get("metadata", {}),
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "success": True,
        "status": "ok",
        "service": "unified-classification-engine",
        "version": API_VERSION,
    }


@app.get("/version")
def version() -> Dict[str, Any]:
    """Version endpoint for deployment checks."""
    return {
        "success": True,
        "service": "unified-classification-engine",
        "version": API_VERSION,
        "modalities": engine.modalities,
    }


@app.post("/classify/text")
def classify_text(text: str = Form(...)) -> Dict[str, Any]:
    """Classify plain text input."""
    try:
        result = engine.classify(text, modality="text")
        return _format_response(result, "text")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/classify/image")
async def classify_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Classify an uploaded image file."""
    return await _classify_upload(file, "image")


@app.post("/classify/pdf")
async def classify_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Classify an uploaded PDF file."""
    return await _classify_upload(file, "pdf")


@app.post("/classify/audio")
async def classify_audio(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Classify an uploaded audio file."""
    return await _classify_upload(file, "audio")


async def _classify_upload(file: UploadFile, modality: str) -> Dict[str, Any]:
    """Save an uploaded file temporarily and classify it."""
    suffix = Path(file.filename or "upload").suffix or f".{modality}"
    tmp_path: str | None = None
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        result = engine.classify(tmp_path, modality=modality)
        return _format_response(result, modality)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
