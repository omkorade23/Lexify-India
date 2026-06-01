"""
Document API endpoints.

Router prefix: /api/documents
Tags:          Documents

Phase 2 — upload_document is FULLY FUNCTIONAL (OCR + RAG ingestion active).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, status

from app.core.config import Settings
from app.core.dependencies import get_settings, RAGServiceDep
from app.core.exceptions import (
    DocumentNotFoundException,
    FileSizeExceededException,
    InvalidFileTypeException,
    OCRExtractionFailedException,
)
from app.models.document import Document, DocumentMetadata, DocumentUploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Documents"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_upload(file: UploadFile, settings: Settings) -> None:
    """
    Validate an incoming upload against configured constraints.

    Raises:
        InvalidFileTypeException: File extension not in ALLOWED_EXTENSIONS.
        FileSizeExceededException: Content-Length exceeds MAX_UPLOAD_SIZE.
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in settings.allowed_extensions_set:
        raise InvalidFileTypeException(
            filename=file.filename or "unknown",
            allowed=settings.allowed_extensions_set,
        )

    if file.size is not None and file.size > settings.MAX_UPLOAD_SIZE:
        raise FileSizeExceededException(
            filename=file.filename or "unknown",
            max_bytes=settings.MAX_UPLOAD_SIZE,
        )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a legal document",
    description=(
        "Accept a legal document (PDF, JPG, PNG), extract text via OCR, "
        "chunk and embed with Gemini, store in ChromaDB, and return structured "
        "results including page count, preview text, and document type."
    ),
)
async def upload_document(
    file: UploadFile = File(..., description="Legal document to upload (PDF, JPG, PNG)."),
    rag_service: RAGServiceDep = ...,
    settings: Settings = Depends(get_settings),
) -> DocumentUploadResponse:
    """
    Upload and process a legal document through the full RAG pipeline.

    **Phase 2 behaviour (active):**
    - Validates file type and size.
    - Persists file to ``settings.UPLOAD_DIR/{uuid}_{filename}``.
    - Extracts text via PaddleOCR (direct PDF text or OCR fallback).
    - Detects document type via keyword heuristics.
    - Chunks text by page, generates 768-dim Gemini embeddings.
    - Stores chunks in ChromaDB document_chunks collection.
    - Registers document in document_registry.json for query-time lookups.

    **Raises:**
    - ``InvalidFileTypeException`` (400): unsupported file format.
    - ``FileSizeExceededException`` (413): file exceeds MAX_UPLOAD_SIZE.
    - ``OCRExtractionFailedException`` (500): extraction pipeline failure.
    """
    _validate_upload(file, settings)

    logger.info("Received upload: %s (%s)", file.filename, file.content_type)

    from app.services.ocr_service import OCRService
    from app.services.document_processor import DocumentProcessor

    ocr_service = OCRService()
    processor = DocumentProcessor(settings=settings, ocr_service=ocr_service)

    try:
        # Step 1: OCR extraction
        document_id, file_path, extraction_result = processor.process_upload(
            file_content=file.file,
            filename=file.filename or "document",
        )

    except ValueError as exc:
        logger.error("Upload validation error: %s", exc)
        raise InvalidFileTypeException(
            filename=file.filename or "unknown",
            allowed=settings.allowed_extensions_set,
        ) from exc
    except Exception as exc:
        logger.error("OCR processing error: %s", exc)
        raise OCRExtractionFailedException(
            document_id="unknown",
            reason=str(exc),
        ) from exc

    # Quality gate — warn on low confidence
    if extraction_result.avg_confidence < settings.OCR_CONFIDENCE_THRESHOLD:
        logger.warning(
            "Low OCR confidence for document_id=%s: %.2f (threshold=%.2f)",
            document_id,
            extraction_result.avg_confidence,
            settings.OCR_CONFIDENCE_THRESHOLD,
        )

    full_text = extraction_result.get_full_text()
    doc_type = processor.get_document_type_hint(full_text)

    try:
        # Step 2: RAG ingestion (chunk + embed + store in ChromaDB)
        ingestion_result = rag_service.ingest_document(
            document_id=document_id,
            extraction_result=extraction_result,
            filename=file.filename or "document",
            file_path=str(file_path),
            document_type=doc_type,
        )

        logger.info(
            "Upload complete: document_id=%s, pages=%d, type=%s, chunks=%d",
            document_id,
            extraction_result.total_pages,
            doc_type,
            ingestion_result["chunks_stored"],
        )

    except Exception as exc:
        logger.error("RAG ingestion error for document_id=%s: %s", document_id, exc)
        # Still return success — document is saved even if embedding fails
        # The registry will not have this document (query will return 404)
        raise OCRExtractionFailedException(
            document_id=document_id,
            reason=f"Embedding/storage failed: {exc}",
        ) from exc

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename or "document",
        num_pages=extraction_result.total_pages,
        extraction_status="completed",
        preview_text=extraction_result.get_preview_text(max_chars=500),
        metadata=DocumentMetadata(
            file_size=file_path.stat().st_size,
            language=extraction_result.language,
            document_type=doc_type,
        ),
    )


@router.get(
    "/{document_id}",
    response_model=Document,
    summary="Get document metadata",
    description=(
        "Retrieve metadata and processing status for a previously uploaded document."
    ),
)
async def get_document(
    document_id: str,
    settings: Settings = Depends(get_settings),  # noqa: ARG001 — kept for DI consistency
) -> Document:
    """
    Retrieve document metadata by ID.

    **Current behaviour (Phase 1 stub):**
    - Accepts any non-empty UUID string.
    - Returns a mock `Document` record.

    TODO (Storage Agent): Replace mock with real registry lookup.
    """
    if not document_id or len(document_id) < 8:
        raise DocumentNotFoundException(document_id)

    return Document(
        document_id=document_id,
        filename="sample_legal_document.pdf",
        upload_date=datetime.now(tz=timezone.utc),
        file_path=f"data/uploads/{document_id}/sample_legal_document.pdf",
        file_size=204_800,
        num_pages=0,
        extraction_status="pending",
        metadata=DocumentMetadata(
            file_size=204_800,
            language="en",
            document_type=None,
        ),
    )
