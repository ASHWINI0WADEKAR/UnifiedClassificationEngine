import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from engine import ClassificationEngine
from classifiers.base import BaseClassifier
from classifiers.text_classifier import TextClassifier
from classifiers.image_classifier import ImageClassifier
from classifiers.pdf_classifier import PDFClassifier
from classifiers.audio_classifier import AudioClassifier
from helpers.dependency_checker import DependencyChecker


class ClassificationEngineTests(unittest.TestCase):
    """Regression tests for the reusable classification engine."""

    def test_engine_returns_standardized_schema_for_text(self) -> None:
        engine = ClassificationEngine()
        result = engine.classify("hello world", modality="text")

        self.assertTrue(result["success"])
        self.assertEqual(
            set(result.keys()),
            {
                "success",
                "category",
                "confidence",
                "summary",
                "explanation",
                "metadata",
                "processing_time",
                "model_used",
                "prediction",
                "top_features",
                "processing_steps",
                "modality",
            },
        )
        self.assertIsInstance(result["metadata"], dict)
        self.assertTrue(result["model_used"])
        self.assertEqual(result["prediction"], result["category"])
        self.assertIsInstance(result["top_features"], list)
        self.assertIsInstance(result["processing_steps"], list)

    def test_classifier_interface_is_consistent(self) -> None:
        classifiers = [
            TextClassifier(),
            ImageClassifier(),
            PDFClassifier(),
            AudioClassifier(),
        ]

        for classifier in classifiers:
            self.assertIsInstance(classifier, BaseClassifier)
            self.assertTrue(hasattr(classifier, "classify"))
            self.assertTrue(hasattr(classifier, "explain"))
            self.assertTrue(hasattr(classifier, "validate"))

    def test_engine_supports_dependency_injection(self) -> None:
        class DummyClassifier(BaseClassifier):
            def __init__(self) -> None:
                super().__init__(name="dummy", model_name="dummy-model")

            def classify(self, input_data: object) -> dict:
                return self._build_result("dummy", 0.99, "tested", "test")

            def explain(self, result: dict) -> str:
                return result["summary"]

            def validate(self, input_data: object) -> bool:
                return True

        engine = ClassificationEngine(classifiers={"dummy": DummyClassifier()})
        result = engine.classify("sample", modality="dummy")

        self.assertEqual(result["category"], "dummy")
        self.assertEqual(result["confidence"], 0.99)

    def test_dependency_checker_reports_package_status(self) -> None:
        checker = DependencyChecker()
        status = checker.check("python")

        self.assertIn("available", status)
        self.assertIn("package", status)


if __name__ == "__main__":
    unittest.main()


