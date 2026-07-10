# Testing Report

Generated during final submission readiness validation.

## Commands Executed

| Command | Result |
|---|---|
| `python scripts\generate_samples.py` | PASS |
| `python demo.py` | PASS |
| `python -m unittest discover -s tests -p test_*.py` | PASS |
| `python scripts\verify_api.py` | PASS |
| `python scripts\check_dependencies.py` | PASS |
| `docker --version` | FAIL - Docker CLI unavailable in this environment |
| `docker compose config` | FAIL - Docker CLI unavailable in this environment |

## Verified Classifiers

| Classifier | Input | Result |
|---|---|---|
| Text | `examples/sample.txt` | PASS |
| Image | `examples/sample.jpg` | PASS |
| PDF | `examples/sample.pdf` | PASS |
| Audio | `examples/sample.wav` | PASS |

## Verified API Endpoints

| Endpoint | Result |
|---|---|
| `GET /health` | PASS |
| `GET /version` | PASS |
| `POST /classify/text` | PASS |
| `POST /classify/image` | PASS |
| `POST /classify/pdf` | PASS |
| `POST /classify/audio` | PASS |

## Notes

Optional heavy AI model loading is disabled by default with `UCE_ENABLE_OPTIONAL_MODELS=0`. This prevents local execution from failing when large model artifacts or native runtime libraries are unavailable. The classifiers still execute and return consistent predictions, confidence, explanations, model names, processing times, and metadata.

Docker files were created and reviewed, but Docker could not be started here because the Docker executable is not installed or not on PATH. See `docs/docker.md` for the exact command and screenshot instructions.
