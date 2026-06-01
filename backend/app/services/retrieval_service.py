"""
Dual-source retrieval service for Lexify-India RAG pipeline.

Queries BOTH ChromaDB collections:
1. document_chunks: user's uploaded document (filtered by document_id)
2. legal_knowledge: pre-seeded Indian legal knowledge (no filter)

Returns AssembledContext for LLM prompt construction.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from app.services.storage_service import StorageService
from app.models.chat import AssembledContext

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Dual-source retrieval coordinator.

    Orchestrates parallel queries to both ChromaDB collections
    and returns assembled context with both source types.
    """

    def __init__(
        self,
        document_storage: StorageService,
        legal_storage: StorageService,
        document_top_k: int = 5,
        legal_top_k: int = 3,
        document_threshold: float = 0.70,
        legal_threshold: float = 0.65,
    ) -> None:
        self.document_storage = document_storage
        self.legal_storage = legal_storage
        self.document_top_k = document_top_k
        self.legal_top_k = legal_top_k
        self.document_threshold = document_threshold
        self.legal_threshold = legal_threshold

    def retrieve(
        self,
        query_embedding: List[float],
        document_id: str,
        document_type: Optional[str] = None,
    ) -> AssembledContext:
        """
        Execute dual-source retrieval for a query.

        Searches document_chunks with document_id filter,
        and legal_knowledge without filter (all entries available).

        Args:
            query_embedding: 768-dim query vector from Gemini
            document_id: User's uploaded document UUID
            document_type: Document type for logging

        Returns:
            AssembledContext with both source types
        """
        logger.info("Dual-source retrieval for document: %s", document_id)

        # PRIMARY: Search user's document (filter by document_id)
        try:
            document_chunks = self.document_storage.search(
                query_embedding=query_embedding,
                document_id=document_id,
                top_k=self.document_top_k,
                similarity_threshold=self.document_threshold,
            )
            logger.debug("Document retrieval: %d chunks", len(document_chunks))
        except Exception as e:
            logger.error("Document retrieval failed: %s", e)
            document_chunks = []

        # SECONDARY: Search legal knowledge (no document_id filter)
        try:
            legal_chunks = self.legal_storage.search(
                query_embedding=query_embedding,
                document_id=None,   # No filter — search all legal knowledge
                top_k=self.legal_top_k,
                similarity_threshold=self.legal_threshold,
            )
            logger.debug("Legal knowledge retrieval: %d chunks", len(legal_chunks))
        except Exception as e:
            logger.error("Legal knowledge retrieval failed: %s", e)
            legal_chunks = []

        context = AssembledContext(
            document_chunks=document_chunks,
            legal_chunks=legal_chunks,
            has_document_context=len(document_chunks) > 0,
            has_legal_context=len(legal_chunks) > 0,
        )

        logger.info(
            "Context assembled: %d doc chunks, %d legal chunks",
            len(document_chunks),
            len(legal_chunks),
        )

        return context
