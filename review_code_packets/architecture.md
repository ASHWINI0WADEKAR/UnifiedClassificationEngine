# Architecture Evidence

## Architectural Integrity

The production hardening was implemented without changing the existing engine architecture. Validation remains in the existing validation package, the engine retains responsibility for orchestration, and replay/provenance remain isolated modules.

## Evidence

- API request validation remains in [app.py](app.py).
- Upload policy enforcement remains in [validation/file_upload_validator.py](validation/file_upload_validator.py).
- Engine-side replay/provenance behavior remains in [src/engine.py](src/engine.py), [replay/writer.py](replay/writer.py), and [provenance/builder.py](provenance/builder.py).
