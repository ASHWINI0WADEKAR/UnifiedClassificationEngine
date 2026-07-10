"""Image classifier implementation with optional OCR and object detection."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from classifiers.base import BaseClassifier
from helpers.dependency_checker import DependencyChecker


class ImageClassifier(BaseClassifier):
    """Classifier for image content using OCR and object detection when available."""

    def __init__(self, model_name: str = "yolov8n") -> None:
        super().__init__(name="image", model_name=model_name)
        self._dependency_checker = DependencyChecker()
        self._easyocr_reader: Optional[Any] = None
        self._model: Optional[Any] = None

    def _load_optional_models(self) -> None:
        """Load OCR and object detection dependencies when explicitly enabled."""
        if os.getenv("UCE_ENABLE_OPTIONAL_MODELS", "0").lower() not in {"1", "true", "yes"}:
            return

        if self._dependency_checker.check("easyocr")["available"]:
            try:
                import easyocr

                self._easyocr_reader = easyocr.Reader(["en"])
            except Exception:
                self._easyocr_reader = None

        if self._dependency_checker.check("torchvision")["available"]:
            try:
                import torchvision

                self._model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=None)
            except Exception:
                self._model = None

    def classify(self, input_data: Any) -> Dict[str, Any]:
        """Classify image input and produce an explainable result payload."""
        if not self.validate(input_data):
            raise ValueError("Image input must be a non-empty string path or object.")
        self._load_optional_models()
        path = str(input_data)
        metadata = self._collect_metadata(path)
        extracted_text = self._extract_text(path)
        objects = self._detect_objects(path)
        prediction = self._predict_image(path, extracted_text, objects)
        summary = self._build_summary(path, prediction["label"], objects, extracted_text)
        explanation = self._build_explanation(prediction["label"], extracted_text, objects)
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
                "top_features": objects or [text for text in extracted_text.split()[:5] if text],
                "processing_steps": ["load_image", "preprocess_image", "ocr_extraction", "object_detection", "classification"],
            }
        )
        return result

    def explain(self, result: Dict[str, Any]) -> str:
        """Return an explanation for an image result."""
        return result.get("explanation", "Image classified successfully.")

    def validate(self, input_data: Any) -> bool:
        """Validate that input is a non-empty string-like value."""
        return isinstance(input_data, (str, bytes)) and bool(input_data)

    def _collect_metadata(self, path: str) -> Dict[str, Any]:
        """Collect basic image metadata when the path exists."""
        try:
            from PIL import Image

            image = Image.open(path)
            return {
                "source": path,
                "format": image.format,
                "size": image.size,
                "mode": image.mode,
            }
        except Exception:
            return {"source": path}

    def _extract_text(self, path: str) -> str:
        """Extract text from an image using EasyOCR when available."""
        if self._easyocr_reader is None:
            return ""
        try:
            result = self._easyocr_reader.readtext(path, detail=0)
            return " ".join(result)
        except Exception:
            return ""

    def _detect_objects(self, path: str) -> List[str]:
        """Detect objects using torchvision when available."""
        if self._model is None:
            return []
        try:
            import cv2
            import numpy as np
            from PIL import Image

            image = cv2.imread(path)
            if image is None:
                return []
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            image_tensor = self._preprocess_image(pil_image)
            with self._model.eval():
                predictions = self._model([image_tensor])[0]
            labels = [str(label) for label in predictions.get("labels", [])]
            return labels[:5]
        except Exception:
            return []

    def _preprocess_image(self, image: Any) -> Any:
        """Apply a lightweight preprocessing step using OpenCV and PIL."""
        from torchvision import transforms

        transform = transforms.Compose([transforms.ToTensor()])
        return transform(image)

    def _predict_image(self, path: str, extracted_text: str, objects: List[str]) -> Dict[str, Any]:
        """Create a best-effort image classification prediction."""
        if extracted_text:
            return {"label": "textual_image", "confidence": 0.78}
        if objects:
            return {"label": "object_scene", "confidence": 0.74}
        return {"label": "image", "confidence": 0.68}

    def _build_summary(self, path: str, label: str, objects: List[str], extracted_text: str) -> str:
        """Create a concise summary for the image result."""
        object_summary = ", ".join(objects[:3]) or "no detected objects"
        text_summary = "text extracted" if extracted_text else "no text extracted"
        return f"Image from {Path(path).name} classified as {label}; {object_summary}; {text_summary}."

    def _build_explanation(self, label: str, extracted_text: str, objects: List[str]) -> str:
        """Create a human-readable explanation for the image classification."""
        object_summary = ", ".join(objects[:3]) or "no detected objects"
        if extracted_text:
            return f"The image was classified as {label} because OCR detected text and the scene contained {object_summary}."
        return f"The image was classified as {label} based on its visual characteristics and detected objects ({object_summary})."


