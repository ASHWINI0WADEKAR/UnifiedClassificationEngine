# Integration Guide

Other projects can reuse the engine without FastAPI or the demo script.

## Import From Source

```python
from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\Ashwini Wadekar\OneDrive\Desktop\UnifiedClassificationEngine")
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from engine import ClassificationEngine

engine = ClassificationEngine()
result = engine.classify("Sample text for classification", modality="text")
print(result["prediction"], result["confidence"])
```

## Classify Files

```python
from engine import ClassificationEngine

engine = ClassificationEngine()

image_result = engine.classify("examples/sample.jpg", modality="image")
pdf_result = engine.classify("examples/sample.pdf", modality="pdf")
audio_result = engine.classify("examples/sample.wav", modality="audio")
```

## Register a Custom Classifier

```python
from classifiers.base import BaseClassifier
from engine import ClassificationEngine

class MyClassifier(BaseClassifier):
    def __init__(self):
        super().__init__(name="custom", model_name="custom-v1")

    def validate(self, input_data):
        return input_data is not None

    def classify(self, input_data):
        return self._build_result("custom_prediction", 0.9, "custom summary", "custom explanation")

    def explain(self, result):
        return result["explanation"]

engine = ClassificationEngine(classifiers={"custom": MyClassifier()})
print(engine.classify("payload", modality="custom"))
```

## Optional Models

By default, optional heavy models are disabled so imports never crash a consumer project. To enable installed optional AI backends:

```powershell
$env:UCE_ENABLE_OPTIONAL_MODELS="1"
```
