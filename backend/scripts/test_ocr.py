#!/usr/bin/env python3
"""
Test script for the OCR service.

Validates that OCRService can extract text from a real document
and that the output format is correct for RAG Agent consumption.

Usage:
    # From backend/ directory:
    python scripts/test_ocr.py                        # Tests files in data/uploads/
    python scripts/test_ocr.py --file path/to/doc.pdf # Tests a specific file
    python scripts/test_ocr.py --generate-sample      # Creates + tests a sample PDF

Requirements:
    pip install reportlab  # Only needed for --generate-sample
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

# Allow running from backend/ directory without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _generate_sample_pdf(output_path: Path) -> None:
    """Create a minimal rental-agreement PDF for smoke testing."""
    try:
        from reportlab.lib.pagesizes import letter  # type: ignore[import]
        from reportlab.pdfgen import canvas  # type: ignore[import]
    except ImportError:
        print("⚠️  reportlab not installed. Run: pip install reportlab")
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=letter)

    # Page 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 740, "RENTAL AGREEMENT")
    c.setFont("Helvetica", 12)
    lines_p1 = [
        "This Rental Agreement is entered into between:",
        "Landlord: Mr. Ramesh Kumar (hereinafter 'Landlord')",
        "Tenant:   Ms. Priya Sharma (hereinafter 'Tenant')",
        "",
        "Property: Flat No. 4B, Sunshine Apartments, Pune - 411001",
        "Monthly Rent: Rs. 25,000 (Rupees Twenty-Five Thousand only)",
        "Security Deposit: Rs. 75,000 (Three months' rent)",
        "Lock-in Period: 11 months from the date of this agreement",
        "Notice Period: 1 month by either party",
        "",
        "The tenant shall pay rent on or before the 5th of each month.",
    ]
    y = 700
    for line in lines_p1:
        c.drawString(72, y, line)
        y -= 20

    c.showPage()

    # Page 2
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, 740, "Clause 1: Payment Terms")
    c.setFont("Helvetica", 12)
    lines_p2 = [
        "Rent shall be paid by bank transfer to the Landlord's account.",
        "Late payment shall attract a penalty of Rs. 500 per day.",
        "",
        "Clause 2: Maintenance",
        "Minor repairs (< Rs. 1,000) shall be borne by the Tenant.",
        "Major repairs shall be the Landlord's responsibility.",
        "",
        "Clause 3: Termination",
        "Either party may terminate this agreement with 1 month's notice.",
        "The Landlord shall refund the security deposit within 15 days",
        "of vacating after deducting any dues.",
    ]
    y = 700
    for line in lines_p2:
        c.drawString(72, y, line)
        y -= 20

    c.save()
    print(f"✅ Sample PDF created: {output_path}")


def test_ocr(file_path: Optional[Path] = None, generate_sample: bool = False) -> None:
    """Run OCR service tests."""
    from app.core.config import Settings
    from app.services.ocr_service import DocumentExtractionResult, ExtractionMethod, OCRService

    print("=" * 60)
    print("🧪  Lexify-India OCR Service Test")
    print("=" * 60)

    settings = Settings()
    ocr = OCRService()

    # ── Determine test file ─────────────────────────────────────────────
    if file_path:
        test_files = [file_path]

    elif generate_sample:
        sample_path = Path("data/test/sample_rental_agreement.pdf")
        _generate_sample_pdf(sample_path)
        test_files = [sample_path]

    else:
        upload_dir = Path(settings.UPLOAD_DIR)
        test_files = (
            list(upload_dir.glob("*.pdf"))
            + list(upload_dir.glob("*.jpg"))
            + list(upload_dir.glob("*.jpeg"))
            + list(upload_dir.glob("*.png"))
        )
        if not test_files:
            print(
                "\n⚠️  No files found in data/uploads/\n"
                "   Options:\n"
                "     1. python scripts/test_ocr.py --generate-sample\n"
                "     2. python scripts/test_ocr.py --file path/to/doc.pdf\n"
                "     3. Upload a file via the API first.\n"
            )
            return

    # ── Run test on first file ──────────────────────────────────────────
    test_file = test_files[0]
    print(f"\n📄  File: {test_file}")
    print(f"    Size: {test_file.stat().st_size:,} bytes\n")

    try:
        result: DocumentExtractionResult = ocr.extract_from_file(test_file)

        print("✅  Extraction successful!")
        print(f"    Pages:           {result.total_pages}")
        print(f"    Method:          {result.extraction_method.value}")
        print(f"    Avg confidence:  {result.avg_confidence:.2f}")
        print(f"    Total chars:     {len(result.get_full_text()):,}")
        print()

        # Per-page breakdown
        print("📋  Per-page details:")
        for page in result.pages:
            print(
                f"    Page {page.page_number:2d}: "
                f"{len(page.text):5,} chars, "
                f"confidence={page.confidence:.2f}, "
                f"method={page.metadata.get('extraction', 'unknown')}"
            )
        print()

        # Preview
        preview = result.get_preview_text(max_chars=300)
        print("📖  Preview (first 300 chars):")
        for line in preview.splitlines()[:10]:
            print(f"    {line}")
        print()

        # RAG integration smoke-check
        print("🔗  RAG integration check:")
        assert result.pages, "Result must have at least one page"
        assert all(p.page_number >= 1 for p in result.pages), "Page numbers must be ≥ 1"
        assert result.get_full_text(), "Full text must not be empty"
        print("    ✅ pages list non-empty")
        print("    ✅ page_number values valid (≥1)")
        print("    ✅ get_full_text() non-empty")
        print()

        print("=" * 60)
        print("✅  ALL TESTS PASSED — OCR service ready for RAG Agent")
        print("=" * 60)

    except FileNotFoundError as exc:
        print(f"❌  File not found: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"❌  Test FAILED: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test the Lexify-India OCR service.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--file",
        type=Path,
        metavar="PATH",
        help="Path to a specific PDF, JPG, or PNG file to test.",
    )
    parser.add_argument(
        "--generate-sample",
        action="store_true",
        help="Generate a sample rental-agreement PDF and test against it.",
    )
    args = parser.parse_args()

    test_ocr(file_path=args.file, generate_sample=args.generate_sample)
