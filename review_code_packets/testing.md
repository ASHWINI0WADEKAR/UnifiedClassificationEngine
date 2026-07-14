# Testing Evidence

## Tests Added

Added API validation regression tests in [tests/test_api_validation.py](tests/test_api_validation.py) covering:

- wrong file type
- missing file
- invalid schema
- corrupted file
- replay artifact not generated after validation failure

## Verification Command

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -p "test_*.py"
```

Observed result: 14 tests passed.
