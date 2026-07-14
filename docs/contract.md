# BHIV Task 3 Contract Notes

## Canonical Response

The engine returns a canonical Pydantic contract for every modality and preserves previous flat keys for backward compatibility.

## Replay

Replay files are written to `replay/artifacts/` with sorted JSON content and artifact hashes.

## Provenance

Each response includes model name, model version, contract version, timestamp, input hash, output hash, classifier name, engine name, and runtime milliseconds.

## Trace

Trace events record request receipt, input validation, hashing, classifier validation, classifier execution, response normalization, and output validation.

## Error Contract

Use `ClassificationEngine.classify_safe()` to return a production error payload instead of raising exceptions.
