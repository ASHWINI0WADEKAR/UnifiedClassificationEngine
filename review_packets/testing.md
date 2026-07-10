# Testing Evidence

Capture screenshot after running:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python scripts\verify_api.py
```

Expected proof: unit tests pass and all endpoints pass.
