import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from engine import ClassificationEngine
from classifiers.base import BaseClassifier
from classifiers.text_classifier import TextClassifier
from classifiers.image_classifier import ImageClassifier
from classifiers.pdf_classifier import PDFClassifier
from classifiers.audio_classifier import AudioClassifier
from helpers.dependency_checker import DependencyChecker
from validation import JsonSchemaValidator
from versioning import CONTRACT_VERSION


class ClassificationEngineTests(unittest.TestCase):
    """Regression tests for the reusable classification engine."""

    def setUp(self) -> None:
        self.engine = ClassificationEngine()
        self.examples = ROOT / "examples"

    def test_engine_returns_canonical_contract_and_legacy_keys_for_text(self) -> None:
        result = self.engine.classify("hello world", modality="text")

        for key in {
            "success",
            "contract_version",
            "request_id",
            "modality",
            "input",
            "output",
            "provenance",
            "trace",
            "replay",
            "metadata",
            "error",
        }:
            self.assertIn(key, result)

        for legacy_key in {
            "category",
            "prediction",
            "confidence",
            "summary",
            "explanation",
            "processing_time",
            "model_used",
            "top_features",
            "processing_steps",
        }:
            self.assertIn(legacy_key, result)

        self.assertTrue(result["success"])
        self.assertEqual(result["contract_version"], CONTRACT_VERSION)
        self.assertEqual(result["prediction"], result["output"]["prediction"])
        self.assertEqual(result["model_used"], result["provenance"]["model_name"])
        self.assertEqual(result["provenance"]["input_sha256"], result["input"]["sha256"])
        self.assertIsNone(result["error"])

    def test_all_modalities_return_same_contract_shape(self) -> None:
        cases = {
            "text": "Contract validation sample text.",
            "image": str(self.examples / "sample.jpg"),
            "pdf": str(self.examples / "sample.pdf"),
            "audio": str(self.examples / "sample.wav"),
        }
        keysets = []
        for modality, payload in cases.items():
            result = self.engine.classify(payload, modality=modality)
            self.assertEqual(result["modality"], modality)
            self.assertEqual(result["contract_version"], CONTRACT_VERSION)
            self.assertIn("prediction", result["output"])
            self.assertIn("runtime_ms", result["provenance"])
            keysets.append(set(result.keys()))
        self.assertEqual(len({frozenset(keys) for keys in keysets}), 1)

    def test_json_schema_validation_accepts_contract(self) -> None:
        result = self.engine.classify("schema validation text", modality="text")
        self.assertTrue(JsonSchemaValidator().validate({k: result[k] for k in [
            "success",
            "contract_version",
            "request_id",
            "modality",
            "input",
            "output",
            "provenance",
            "trace",
            "replay",
            "metadata",
            "error",
        ]}))

    def test_replay_artifact_is_written(self) -> None:
        result = self.engine.classify("replay artifact text", modality="text")
        replay = result["replay"]
        replay_path = ROOT / replay["path"]
        self.assertTrue(replay_path.exists())
        payload = json.loads(replay_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["contract_version"], CONTRACT_VERSION)
        self.assertEqual(payload["output"]["prediction"], result["output"]["prediction"])

    def test_contract_compatibility_checker(self) -> None:
        compatible = self.engine.check_contract_compatibility("1.0.0")
        incompatible = self.engine.check_contract_compatibility("9.9.9")
        self.assertTrue(compatible["compatible"])
        self.assertFalse(incompatible["compatible"])

    def test_production_error_contract_is_returned_by_safe_classifier(self) -> None:
        result = self.engine.classify_safe("", modality="text")
        self.assertFalse(result["success"])
        self.assertEqual(result["contract_version"], CONTRACT_VERSION)
        self.assertEqual(result["error"]["code"], "CLASSIFICATION_ERROR")

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
        self.assertEqual(result["contract_version"], CONTRACT_VERSION)

    def test_dependency_checker_reports_package_status(self) -> None:
        checker = DependencyChecker()
        status = checker.check("python")

        self.assertIn("available", status)
        self.assertIn("package", status)


if __name__ == "__main__":
    unittest.main()
