# Runtime Documentation

## Runtime validation evidence

The runtime behavior for BHIV Task 3 was validated through the CLI and API entry points.

### Verified behaviors

- The CLI demo completed successfully and exercised classification for text, image, PDF, and audio.
- The API health, version, schema, and modality-specific classification endpoints responded correctly.
- Unsupported uploads were rejected before engine dispatch with HTTP 415 and the canonical error contract.
- Corrupted uploads were rejected with HTTP 400 and the canonical error contract.
- Valid uploads continued through the engine and produced replay artifacts.

### Relevant files

- [app.py](app.py)
- [src/engine.py](src/engine.py)
- [validation/file_upload_validator.py](validation/file_upload_validator.py)
- [tests/test_api_validation.py](tests/test_api_validation.py)
