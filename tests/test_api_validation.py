import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app import app

ROOT = Path(__file__).resolve().parents[1]
REPLAY_DIR = ROOT / "replay" / "artifacts"


class UploadValidationApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def _artifact_count(self) -> int:
        return len(list(REPLAY_DIR.glob("*.json")))

    def test_wrong_file_type_returns_canonical_error_contract_with_415(self) -> None:
        before_count = len(list(REPLAY_DIR.glob("*.json")))
        response = self.client.post(
            "/classify/image",
            files={"file": ("sample.txt", b"plain text", "text/plain")},
        )
        self.assertEqual(response.status_code, 415)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "INVALID_UPLOAD")
        self.assertEqual(payload["error"]["detail"]["modality"], "image")
        self.assertEqual(len(list(REPLAY_DIR.glob("*.json"))), before_count)

    def test_jpg_to_pdf_endpoint_returns_415(self) -> None:
        response = self.client.post(
            "/classify/pdf",
            files={"file": ("sample.jpg", b"\xff\xd8\xff", "image/jpeg")},
        )
        self.assertEqual(response.status_code, 415)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "INVALID_UPLOAD")

    def test_pdf_to_image_endpoint_returns_415(self) -> None:
        response = self.client.post(
            "/classify/image",
            files={"file": ("sample.pdf", b"%PDF-1.4", "application/pdf")},
        )
        self.assertEqual(response.status_code, 415)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "INVALID_UPLOAD")

    def test_pdf_to_audio_endpoint_returns_415(self) -> None:
        response = self.client.post(
            "/classify/audio",
            files={"file": ("sample.pdf", b"%PDF-1.4", "application/pdf")},
        )
        self.assertEqual(response.status_code, 415)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "INVALID_UPLOAD")

    def test_txt_to_image_endpoint_returns_415(self) -> None:
        response = self.client.post(
            "/classify/image",
            files={"file": ("sample.txt", b"hello world", "text/plain")},
        )
        self.assertEqual(response.status_code, 415)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "INVALID_UPLOAD")

    def test_missing_file_returns_canonical_error_contract_with_400(self) -> None:
        response = self.client.post("/classify/image")
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "INVALID_UPLOAD")

    def test_invalid_schema_returns_canonical_error_contract(self) -> None:
        response = self.client.post("/classify/text")
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "INVALID_REQUEST")

    def test_corrupted_file_returns_canonical_error_contract_before_engine_dispatch(self) -> None:
        response = self.client.post(
            "/classify/image",
            files={"file": ("sample.jpg", b"not-a-real-image", "image/jpeg")},
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "INVALID_UPLOAD")
        self.assertIn("corrupt", payload["error"]["message"].lower())

    def test_corrupted_pdf_returns_400_on_pdf_endpoint(self) -> None:
        response = self.client.post(
            "/classify/pdf",
            files={"file": ("sample.pdf", b"not-a-real-pdf", "application/pdf")},
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertEqual(payload["error"]["code"], "INVALID_UPLOAD")

    def test_replay_artifact_is_not_generated_after_validation_failure(self) -> None:
        before_count = self._artifact_count()
        response = self.client.post(
            "/classify/pdf",
            files={"file": ("sample.txt", b"this is not a pdf", "application/pdf")},
        )
        self.assertEqual(response.status_code, 415)
        self.assertEqual(len(list(REPLAY_DIR.glob("*.json"))), before_count)


if __name__ == "__main__":
    unittest.main()
