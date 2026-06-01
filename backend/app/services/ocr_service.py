"""
OCR service for extracting text from legal documents.

Supports:
- PDF text extraction (direct + OCR fallback for scanned pages)
- Image OCR (JPG, PNG)
- Image preprocessing pipeline for quality improvement
- Page-level structure preservation for citation support
- Per-page confidence scoring

Output format is designed for downstream RAG Agent consumption:
    result.pages[i].page_number  → use for citations
    result.pages[i].text         → chunk this for embeddings
    result.pages[i].confidence   → quality gate indicator
"""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
import pdfplumber
from PIL import Image

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


class ExtractionMethod(Enum):
    """Method used to extract text from a document."""

    PDF_DIRECT = "pdf_direct"  # Direct embedded text from PDF
    PDF_OCR = "pdf_ocr"        # OCR applied to rasterised PDF pages
    IMAGE_OCR = "image_ocr"    # OCR applied to an image file


class PageText:
    """
    Represents extracted text from a single document page.

    Attributes:
        page_number:  1-based page index (use for RAG citations).
        text:         Extracted UTF-8 text content.
        confidence:   Mean OCR confidence in [0, 1].  1.0 for direct PDF text.
        sections:     Heuristically detected sections (future use).
        metadata:     Per-page extraction metadata (``extraction`` key:
                      ``"direct"`` | ``"ocr"``).
    """

    def __init__(
        self,
        page_number: int,
        text: str,
        confidence: float = 1.0,
        sections: Optional[List[Dict[str, str]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.page_number: int = page_number
        self.text: str = text
        self.confidence: float = confidence
        self.sections: List[Dict[str, str]] = sections or []
        self.metadata: Dict[str, Any] = metadata or {}

    def __repr__(self) -> str:
        return (
            f"PageText(page={self.page_number}, "
            f"chars={len(self.text)}, "
            f"confidence={self.confidence:.2f})"
        )


class DocumentExtractionResult:
    """
    Complete extraction result for one document.

    This is the primary output handed to the RAG Pipeline Agent.

    Attributes:
        pages:             Ordered list of PageText objects (page 1 first).
        total_pages:       Total page count in the original document.
        extraction_method: How text was obtained (direct PDF / OCR).
        language:          ISO 639-1 language code (default ``"en"``).
        avg_confidence:    Mean confidence across all pages.
        metadata:          Document-level metadata dict.
    """

    def __init__(
        self,
        pages: List[PageText],
        total_pages: int,
        extraction_method: ExtractionMethod,
        language: str = "en",
        avg_confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.pages: List[PageText] = pages
        self.total_pages: int = total_pages
        self.extraction_method: ExtractionMethod = extraction_method
        self.language: str = language
        self.avg_confidence: float = avg_confidence
        self.metadata: Dict[str, Any] = metadata or {}

    # ------------------------------------------------------------------
    # Convenience accessors (used by API layer and test scripts)
    # ------------------------------------------------------------------

    def get_full_text(self) -> str:
        """Concatenate all page texts with double newline separators."""
        return "\n\n".join(page.text for page in self.pages if page.text)

    def get_preview_text(self, max_chars: int = 500) -> str:
        """Return a preview from the first page, truncated to *max_chars*."""
        if not self.pages:
            return ""
        first = self.pages[0].text
        if len(first) <= max_chars:
            return first
        return first[:max_chars] + "…"

    def __repr__(self) -> str:
        return (
            f"DocumentExtractionResult("
            f"pages={self.total_pages}, "
            f"method={self.extraction_method.value}, "
            f"confidence={self.avg_confidence:.2f})"
        )


# ---------------------------------------------------------------------------
# OCR Service
# ---------------------------------------------------------------------------


class OCRService:
    """
    OCR and document text-extraction service.

    Implements a two-stage extraction strategy for PDFs:
      1. Direct text extraction via *pdfplumber* (fast, 100 % accuracy).
      2. OCR fallback via *PaddleOCR* when a page lacks embedded text
         (handles scanned documents, image-only PDFs).

    Image files (JPG, PNG) always go through the OCR path.

    The PaddleOCR engine is **lazy-loaded** on first use to avoid slowing
    down application startup.

    Usage::

        ocr = OCRService()
        result = ocr.extract_from_file(Path("rental_agreement.pdf"))
        for page in result.pages:
            print(page.page_number, page.confidence, page.text[:100])
    """

    # Minimum character count below which a page is considered "sparse"
    # and will be re-extracted via OCR.
    _SPARSE_TEXT_THRESHOLD: int = 50

    def __init__(self) -> None:
        self._ocr_engine = None  # Lazy-loaded on first OCR call
        self.supported_image_formats: set[str] = {".jpg", ".jpeg", ".png"}
        self.supported_pdf_format: str = ".pdf"

    # ------------------------------------------------------------------
    # Internal: lazy OCR engine access
    # ------------------------------------------------------------------

    @property
    def ocr_engine(self):
        """
        Lazy-load and cache the PaddleOCR engine.

        PaddleOCR is imported here (not at module level) so that the
        application can start without the library installed — useful when
        running unit tests that mock this property.
        """
        if self._ocr_engine is None:
            logger.info("Initialising PaddleOCR engine (first-time, may take a moment)…")
            try:
                from paddleocr import PaddleOCR  # type: ignore[import]
            except ImportError as exc:
                raise RuntimeError(
                    "PaddleOCR is not installed. "
                    "Run: pip install paddleocr>=2.7.0"
                ) from exc

            self._ocr_engine = PaddleOCR(
                use_angle_cls=True,   # Auto-detect rotated text
                lang="en",            # English primary; multilingual supported
                use_gpu=False,        # CPU mode — compatible everywhere
                show_log=False,       # Suppress PaddleOCR's verbose console output
            )
            logger.info("PaddleOCR engine ready.")
        return self._ocr_engine

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_from_file(self, file_path: Path) -> DocumentExtractionResult:
        """
        Extract text from a supported document file.

        Args:
            file_path: Absolute or relative path to a PDF, JPG, or PNG file.

        Returns:
            :class:`DocumentExtractionResult` with per-page text, confidence,
            and extraction metadata.

        Raises:
            FileNotFoundError: *file_path* does not exist.
            ValueError:        File format not supported.
            RuntimeError:      Underlying extraction failure.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()

        if suffix == self.supported_pdf_format:
            return self._extract_from_pdf(file_path)
        elif suffix in self.supported_image_formats:
            return self._extract_from_image(file_path)
        else:
            raise ValueError(
                f"Unsupported file format: '{suffix}'. "
                f"Supported: {self.supported_pdf_format}, "
                f"{', '.join(sorted(self.supported_image_formats))}"
            )

    # ------------------------------------------------------------------
    # PDF extraction
    # ------------------------------------------------------------------

    def _extract_from_pdf(self, pdf_path: Path) -> DocumentExtractionResult:
        """
        Extract text from a PDF using direct extraction with OCR fallback.

        Strategy per page:
        - If ``pdfplumber`` returns ≥ 50 characters → direct extraction (fast).
        - Otherwise → rasterise page at 300 DPI and run PaddleOCR.
        """
        logger.info("Processing PDF: %s", pdf_path.name)
        pages: List[PageText] = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logger.debug("PDF has %d page(s).", total_pages)

                for page_num, page in enumerate(pdf.pages, start=1):
                    raw_text: str | None = page.extract_text()

                    if raw_text and len(raw_text.strip()) >= self._SPARSE_TEXT_THRESHOLD:
                        # ── Fast path: embedded text ─────────────────────
                        page_text = PageText(
                            page_number=page_num,
                            text=raw_text.strip(),
                            confidence=1.0,
                            metadata={"extraction": "direct"},
                        )
                        logger.debug(
                            "Page %d: direct extraction (%d chars).",
                            page_num,
                            len(raw_text),
                        )
                    else:
                        # ── Slow path: OCR fallback ───────────────────────
                        logger.debug("Page %d: sparse text — falling back to OCR.", page_num)
                        page_text = self._ocr_pdf_page(page, page_num)

                    pages.append(page_text)

        except Exception as exc:
            logger.error("PDF extraction error for '%s': %s", pdf_path.name, exc)
            raise RuntimeError(f"Failed to extract text from PDF '{pdf_path.name}': {exc}") from exc

        ocr_count = sum(1 for p in pages if p.metadata.get("extraction") == "ocr")
        method = (
            ExtractionMethod.PDF_OCR
            if total_pages > 0 and ocr_count > total_pages / 2
            else ExtractionMethod.PDF_DIRECT
        )
        avg_conf = sum(p.confidence for p in pages) / len(pages) if pages else 0.0

        logger.info(
            "PDF extraction complete: %d page(s), method=%s, avg_confidence=%.2f",
            total_pages,
            method.value,
            avg_conf,
        )
        return DocumentExtractionResult(
            pages=pages,
            total_pages=total_pages,
            extraction_method=method,
            avg_confidence=avg_conf,
        )

    def _ocr_pdf_page(self, page, page_num: int) -> PageText:
        """
        Rasterise a *pdfplumber* page and run PaddleOCR on it.

        Args:
            page:     A ``pdfplumber.Page`` object.
            page_num: 1-based page number.

        Returns:
            :class:`PageText` with OCR-extracted content.
        """
        # Rasterise to PIL image at 300 DPI for good OCR quality
        pil_image: Image.Image = page.to_image(resolution=300).original

        # Convert PIL → OpenCV (BGR)
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        # Preprocess for better OCR accuracy
        processed = self._preprocess_image(opencv_image)

        return self._run_paddle_ocr(processed, page_num, extraction_tag="ocr")

    # ------------------------------------------------------------------
    # Image extraction
    # ------------------------------------------------------------------

    def _extract_from_image(self, image_path: Path) -> DocumentExtractionResult:
        """
        Extract text from an image file (JPG / PNG) via OCR.

        Args:
            image_path: Path to the image file.

        Returns:
            :class:`DocumentExtractionResult` with a single page.
        """
        logger.info("Processing image: %s", image_path.name)

        image = cv2.imread(str(image_path))
        if image is None:
            raise RuntimeError(f"OpenCV could not load image: {image_path}")

        processed = self._preprocess_image(image)
        page_text = self._run_paddle_ocr(processed, page_num=1, extraction_tag="ocr")

        logger.info(
            "Image OCR complete: %d chars, confidence=%.2f",
            len(page_text.text),
            page_text.confidence,
        )
        return DocumentExtractionResult(
            pages=[page_text],
            total_pages=1,
            extraction_method=ExtractionMethod.IMAGE_OCR,
            avg_confidence=page_text.confidence,
        )

    # ------------------------------------------------------------------
    # OCR runner
    # ------------------------------------------------------------------

    def _run_paddle_ocr(
        self,
        image: np.ndarray,
        page_num: int,
        extraction_tag: str = "ocr",
    ) -> PageText:
        """
        Run PaddleOCR on a preprocessed image and return a PageText.

        Args:
            image:          Preprocessed grayscale or BGR image array.
            page_num:       1-based page number to assign.
            extraction_tag: Value stored in ``metadata["extraction"]``.

        Returns:
            :class:`PageText` with joined OCR text lines and mean confidence.
        """
        try:
            ocr_result = self.ocr_engine.ocr(image, cls=True)
        except Exception as exc:
            logger.warning("PaddleOCR failed on page %d: %s", page_num, exc)
            return PageText(
                page_number=page_num,
                text="",
                confidence=0.0,
                metadata={"extraction": extraction_tag, "error": str(exc)},
            )

        text_lines: List[str] = []
        confidences: List[float] = []

        if ocr_result and ocr_result[0]:
            for line in ocr_result[0]:
                # Each line: [[bbox_points], [text, confidence]]
                if line and len(line) == 2:
                    text_data = line[1]
                    if text_data and text_data[0]:
                        text_lines.append(text_data[0])
                        confidences.append(float(text_data[1]))

        joined_text = "\n".join(text_lines)
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        return PageText(
            page_number=page_num,
            text=joined_text,
            confidence=avg_conf,
            metadata={"extraction": extraction_tag},
        )

    # ------------------------------------------------------------------
    # Image preprocessing
    # ------------------------------------------------------------------

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess an image for improved OCR accuracy.

        Pipeline:
        1. Grayscale conversion (reduces noise dimensionality).
        2. Fast non-local means denoising.
        3. CLAHE contrast enhancement.
        4. Adaptive Gaussian thresholding (binarisation).

        Args:
            image: BGR or grayscale NumPy array.

        Returns:
            Binarised grayscale image ready for OCR.
        """
        # 1. Grayscale
        gray = (
            cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            if len(image.shape) == 3
            else image
        )

        # 2. Denoise
        denoised = cv2.fastNlMeansDenoising(
            gray, None, h=10, templateWindowSize=7, searchWindowSize=21
        )

        # 3. CLAHE contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # 4. Adaptive binarisation
        binary = cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2,
        )

        return binary


# ---------------------------------------------------------------------------
# RAG Agent integration note
# ---------------------------------------------------------------------------
# TODO (RAG Agent): Consume OCRService output as follows:
#
#   from app.services.ocr_service import OCRService
#
#   ocr = OCRService()
#   result = ocr.extract_from_file(pdf_path)
#
#   for page in result.pages:
#       # page.page_number → include in chunk metadata for citations
#       # page.text        → pass to your chunker
#       # page.confidence  → skip/flag pages below threshold
