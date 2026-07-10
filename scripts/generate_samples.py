"""Generate sample input files for the classification engine demo."""

from __future__ import annotations

import wave
from pathlib import Path

from PIL import Image, ImageDraw


def _write_sample_pdf(path: Path) -> None:
    """Write a valid lightweight PDF sample."""
    try:
        from pypdf import PdfWriter

        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        writer.add_metadata(
            {
                "/Title": "Unified Classification Engine Sample",
                "/Author": "Unified Classification Engine",
                "/Subject": "Sample PDF document for classification demo",
            }
        )
        with path.open("wb") as output:
            writer.write(output)
        return
    except Exception:
        pass

    # Fallback: Pillow can still create a valid one-page PDF from an image.
    image = Image.new("RGB", (612, 792), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((72, 120), "Sample PDF document for classification demo.", fill=(0, 0, 0))
    image.save(path, "PDF")


def main() -> None:
    examples = Path(__file__).resolve().parents[1] / "examples"
    examples.mkdir(exist_ok=True)

    (examples / "sample.txt").write_text(
        "This is a sample text document for the Unified Classification Engine demo. "
        "It contains enough words to trigger meaningful keyword extraction and classification.",
        encoding="utf-8",
    )

    img = Image.new("RGB", (400, 200), color=(240, 240, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 390, 190], outline=(50, 50, 150), width=2)
    draw.text((30, 80), "Sample Image Document", fill=(30, 30, 120))
    img.save(examples / "sample.jpg", "JPEG")

    _write_sample_pdf(examples / "sample.pdf")

    with wave.open(str(examples / "sample.wav"), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)

    for path in sorted(examples.iterdir()):
        print(f"  {path.name} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
