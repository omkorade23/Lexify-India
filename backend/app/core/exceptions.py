"""
Custom exception hierarchy for Lexify-India.

All domain exceptions inherit from LexifyException, which carries:
  - code    : machine-readable error code (snake_case)
  - message : human-readable description
  - details : optional extra context (e.g., filename, id)

The global exception handler in main.py converts these to structured
JSON HTTP responses so every API consumer gets a consistent error shape:

    {
        "error": {
            "code": "document_not_found",
            "message": "No document with id '...' exists.",
            "details": "document_id=abc123"
        }
    }
"""

from __future__ import annotations


class LexifyException(Exception):
    """Base exception for all Lexify-India domain errors."""

    def __init__(
        self,
        code: str,
        message: str,
        details: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code: str = code
        self.message: str = message
        self.details: str | None = details

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"code={self.code!r}, "
            f"message={self.message!r}, "
            f"details={self.details!r})"
        )


# ---------------------------------------------------------------------------
# Document-related exceptions
# ---------------------------------------------------------------------------


class DocumentNotFoundException(LexifyException):
    """Raised when a requested document does not exist in storage."""

    def __init__(self, document_id: str) -> None:
        super().__init__(
            code="document_not_found",
            message=f"No document with id '{document_id}' exists.",
            details=f"document_id={document_id}",
        )


class InvalidFileTypeException(LexifyException):
    """Raised when an uploaded file has an unsupported extension or MIME type."""

    def __init__(self, filename: str, allowed: set[str]) -> None:
        allowed_str = ", ".join(sorted(allowed))
        super().__init__(
            code="invalid_file_type",
            message=(
                f"File '{filename}' has an unsupported format. "
                f"Allowed types: {allowed_str}."
            ),
            details=f"filename={filename}",
        )


class FileSizeExceededException(LexifyException):
    """Raised when an uploaded file exceeds the configured size limit."""

    def __init__(self, filename: str, max_bytes: int) -> None:
        max_mb = max_bytes / (1024 * 1024)
        super().__init__(
            code="file_size_exceeded",
            message=(
                f"File '{filename}' exceeds the maximum upload size of "
                f"{max_mb:.0f} MB."
            ),
            details=f"filename={filename}, max_bytes={max_bytes}",
        )


# ---------------------------------------------------------------------------
# Processing exceptions
# ---------------------------------------------------------------------------


class OCRExtractionFailedException(LexifyException):
    """
    Raised when the OCR pipeline fails to extract text from a document.

    TODO (OCR Agent): Raise this exception inside ocr_service.py when
    PaddleOCR or any other OCR engine returns an unrecoverable error.
    """

    def __init__(self, document_id: str, reason: str | None = None) -> None:
        super().__init__(
            code="ocr_extraction_failed",
            message=(
                f"OCR extraction failed for document '{document_id}'. "
                f"{reason or 'Unknown error.'}"
            ),
            details=f"document_id={document_id}",
        )


class RAGPipelineException(LexifyException):
    """
    Raised when the RAG retrieval / generation pipeline encounters an error.

    TODO (RAG Agent): Raise this exception inside rag_service.py when
    embedding or LLM generation fails.
    """

    def __init__(self, reason: str | None = None) -> None:
        super().__init__(
            code="rag_pipeline_error",
            message=f"RAG pipeline error. {reason or 'Unknown error.'}",
        )


# ---------------------------------------------------------------------------
# Infrastructure / operational exceptions
# ---------------------------------------------------------------------------


class RateLimitExceededException(LexifyException):
    """Raised when an API rate limit is exceeded (Gemini, etc.)."""

    def __init__(self, service: str = "API") -> None:
        super().__init__(
            code="rate_limit_exceeded",
            message=f"{service} rate limit exceeded. Please retry after a short delay.",
            details=f"service={service}",
        )


class VectorStoreException(LexifyException):
    """
    Raised when the ChromaDB vector store operation fails.

    TODO (Vector DB Agent): Raise this exception inside storage_service.py
    when ChromaDB queries or inserts fail.
    """

    def __init__(self, operation: str, reason: str | None = None) -> None:
        super().__init__(
            code="vector_store_error",
            message=(
                f"Vector store operation '{operation}' failed. "
                f"{reason or 'Unknown error.'}"
            ),
            details=f"operation={operation}",
        )
