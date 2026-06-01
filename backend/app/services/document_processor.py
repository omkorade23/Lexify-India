"""
Document processing coordinator.

This module is the high-level orchestrator called by the API upload endpoint.
It handles:
  - File validation and persistence (UUID-prefixed filenames)
  - OCR invocation via OCRService
  - Heuristic document-type detection
  - Clean error handling with file cleanup on failure

The returned tuple ``(document_id, file_path, extraction_result)`` is the
contract between the API layer and the OCR layer.  The RAG Agent will later
consume `extraction_result` for chunking and embedding.
"""

from __future__ import annotations

import logging
import shutil
import uuid
from pathlib import Path
from typing import BinaryIO, Optional, Tuple

from app.core.config import Settings
from app.services.ocr_service import DocumentExtractionResult, OCRService

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    High-level document upload and processing coordinator.

    Responsibilities:
    - Validate and save uploaded bytes to ``settings.UPLOAD_DIR``.
    - Delegate text extraction to :class:`~app.services.ocr_service.OCRService`.
    - Detect document type from extracted text via keyword heuristics.
    - Return a structured result to the API layer.

    This class is **not** responsible for chunking, embedding, or vector
    storage — those belong to the RAG Agent.
    """

    # Keyword maps for heuristic document-type detection.
    # Ordered from most-specific to least-specific so the first match wins.
    _TYPE_KEYWORDS: list[tuple[str, list[str]]] = [
        ("rental_agreement", [
            "rental agreement", "tenancy agreement", "lease deed",
            "landlord", "tenant", "monthly rent", "security deposit",
            "lock-in period",
        ]),
        ("employment_contract", [
            "employment agreement", "offer letter", "appointment letter",
            "employer", "employee", "salary", "probation period",
            "notice period", "designation",
        ]),
        ("nda", [
            "non-disclosure agreement", "non disclosure", "nda",
            "confidentiality agreement", "proprietary information",
            "trade secret",
        ]),
        ("property_document", [
            "sale deed", "sale agreement", "purchase agreement",
            "conveyance deed", "property", "plot no", "survey number",
            "stamp duty",
        ]),
        ("court_notice", [
            "court", "summons", "legal notice", "petition",
            "plaintiff", "defendant", "applicant", "respondent",
            "high court", "supreme court", "district court",
        ]),
    ]

    def __init__(self, settings: Settings, ocr_service: OCRService) -> None:
        self.settings = settings
        self.ocr_service = ocr_service
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("DocumentProcessor initialised. upload_dir=%s", self.upload_dir)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_upload(
        self,
        file_content: BinaryIO,
        filename: str,
    ) -> Tuple[str, Path, DocumentExtractionResult]:
        """
        Persist an uploaded file and extract its text content.

        Args:
            file_content: Binary file-like object (e.g., ``UploadFile.file``).
            filename:     Original filename provided by the client.

        Returns:
            A 3-tuple ``(document_id, saved_path, extraction_result)``:
              - ``document_id``      — UUID string assigned to this document.
              - ``saved_path``       — Absolute path where the file was saved.
              - ``extraction_result``— Full OCR result for downstream use.

        Raises:
            ValueError:     File extension not in ``settings.ALLOWED_EXTENSIONS``.
            RuntimeError:   File save or OCR extraction failure; uploaded file
                            is cleaned up automatically on error.
        """
        document_id = str(uuid.uuid4())
        suffix = Path(filename).suffix.lower()

        # Extension validation (guard in addition to the API-level check)
        if suffix not in self.settings.allowed_extensions_set:
            raise ValueError(
                f"Unsupported file type '{suffix}'. "
                f"Allowed: {', '.join(sorted(self.settings.allowed_extensions_set))}"
            )

        # Build a safe, collision-free filename
        safe_filename = f"{document_id}_{filename}"
        file_path = self.upload_dir / safe_filename

        try:
            # ── Persist file ─────────────────────────────────────────────
            with open(file_path, "wb") as dest:
                shutil.copyfileobj(file_content, dest)

            file_size_bytes = file_path.stat().st_size
            logger.info(
                "Saved uploaded file: %s (%d bytes, document_id=%s)",
                safe_filename,
                file_size_bytes,
                document_id,
            )

            # ── Extract text ─────────────────────────────────────────────
            logger.info("Starting OCR extraction for document_id=%s", document_id)
            extraction_result = self.ocr_service.extract_from_file(file_path)

            logger.info(
                "Extraction complete: document_id=%s, pages=%d, "
                "method=%s, confidence=%.2f",
                document_id,
                extraction_result.total_pages,
                extraction_result.extraction_method.value,
                extraction_result.avg_confidence,
            )

            return document_id, file_path, extraction_result

        except Exception as exc:
            # Clean up partially-written file to avoid orphans
            if file_path.exists():
                file_path.unlink(missing_ok=True)
                logger.debug("Cleaned up failed upload: %s", file_path)

            logger.error(
                "Document processing failed for document_id=%s: %s",
                document_id,
                exc,
            )
            raise RuntimeError(f"Failed to process document '{filename}': {exc}") from exc

    # ------------------------------------------------------------------
    # Heuristic document-type detection
    # ------------------------------------------------------------------

    def get_document_type_hint(self, text: str) -> Optional[str]:
        """
        Heuristically detect the legal document type from extracted text.

        Uses simple keyword matching against a curated set of Indian legal
        document vocabulary.  Returns the first matching category or the
        generic fallback ``"legal_document"``.

        Args:
            text: Full extracted text from the document.

        Returns:
            One of: ``"rental_agreement"``, ``"employment_contract"``,
            ``"nda"``, ``"property_document"``, ``"court_notice"``,
            ``"legal_document"``.
        """
        text_lower = text.lower()

        for doc_type, keywords in self._TYPE_KEYWORDS:
            if any(kw in text_lower for kw in keywords):
                logger.debug("Document type detected: %s", doc_type)
                return doc_type

        logger.debug("No specific document type matched; using 'legal_document'.")
        return "legal_document"
