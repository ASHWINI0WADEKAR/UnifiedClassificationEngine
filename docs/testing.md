# Testing Report

## Commands

```powershell
python scripts\generate_samples.py
python demo.py
python -m unittest discover -s tests -p "test_*.py"
python scripts\verify_api.py
```

## Coverage

- Text classifier execution through `demo.py` and API verifier.
- Image classifier execution with `examples/sample.jpg`.
- PDF classifier execution with `examples/sample.pdf`.
- Audio classifier execution with `examples/sample.wav`.
- Engine standardized schema unit tests.
- Dependency checker unit test.
- REST endpoint verification for `/health`, `/version`, and all four classification routes.

## Expected Evidence

Capture screenshots showing:

- CLI demo completed successfully.
- Unit tests passed.
- API verifier reports all endpoints passed.
- Docker compose API responds at `/health`.

## Current Notes

Use `python -m unittest discover -s tests -p "test_*.py"` on Windows to avoid collision with unrelated installed packages named `tests`.
