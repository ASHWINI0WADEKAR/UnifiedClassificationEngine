"""Core classification engine for reusable backend orchestration."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Mapping, Optional

from classifiers.audio_classifier import AudioClassifier
from classifiers.base import BaseClassifier
from classifiers.image_classifier import ImageClassifier
from classifiers.pdf_classifier import PDFClassifier
from classifiers.text_classifier import TextClassifier
from contracts import ClassificationContract, ClassificationOutput, model_to_dict
from contracts.errors import ProductionErrorBuilder
from helpers.logging_config import configure_logging
from provenance import ProvenanceBuilder, input_reference, stable_json_hash
from replay import ReplayArtifactWriter
from trace import ExecutionTracer
from validation import InputValidator, JsonSchemaValidator, OutputValidator
from versioning import CONTRACT_VERSION
from versioning.compatibility import ContractCompatibilityChecker


class ClassificationEngine:
    """Coordinate modality-specific classifiers through a shared contract."""

    def __init__(
        self,
        classifiers: Optional[Mapping[str, BaseClassifier]] = None,
        logger: Optional[logging.Logger] = None,
        replay_dir: str = "replay/artifacts",
    ) -> None:
        """Initialize the engine with injectable classifiers and contract tooling."""
        self._logger = logger or configure_logging("classification_engine")
        self._classifiers: Dict[str, BaseClassifier] = dict(classifiers or {})
        self._input_validator = InputValidator()
        self._output_validator = OutputValidator()
        self._schema_validator = JsonSchemaValidator()
        self._compatibility_checker = ContractCompatibilityChecker()
        self._provenance_builder = ProvenanceBuilder()
        self._replay_writer = ReplayArtifactWriter(replay_dir)
        self._error_builder = ProductionErrorBuilder()
        self._register_default_classifiers()

    def _register_default_classifiers(self) -> None:
        """Populate the engine with built-in modality classifiers."""
        defaults = {
            "text": TextClassifier(),
            "image": ImageClassifier(),
            "pdf": PDFClassifier(),
            "audio": AudioClassifier(),
        }
        for modality, classifier in defaults.items():
            self._classifiers.setdefault(modality, classifier)

    @property
    def modalities(self) -> list[str]:
        """Return registered modality names."""
        return sorted(self._classifiers.keys())

    @property
    def contract_version(self) -> str:
        """Return the active classification contract version."""
        return CONTRACT_VERSION

    def contract_schema(self) -> Dict[str, Any]:
        """Return the canonical JSON schema."""
        return self._schema_validator.schema()

    def check_contract_compatibility(self, requested_version: str) -> Dict[str, Any]:
        """Check requested contract compatibility."""
        return self._compatibility_checker.check(requested_version).to_dict()

    def classify(
        self,
        input_data: Any,
        modality: str = "text",
        contract_version: str = CONTRACT_VERSION,
    ) -> Dict[str, Any]:
        """Classify input and return canonical contract data plus legacy keys."""
        contract = self.classify_contract(input_data, modality=modality, contract_version=contract_version)
        return contract.to_legacy_dict()

    def classify_contract(
        self,
        input_data: Any,
        modality: str = "text",
        contract_version: str = CONTRACT_VERSION,
    ) -> ClassificationContract:
        """Classify input and return the canonical Pydantic contract."""
        self._compatibility_checker.require_compatible(contract_version)
        tracer = ExecutionTracer()
        tracer.add("request_received", detail={"modality": modality, "contract_version": contract_version})
        self._logger.info("Starting classification for modality=%s", modality)

        classifier = self._classifiers.get(modality)
        if classifier is None:
            self._logger.error("Unsupported modality requested: %s", modality)
            raise KeyError(f"Unsupported modality: {modality}")

        self._input_validator.validate(input_data, modality)
        tracer.add("input_validated")
        input_ref = input_reference(input_data, modality)
        request_id = self._request_id(modality, input_ref.sha256)
        tracer.add("input_hashed", detail={"sha256": input_ref.sha256})

        if not classifier.validate(input_data):
            raise ValueError(f"Invalid input for modality: {modality}")
        tracer.add("classifier_input_validated", detail={"classifier": classifier.__class__.__name__})

        start = time.perf_counter()
        raw_result = classifier.classify(input_data)
        runtime_ms = (time.perf_counter() - start) * 1000
        raw_result["processing_time"] = f"{runtime_ms / 1000:.6f}s"
        raw_result["explanation"] = classifier.explain(raw_result)
        tracer.add("classifier_executed", detail={"runtime_ms": round(runtime_ms, 3)})

        output = self._normalize_output(raw_result)
        tracer.add("response_normalized")
        provenance = self._provenance_builder.build(
            model_name=str(raw_result.get("model_used", classifier.model_name)),
            classifier=classifier.__class__.__name__,
            input_sha256=input_ref.sha256,
            output_payload=model_to_dict(output),
            runtime_ms=runtime_ms,
            model_version=str(raw_result.get("model_version", "unknown")),
        )
        contract_payload: Dict[str, Any] = {
            "success": True,
            "contract_version": CONTRACT_VERSION,
            "request_id": request_id,
            "modality": modality,
            "input": model_to_dict(input_ref),
            "output": model_to_dict(output),
            "provenance": model_to_dict(provenance),
            "trace": [model_to_dict(event) for event in tracer.events()],
            "replay": None,
            "metadata": dict(raw_result.get("metadata", {})),
            "error": None,
        }
        contract = self._output_validator.validate(contract_payload)
        tracer.add("output_validated")
        contract.trace = tracer.events()
        replay = self._replay_writer.write(model_to_dict(contract), request_id)
        contract.replay = replay
        contract = self._output_validator.validate(model_to_dict(contract))
        self._schema_validator.validate(model_to_dict(contract))
        self._logger.info("Classification completed for modality=%s", modality)
        return contract

    def classify_safe(
        self,
        input_data: Any,
        modality: str = "text",
        contract_version: str = CONTRACT_VERSION,
    ) -> Dict[str, Any]:
        """Classify input and return a production error contract instead of raising."""
        try:
            return self.classify(input_data, modality=modality, contract_version=contract_version)
        except Exception as exc:  # pragma: no cover - production guard
            self._logger.warning("Safe classification failed for modality=%s: %s", modality, exc)
            return self._error_builder.response(exc, request_id="unavailable", modality=modality)

    def register_classifier(self, modality: str, classifier: BaseClassifier) -> None:
        """Register a classifier instance for a modality."""
        self._classifiers[modality] = classifier
        self._logger.info("Registered classifier for modality=%s", modality)

    def _normalize_output(self, result: Dict[str, Any]) -> ClassificationOutput:
        """Normalize legacy classifier output into canonical output."""
        prediction = str(result.get("prediction", result.get("category", "unknown")))
        confidence = float(result.get("confidence", 0.0))
        return ClassificationOutput(
            prediction=prediction,
            confidence=max(0.0, min(1.0, confidence)),
            explanation=str(result.get("explanation", "")),
            summary=str(result.get("summary", "")),
            top_features=[str(item) for item in result.get("top_features", [])],
            processing_steps=[str(item) for item in result.get("processing_steps", [])],
        )

    def _request_id(self, modality: str, input_sha256: str) -> str:
        """Create a deterministic request identifier for replay lookup."""
        return stable_json_hash({"contract_version": CONTRACT_VERSION, "modality": modality, "input_sha256": input_sha256})[:24]


