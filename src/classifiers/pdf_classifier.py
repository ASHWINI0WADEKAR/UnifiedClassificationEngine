"""PDF classifier implementation with metadata, text extraction, and OCR."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from classifiers.base import BaseClassifier
from helpers.dependency_checker import DependencyChecker


class PDFClassifier(BaseClassifier):
    """Classifier for PDF documents with metadata extraction and OCR fallback."""

    def __init__(self, model_name: str = "pdf-classifier-v1") -> None:
        super().__init__(name="pdf", model_name=model_name)
        self._dependency_checker = DependencyChecker()
        self._ocr_reader: Optional[Any] = None

    def _load_optional_models(self) -> None:
        """Load OCR helpers when explicitly enabled."""
        if os.getenv("UCE_ENABLE_OPTIONAL_MODELS", "0").lower() not in {"1", "true", "yes"}:
            return

        if self._dependency_checker.check("easyocr")["available"]:
            try:
                import easyocr

                self._ocr_reader = easyocr.Reader(["en"])
            except Exception:
                self._ocr_reader = None

    def classify(self, input_data: Any) -> Dict[str, Any]:
        """Classify a PDF and produce an explainable result payload."""
        if not self.validate(input_data):
            raise ValueError("PDF input must be a non-empty string path.")
        self._load_optional_models()
        path = str(input_data)
        metadata = self._extract_metadata(path)
        extracted_text = self._extract_text(path)
        prediction = self._predict_pdf(extracted_text)
        summary = self._build_summary(path, prediction["label"], extracted_text)
        explanation = self._build_explanation(prediction["label"], extracted_text, metadata)
        result = self._build_result(
            prediction["label"],
            float(prediction["confidence"]),
            summary,
            explanation,
            metadata,
        )
        result.update(
            {
                "prediction": prediction["label"],
                "top_features": self._extract_keywords(extracted_text),
                "processing_steps": ["extract_metadata", "extract_text", "ocr_scan_if_needed", "classify_content", "explain_result"],
            }
        )
        return result

    def explain(self, result: Dict[str, Any]) -> str:
        """Return an explanation for a PDF result."""
        return result.get("explanation", "PDF classified successfully.")

    def validate(self, input_data: Any) -> bool:
        """Validate that input is a non-empty string-like value."""
        return isinstance(input_data, (str, bytes)) and bool(input_data)

    def _extract_metadata(self, path: str) -> Dict[str, Any]:
        """Extract PDF metadata using pypdf when available."""
        try:
            from pypdf import PdfReader

            reader = PdfReader(path)
            info = reader.metadata or {}
            return {
                "source": path,
                "pages": len(reader.pages),
                "title": getattr(info, "title", None),
                "author": getattr(info, "author", None),
                "creator": getattr(info, "creator", None),
            }
        except Exception:
            return {"source": path}

    def _extract_text(self, path: str) -> str:
        """Extract text from PDF, falling back to OCR when direct extraction is empty."""
        try:
            from pypdf import PdfReader

            reader = PdfReader(path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            if text.strip():
                return text
        except Exception:
            pass

        if self._ocr_reader is not None:
            try:
                return " ".join(self._ocr_reader.readtext(path, detail=0))
            except Exception:
                pass
        return ""

    def _predict_pdf(self, text: str) -> Dict[str, Any]:
        """Classify the extracted text using a simple, dependency-light heuristic."""
        if not text.strip():
            return {"label": "scanned_pdf", "confidence": 0.62}
        lowered = text.lower()
        if any(token in lowered for token in ["invoice", "receipt", "payment", "billing"]):
            return {"label": "financial_document", "confidence": 0.81}
        if any(token in lowered for token in ["contract", "agreement", "terms", "policy"]):
            return {"label": "legal_document", "confidence": 0.79}
        return {"label": "general_pdf", "confidence": 0.70}

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from the PDF text."""
        import re

        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        return list(dict.fromkeys(words))[:8]

    def _build_summary(self, path: str, label: str, text: str) -> str:
        """Create a concise summary for the PDF result."""
        return f"PDF {Path(path).name} classified as {label} with {len(text.split())} extracted words."

    def _build_explanation(self, label: str, text: str, metadata: Dict[str, Any]) -> str:
        """Create a human-readable explanation for the PDF classification."""
        if text.strip():
            return f"The document was classified as {label} based on extracted text content and metadata such as pages={metadata.get('pages')}."
        return f"The document was classified as {label} using OCR-assisted analysis because direct text extraction was unavailable."


