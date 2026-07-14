# Integration Evidence

Integration remains backward compatible:

```python
from engine import ClassificationEngine

engine = ClassificationEngine()
result = engine.classify("hello", modality="text")
print(result["prediction"])
print(result["output"]["prediction"])
```

New canonical usage:

```python
contract = engine.classify_contract("hello", modality="text")
print(contract.contract_version)
print(contract.provenance.input_sha256)
```

Production-safe usage:

```python
payload = engine.classify_safe("", modality="text")
print(payload["success"], payload["error"])
```
