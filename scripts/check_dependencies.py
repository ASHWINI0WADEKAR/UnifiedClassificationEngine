"""Report optional dependency availability for submission verification."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from helpers.dependency_checker import DependencyChecker  # noqa: E402

OPTIONAL_DEPENDENCIES = [
    "transformers",
    "torch",
    "spacy",
    "cv2",
    "easyocr",
    "PIL",
    "pypdf",
    "pydub",
    "librosa",
    "faster_whisper",
    "fastapi",
    "uvicorn",
]


def main() -> int:
    checker = DependencyChecker()
    print("Dependency Verification")
    print("=" * 50)
    for package in OPTIONAL_DEPENDENCIES:
        status = checker.check(package)
        label = "AVAILABLE" if status["available"] else "OPTIONAL-FALLBACK"
        print(f"  {label:17} {package}")
    print("=" * 50)
    print("Unavailable optional dependencies degrade through fallback classifiers and do not block runtime.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
