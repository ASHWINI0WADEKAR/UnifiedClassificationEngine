# Runtime Evidence

## Runtime Behavior Verified

- Upload validation executes before any classifier dispatch.
- Invalid uploads return canonical error payloads and do not create replay artifacts.
- Valid uploads continue to complete classification and produce a replay artifact.

## Evidence

Verified through the new API tests in [tests/test_api_validation.py](tests/test_api_validation.py) and the runtime checks executed from the terminal.
