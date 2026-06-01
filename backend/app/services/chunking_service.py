"""
Document text chunking service with metadata preservation.

Splits document text into overlapping chunks while preserving:
- Page numbers (for citation accuracy)
- Section information
- Document structure

Uses LangChain RecursiveCharacterTextSplitter for robust splitting.
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.storage_service import DocumentChunk

logger = logging.getLogger(__name__)


class ChunkingService:
    """
    Document chunking service for RAG pipeline.

    Splits extracted document text into chunks that preserve
    page numbers and structural metadata for citation accuracy.
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
            is_separator_regex=False,
        )

    def chunk_document(
        self,
        pages: list,  # List of PageText objects from OCRService
        document_id: str,
        document_type: Optional[str] = "legal_document",
    ) -> List[DocumentChunk]:
        """
        Chunk document pages into overlapping text segments.

        Each chunk preserves:
        - The page number it came from (critical for citations)
        - Document ID for vector store filtering
        - Section detection (best-effort from text patterns)

        Args:
            pages: List of PageText objects from OCRService
            document_id: Parent document UUID
            document_type: Detected document type from processor

        Returns:
            List of DocumentChunk objects ready for embedding
        """
        all_chunks: List[DocumentChunk] = []

        for page in pages:
            if not page.text or len(page.text.strip()) < 20:
                logger.debug("Skipping empty page %d", page.page_number)
                continue

            # Split page text into chunks
            page_text_chunks = self.splitter.split_text(page.text)

            char_offset = 0
            for i, chunk_text in enumerate(page_text_chunks):
                # Detect section heading if present
                section = self._detect_section(chunk_text)

                # Track character positions for metadata
                start_char = page.text.find(chunk_text[:50], char_offset)
                if start_char == -1:
                    start_char = char_offset
                end_char = start_char + len(chunk_text)
                char_offset = max(0, end_char - self.chunk_overlap)

                chunk = DocumentChunk(
                    chunk_id=f"{document_id}_p{page.page_number}_c{i}",
                    document_id=document_id,
                    text=chunk_text.strip(),
                    page_number=page.page_number,
                    section=section,
                    clause_number=self._detect_clause_number(chunk_text),
                    start_char=start_char,
                    end_char=end_char,
                    metadata={
                        "source_type": "document",
                        "document_type": document_type or "legal_document",
                        "chunk_index": i,
                        "page_chunk_count": len(page_text_chunks),
                    },
                )

                all_chunks.append(chunk)

        logger.info(
            "Chunked document %s: %d pages → %d chunks",
            document_id,
            len(pages),
            len(all_chunks),
        )

        return all_chunks

    def _detect_section(self, text: str) -> Optional[str]:
        """Detect section heading from chunk text using regex patterns."""
        patterns = [
            r"^(Clause\s+\d+[\.\d]*[^.\n]*)",
            r"^(Article\s+\d+[\.\d]*[^.\n]*)",
            r"^(Section\s+\d+[\.\d]*[^.\n]*)",
            r"^(\d+\.\s+[A-Z][^.\n]{5,50})",
            r"^([A-Z][A-Z\s]{5,40}:)",
        ]

        first_line = text.strip().split("\n")[0]
        for pattern in patterns:
            match = re.match(pattern, first_line, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _detect_clause_number(self, text: str) -> Optional[str]:
        """Extract clause number from text if present."""
        match = re.match(
            r"^(Clause|Article|Section)\s+(\d+[\.\d]*)",
            text.strip(),
            re.IGNORECASE,
        )
        if match:
            return match.group(2)

        match = re.match(r"^(\d+\.\d+)", text.strip())
        if match:
            return match.group(1)

        return None
