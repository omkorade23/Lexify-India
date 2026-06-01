"""
RAG orchestration service — the core intelligence layer.

Coordinates:
- Document ingestion: OCR output → chunks → embeddings → storage
- Query processing: question → embeddings → dual retrieval → LLM → response

This is the primary service called by API endpoints.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.storage_service import StorageService
from app.models.chat import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)


class RAGService:
    """
    Central RAG orchestration service.

    Wires together all pipeline components:
    Chunking → Embedding → Storage (ingestion path)
    Embedding → Retrieval → Generation (query path)
    """

    def __init__(
        self,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService,
        retrieval_service: RetrievalService,
        llm_service: LLMService,
        document_storage: StorageService,
        registry_path: str = "data/document_registry.json",
    ) -> None:
        self.chunking = chunking_service
        self.embedding = embedding_service
        self.retrieval = retrieval_service
        self.llm = llm_service
        self.document_storage = document_storage
        self.registry_path = Path(registry_path)

    def ingest_document(
        self,
        document_id: str,
        extraction_result,   # DocumentExtractionResult from OCRService
        filename: str,
        file_path: str,
        document_type: Optional[str] = "legal_document",
    ) -> dict:
        """
        Process document after OCR: chunk → embed → store.

        Called by upload endpoint after OCR extraction.

        Args:
            document_id: UUID for the document
            extraction_result: OCR output with pages and text
            filename: Original filename
            file_path: Path to saved file
            document_type: Detected document type

        Returns:
            Ingestion stats dict
        """
        logger.info("Starting document ingestion: %s", document_id)

        # Step 1: Chunk the document pages
        chunks = self.chunking.chunk_document(
            pages=extraction_result.pages,
            document_id=document_id,
            document_type=document_type,
        )

        if not chunks:
            logger.warning("No chunks generated for %s", document_id)
            # Still register the document even if no chunks
            self._update_registry(
                document_id=document_id,
                filename=filename,
                file_path=file_path,
                document_type=document_type,
                num_pages=extraction_result.total_pages,
                chunks_stored=0,
            )
            return {"chunks_stored": 0, "status": "no_content", "document_id": document_id}

        # Step 2: Generate embeddings for all chunks
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding.embed_batch(chunk_texts, task_type="retrieval_document")

        # Step 3: Store in ChromaDB document_chunks collection
        store_result = self.document_storage.store_chunks(
            chunks=chunks,
            embeddings=embeddings,
        )

        # Step 4: Save to document registry for existence checks
        self._update_registry(
            document_id=document_id,
            filename=filename,
            file_path=file_path,
            document_type=document_type,
            num_pages=extraction_result.total_pages,
            chunks_stored=store_result["stored"],
        )

        logger.info(
            "Document ingestion complete: %s, %d chunks stored",
            document_id,
            store_result["stored"],
        )

        return {
            "chunks_stored": store_result["stored"],
            "status": "completed",
            "document_id": document_id,
        }

    def query(self, request: QueryRequest) -> QueryResponse:
        """
        Process a user query with dual-source retrieval.

        Args:
            request: QueryRequest with document_id, question, history

        Returns:
            QueryResponse with grounded answer and citations
        """
        logger.info("Processing query for document: %s", request.document_id)

        # Validate document exists
        doc_info = self._get_document_info(request.document_id)
        if not doc_info:
            raise ValueError(f"Document not found: {request.document_id}")

        # Step 1: Embed user query
        query_embedding = self.embedding.embed_query(request.question)

        # Step 2: Dual-source retrieval
        context = self.retrieval.retrieve(
            query_embedding=query_embedding,
            document_id=request.document_id,
            document_type=doc_info.get("document_type"),
        )

        # Step 3: Generate response
        response = self.llm.generate_response(
            question=request.question,
            context=context,
            conversation_history=request.conversation_history,
        )

        logger.info(
            "Query complete: confidence=%s, citations=%d",
            response.confidence,
            len(response.citations),
        )

        return response

    def document_exists(self, document_id: str) -> bool:
        """Check if document has been processed and registered."""
        return self._get_document_info(document_id) is not None

    def _update_registry(
        self,
        document_id: str,
        filename: str,
        file_path: str,
        document_type: Optional[str],
        num_pages: int,
        chunks_stored: int,
    ) -> None:
        """Update document registry JSON file."""
        registry = self._load_registry()

        registry[document_id] = {
            "filename": filename,
            "file_path": str(file_path),
            "document_type": document_type,
            "num_pages": num_pages,
            "upload_date": datetime.utcnow().isoformat() + "Z",
            "extraction_status": "completed",
            "chunks_stored": chunks_stored,
        }

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w") as f:
            json.dump(registry, f, indent=2)

    def _get_document_info(self, document_id: str) -> Optional[dict]:
        """Get document metadata from registry."""
        registry = self._load_registry()
        return registry.get(document_id)

    def _load_registry(self) -> dict:
        """Load document registry from JSON file."""
        if not self.registry_path.exists():
            return {}
        try:
            with open(self.registry_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
