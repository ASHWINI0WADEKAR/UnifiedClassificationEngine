# Architecture Evidence

## Implemented architecture

The repository remains in the same Unified Classification Engine architecture and extends it in place for BHIV Task 3.

- The FastAPI entry point in [app.py](app.py) exposes the REST surface for text, image, PDF, and audio classification.
- The orchestration engine in [src/engine.py](src/engine.py) coordinates validation, normalization, provenance, trace generation, replay writing, and compatibility checks.
- Modality-specific classifiers remain isolated under [src/classifiers](src/classifiers) for text, image, PDF, and audio.
- Canonical contract definitions and error contracts live in [contracts/classification.py](contracts/classification.py) and [contracts/errors.py](contracts/errors.py).
- Validation, schema, and compatibility logic are implemented in [validation](validation), [schemas](schemas), and [versioning](versioning).
- Deterministic replay and provenance are implemented in [replay](replay) and [provenance](provenance).

## Runtime flow

1. An API request or CLI invocation reaches the engine.
2. Input and upload validation runs before engine dispatch.
3. The engine hashes the input, creates an execution trace, builds provenance metadata, and invokes the appropriate classifier.
4. The classifier output is normalized into the canonical contract and validated.
5. A deterministic replay artifact is written and returned with the response.

## Engineering review conclusion

The architecture remains production-ready, backward compatible, and aligned with the Task 3 specification without introducing a new project or redesign.
