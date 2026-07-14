"""Verify all REST API endpoints for the classification engine."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app import app  # noqa: E402

EXAMPLES = ROOT / "examples"
client = TestClient(app)

REQUIRED_CONTRACT_FIELDS = {
    "success",
    "contract_version",
    "request_id",
    "modality",
    "input",
    "output",
    "provenance",
    "trace",
    "replay",
    "metadata",
    "error",
}
LEGACY_FIELDS = {"prediction", "confidence", "explanation", "model_used", "processing_time"}


def _valid_classification(response, modality: str) -> bool:
    if response.status_code != 200:
        return False
    payload = response.json()
    return (
        REQUIRED_CONTRACT_FIELDS.issubset(payload.keys())
        and LEGACY_FIELDS.issubset(payload.keys())
        and payload.get("modality") == modality
        and payload.get("contract_version") == "1.0.0"
        and payload.get("output", {}).get("prediction") == payload.get("prediction")
    )


def main() -> int:
    """Verify every API endpoint returns a valid response."""
    results: list[tuple[str, bool, str]] = []

    response = client.get("/health")
    ok = response.status_code == 200 and response.json().get("status") == "ok"
    results.append(("GET /health", ok, response.text[:300]))

    response = client.get("/version")
    ok = response.status_code == 200 and response.json().get("contract_version") == "1.0.0"
    results.append(("GET /version", ok, response.text[:300]))

    response = client.get("/schema")
    ok = response.status_code == 200 and "properties" in response.json()
    results.append(("GET /schema", ok, response.text[:300]))

    response = client.post(
        "/classify/text",
        data={"text": "Sample API text classification request for verification."},
    )
    results.append(("POST /classify/text", _valid_classification(response, "text"), response.text[:300]))

    with open(EXAMPLES / "sample.jpg", "rb") as img:
        response = client.post(
            "/classify/image",
            files={"file": ("sample.jpg", img, "image/jpeg")},
        )
    results.append(("POST /classify/image", _valid_classification(response, "image"), response.text[:300]))

    with open(EXAMPLES / "sample.pdf", "rb") as pdf:
        response = client.post(
            "/classify/pdf",
            files={"file": ("sample.pdf", pdf, "application/pdf")},
        )
    results.append(("POST /classify/pdf", _valid_classification(response, "pdf"), response.text[:300]))

    with open(EXAMPLES / "sample.wav", "rb") as audio:
        response = client.post(
            "/classify/audio",
            files={"file": ("sample.wav", audio, "audio/wav")},
        )
    results.append(("POST /classify/audio", _valid_classification(response, "audio"), response.text[:300]))

    print("API Endpoint Verification")
    print("=" * 50)
    all_ok = True
    for endpoint, ok, snippet in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}  {endpoint}")
        if not ok:
            all_ok = False
            print(f"         {snippet}")

    print("=" * 50)
    print("All endpoints passed." if all_ok else "Some endpoints failed.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
