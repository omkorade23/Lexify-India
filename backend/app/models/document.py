"""
Pydantic models for legal documents.

These models define the API contract for document-related operations and
must remain in sync with the Lexify-India PRD specifications.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DocumentMetadata(BaseModel):
    """Supplementary metadata attached to every document record."""

    file_size: int = Field(..., gt=0, description="File size in bytes.")
    language: Optional[str] = Field(
        default="en",
        description="ISO 639-1 language code of the document content.",
    )
    document_type: Optional[str] = Field(
        default=None,
        description=(
            "Inferred document category, e.g., 'contract', 'affidavit', "
            "'court_order'. Populated by OCR Agent in Phase 2."
        ),
    )


class Document(BaseModel):
    """
    Full document record — returned when fetching an existing document.

    The `extraction_status` lifecycle:
        pending → processing → completed | failed
    """

    document_id: str = Field(
        ...,
        description="UUID v4 string uniquely identifying this document.",
    )
    filename: str = Field(..., description="Original filename as uploaded.")
    upload_date: datetime = Field(
        ...,
        description="UTC timestamp when the document was received by the API.",
    )
    file_path: str = Field(
        ...,
        description=(
            "Relative path under UPLOAD_DIR where the file is stored. "
            "Populated by the Storage Agent in Phase 2."
        ),
    )
    file_size: int = Field(..., gt=0, description="File size in bytes.")
    num_pages: int = Field(
        ...,
        ge=0,
        description="Page count extracted by OCR Agent. 0 while pending.",
    )
    extraction_status: str = Field(
        ...,
        description="OCR pipeline status: 'pending' | 'processing' | 'completed' | 'failed'.",
    )
    metadata: DocumentMetadata

    @field_validator("extraction_status")
    @classmethod
    def validate_extraction_status(cls, value: str) -> str:
        allowed = {"pending", "processing", "completed", "failed"}
        if value not in allowed:
            raise ValueError(f"extraction_status must be one of {allowed}.")
        return value


class DocumentUploadResponse(BaseModel):
    """
    Slim response returned immediately after a successful upload.

    This is intentionally lighter than Document — the caller does not
    need the full record, only enough to track async processing.
    """

    document_id: str = Field(
        ...,
        description="UUID assigned to the newly uploaded document.",
    )
    filename: str = Field(..., description="Original filename as uploaded.")
    num_pages: int = Field(
        default=0,
        ge=0,
        description="Known page count at upload time. Usually 0 (pending OCR).",
    )
    extraction_status: str = Field(
        default="pending",
        description="Initial OCR pipeline status — always 'pending' at upload.",
    )
    preview_text: Optional[str] = Field(
        default=None,
        description=(
            "Short preview of extracted text (first ~200 chars). "
            "Null until OCR completes."
        ),
    )
    metadata: DocumentMetadata
