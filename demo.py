"""CLI demo for the Unified Classification Engine.

Runs all four modality classifiers against bundled sample files and prints
Prediction, Confidence, Explanation, Model Used, and Processing Time.

Usage:
    python demo.py
    python demo.py --modality text
    python demo.py --modality image --input path/to/file.jpg
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from engine import ClassificationEngine  # noqa: E402

EXAMPLES = ROOT / "examples"

MODALITY_DEFAULTS = {
    "text": EXAMPLES / "sample.txt",
    "image": EXAMPLES / "sample.jpg",
    "pdf": EXAMPLES / "sample.pdf",
    "audio": EXAMPLES / "sample.wav",
}


def load_input(modality: str, input_path: Path | None) -> Any:
    """Load input data for the requested modality."""
    path = input_path or MODALITY_DEFAULTS[modality]
    if not path.exists():
        raise FileNotFoundError(f"Sample file not found: {path}")

    if modality == "text":
        return path.read_text(encoding="utf-8")
    return str(path.resolve())


def print_result(modality: str, result: Dict[str, Any], elapsed: float) -> None:
    """Print the standardized classification output fields."""
    prediction = result.get("prediction", result.get("category", "unknown"))
    confidence = result.get("confidence", 0.0)
    explanation = result.get("explanation", "")
    model_used = result.get("model_used", "unknown")
    processing_time = f"{elapsed:.4f}s"

    print(f"\n{'=' * 64}")
    print(f"  {modality.upper()} CLASSIFICATION")
    print(f"{'=' * 64}")
    print(f"  Prediction:      {prediction}")
    print(f"  Confidence:      {confidence:.4f}" if isinstance(confidence, float) else f"  Confidence:      {confidence}")
    print(f"  Explanation:     {explanation}")
    print(f"  Model Used:      {model_used}")
    print(f"  Processing Time: {processing_time}")


def run_classification(
    engine: ClassificationEngine,
    modality: str,
    input_path: Path | None = None,
) -> Dict[str, Any]:
    """Classify input for a single modality and print results."""
    input_data = load_input(modality, input_path)
    start = time.perf_counter()
    result = engine.classify(input_data, modality=modality)
    elapsed = time.perf_counter() - start
    print_result(modality, result, elapsed)
    return result


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate the Unified Classification Engine across all modalities.",
    )
    parser.add_argument(
        "--modality",
        choices=["text", "image", "pdf", "audio", "all"],
        default="all",
        help="Modality to classify (default: all)",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Optional input file path (defaults to examples/sample.*)",
    )
    return parser.parse_args()


def main() -> int:
    """Run the classification demo."""
    args = parse_args()
    engine = ClassificationEngine()

    print("Unified Classification Engine — Demo")
    print(f"Sample directory: {EXAMPLES}")

    modalities = ["text", "image", "pdf", "audio"] if args.modality == "all" else [args.modality]

    try:
        for modality in modalities:
            run_classification(engine, modality, args.input if args.modality != "all" else None)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        print("Run: python scripts/generate_samples.py", file=sys.stderr)
        return 1
    except (KeyError, ValueError) as exc:
        print(f"\nClassification error: {exc}", file=sys.stderr)
        return 1

    print(f"\n{'=' * 64}")
    print("  Demo completed successfully.")
    print(f"{'=' * 64}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
