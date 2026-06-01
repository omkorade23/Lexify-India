"""
Vector storage service for document embeddings using ChromaDB.

This service manages:
- Collection creation and management
- Embedding storage with rich metadata
- Similarity search with document_id filtering
- Chunk retrieval and document-level deletion

Design contract for the RAG Pipeline Agent
------------------------------------------
1. You generate embeddings (we just store them).
2. You call ``store_chunks(chunks, embeddings)`` after embedding.
3. You call ``search(query_embedding, document_id, ...)`` at query time.
4. We return dicts with all the metadata you need to build citations.

Never import this module directly in route handlers — use the
``get_storage_service`` dependency from ``app.core.dependencies``.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


class DocumentChunk:
    """
    Lightweight value object that carries a single document chunk and its
    metadata. Created by the RAG Agent's chunking step and passed to
    ``StorageService.store_chunks()`` alongside the corresponding embeddings.

    Attributes
    ----------
    chunk_id:       Globally unique ID for this chunk (e.g. ``"{doc_id}_chunk_{n}"``).
    document_id:    UUID of the parent document (used for filtering in search).
    text:           Raw text content of the chunk.
    page_number:    1-indexed page where this chunk begins.
    section:        Section/article heading, if detected (optional).
    clause_number:  Legal clause identifier, e.g. ``"3.2.1"`` (optional).
    start_char:     Character offset in the full document text (inclusive).
    end_char:       Character offset in the full document text (exclusive).
    metadata:       Arbitrary extra key-value pairs stored alongside the chunk.
    """

    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        text: str,
        page_number: int,
        section: Optional[str] = None,
        clause_number: Optional[str] = None,
        start_char: int = 0,
        end_char: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.text = text
        self.page_number = page_number
        self.section = section
        self.clause_number = clause_number
        self.start_char = start_char
        self.end_char = end_char
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return (
            f"DocumentChunk(chunk_id={self.chunk_id!r}, "
            f"document_id={self.document_id!r}, "
            f"page={self.page_number})"
        )


# ---------------------------------------------------------------------------
# Storage service
# ---------------------------------------------------------------------------


class StorageService:
    """
    ChromaDB storage service for vector embeddings.

    Provides persistent storage and retrieval of document chunk embeddings
    with rich metadata. Designed as the single integration point between the
    RAG Pipeline Agent (caller) and ChromaDB (storage layer).

    Thread-safety
    -------------
    ChromaDB's ``PersistentClient`` is thread-safe by design; this class adds
    no shared mutable state, so a single instance can be shared across
    FastAPI's async worker threads safely.

    Parameters
    ----------
    database_path:    Filesystem path for ChromaDB's SQLite + binary stores.
    collection_name:  ChromaDB collection name (default: ``"legal_documents"``).
    """

    def __init__(
        self,
        database_path: str,
        collection_name: str = "legal_documents",
    ) -> None:
        self.database_path = Path(database_path)
        self.collection_name = collection_name

        # Ensure the storage directory exists.
        self.database_path.mkdir(parents=True, exist_ok=True)

        # Initialise a persistent ChromaDB client.
        self.client = chromadb.PersistentClient(
            path=str(self.database_path),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,  # Convenient during development; restrict in prod.
            ),
        )

        # Get or create the collection.
        self.collection = self._get_or_create_collection()

        logger.info(
            "StorageService ready | collection=%s | path=%s",
            self.collection_name,
            self.database_path,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_or_create_collection(self) -> chromadb.Collection:
        """Return the existing collection or create a fresh one."""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info("Loaded existing ChromaDB collection: %s", self.collection_name)
        except Exception:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Legal document chunk embeddings — Lexify-India"},
            )
            logger.info("Created new ChromaDB collection: %s", self.collection_name)
        return collection

    # ------------------------------------------------------------------
    # Public API — called by the RAG Pipeline Agent
    # ------------------------------------------------------------------

    def store_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ) -> Dict[str, Any]:
        """
        Persist document chunks together with their embedding vectors.

        Parameters
        ----------
        chunks:      List of ``DocumentChunk`` objects (order must match embeddings).
        embeddings:  List of float vectors from the embedding model, one per chunk.

        Returns
        -------
        dict with keys:
            - ``stored``       — number of chunks written.
            - ``document_ids`` — unique document IDs contained in this batch.
            - ``collection``   — collection name (for logging/debugging).

        Raises
        ------
        ValueError
            If ``len(chunks) != len(embeddings)`` or if ``chunks`` is empty.
        """
        if not chunks:
            logger.warning("store_chunks called with empty chunk list — nothing stored.")
            return {"stored": 0, "document_ids": [], "collection": self.collection_name}

        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks/embeddings length mismatch: "
                f"{len(chunks)} chunks vs {len(embeddings)} embeddings."
            )

        # ChromaDB requires metadata values to be str | int | float | bool.
        # We coerce everything to the right primitive type here so callers
        # don't need to worry about it.
        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for chunk in chunks:
            ids.append(chunk.chunk_id)
            documents.append(chunk.text)
            metadatas.append(
                {
                    "document_id": chunk.document_id,
                    "page_number": int(chunk.page_number),
                    "section": str(chunk.section or ""),
                    "clause_number": str(chunk.clause_number or ""),
                    "start_char": int(chunk.start_char),
                    "end_char": int(chunk.end_char),
                    # Spread any custom metadata; values must be primitive.
                    **{k: v for k, v in chunk.metadata.items()},
                }
            )

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
        except Exception as exc:
            logger.error("ChromaDB add() failed: %s", exc, exc_info=True)
            raise

        unique_doc_ids = list({c.document_id for c in chunks})
        logger.info(
            "Stored %d chunks across %d document(s) → collection=%s",
            len(chunks),
            len(unique_doc_ids),
            self.collection_name,
        )
        return {
            "stored": len(chunks),
            "document_ids": unique_doc_ids,
            "collection": self.collection_name,
        }

    def search(
        self,
        query_embedding: List[float],
        document_id: Optional[str] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most semantically similar chunks for a query vector,
        scoped to a single document.

        The default distance metric for ChromaDB collections is L2 (Euclidean).
        We convert distance → similarity via:  ``similarity = 1 / (1 + distance)``
        This maps [0, ∞) distance to (0, 1] similarity.

        Parameters
        ----------
        query_embedding:     Float vector of the user's question.
        document_id:         Restricts results to chunks of this document only.
        top_k:               Maximum number of results to return.
        similarity_threshold:
                             Minimum similarity score (inclusive). Chunks below
                             this score are excluded. Set to ``0.0`` in tests.

        Returns
        -------
        List of dicts, each containing:
            - ``chunk_id``        — chunk identifier
            - ``text``            — raw chunk text
            - ``metadata``        — full metadata dict
            - ``similarity_score``— float in (0, 1]
            - ``page_number``     — extracted from metadata for convenience
            - ``section``         — extracted from metadata for convenience
        """
        try:
            query_kwargs: Dict[str, Any] = dict(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )
            if document_id is not None:
                query_kwargs["where"] = {"document_id": document_id}

            results = self.collection.query(**query_kwargs)
        except Exception as exc:
            logger.error("ChromaDB query() failed: %s", exc, exc_info=True)
            raise

        chunks: List[Dict[str, Any]] = []

        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                # L2 distance → similarity score in (0, 1].
                similarity = 1.0 / (1.0 + distance)

                if similarity < similarity_threshold:
                    continue  # Skip chunks below the threshold.

                meta = results["metadatas"][0][i]
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "text": results["documents"][0][i],
                        "metadata": meta,
                        "similarity_score": round(similarity, 6),
                        "page_number": int(meta.get("page_number", 0)),
                        "section": str(meta.get("section", "")),
                    }
                )

        logger.info(
            "search() → %d chunks above threshold %.2f | document=%s",
            len(chunks),
            similarity_threshold,
            document_id or "ALL",
        )
        return chunks

    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve **all** stored chunks for a given document (no embedding needed).

        Useful for debugging, re-indexing, or building a full document view.

        Parameters
        ----------
        document_id:  UUID of the target document.

        Returns
        -------
        List of dicts, each containing:
            - ``chunk_id``  — chunk identifier
            - ``text``      — raw chunk text
            - ``metadata``  — full metadata dict
        """
        try:
            results = self.collection.get(
                where={"document_id": document_id},
                include=["documents", "metadatas"],
            )
        except Exception as exc:
            logger.error("ChromaDB get() failed: %s", exc, exc_info=True)
            raise

        chunks: List[Dict[str, Any]] = []
        if results["ids"]:
            for i, chunk_id in enumerate(results["ids"]):
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "text": results["documents"][i],
                        "metadata": results["metadatas"][i],
                    }
                )

        logger.info(
            "get_document_chunks() → %d chunks | document=%s",
            len(chunks),
            document_id,
        )
        return chunks

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete **all** chunks associated with a document.

        Called when a document is removed from the platform so we don't
        accumulate orphaned embeddings.

        Parameters
        ----------
        document_id:  UUID of the document to purge.

        Returns
        -------
        dict with keys:
            - ``deleted``     — number of chunks removed (0 if not found).
            - ``document_id`` — echoed back for confirmation.
        """
        try:
            # Fetch only IDs — avoids loading embedding data unnecessarily.
            results = self.collection.get(
                where={"document_id": document_id},
                include=[],
            )
        except Exception as exc:
            logger.error("ChromaDB get() during delete failed: %s", exc, exc_info=True)
            raise

        if not results["ids"]:
            logger.warning(
                "delete_document() — no chunks found for document=%s", document_id
            )
            return {"deleted": 0, "document_id": document_id}

        try:
            self.collection.delete(ids=results["ids"])
        except Exception as exc:
            logger.error("ChromaDB delete() failed: %s", exc, exc_info=True)
            raise

        deleted_count = len(results["ids"])
        logger.info(
            "Deleted %d chunks | document=%s", deleted_count, document_id
        )
        return {"deleted": deleted_count, "document_id": document_id}

    def collection_stats(self) -> Dict[str, Any]:
        """
        Return basic statistics about the current collection.

        Returns
        -------
        dict with keys:
            - ``collection_name``  — collection identifier
            - ``total_chunks``     — total number of stored chunks
            - ``database_path``    — filesystem path of the ChromaDB store
        """
        try:
            count = self.collection.count()
        except Exception as exc:
            logger.error("ChromaDB count() failed: %s", exc, exc_info=True)
            raise

        return {
            "collection_name": self.collection_name,
            "total_chunks": count,
            "database_path": str(self.database_path),
        }

    def reset_collection(self) -> Dict[str, str]:
        """
        Drop and recreate the collection — **development/testing use only**.

        WARNING: This permanently deletes all stored embeddings. There is no
        undo. The ``--reset`` guard in ``scripts/init_chroma.py`` requires an
        interactive confirmation before calling this.

        Returns
        -------
        dict with keys:
            - ``status``     — ``"collection_reset"``
            - ``collection`` — collection name
        """
        logger.warning(
            "reset_collection() called — ALL data in '%s' will be deleted.",
            self.collection_name,
        )
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Legal document chunk embeddings — Lexify-India"},
            )
        except Exception as exc:
            logger.error("reset_collection() failed: %s", exc, exc_info=True)
            raise

        logger.info("Collection recreated: %s", self.collection_name)
        return {"status": "collection_reset", "collection": self.collection_name}


# ---------------------------------------------------------------------------
# Integration guide for the RAG Pipeline Agent
# ---------------------------------------------------------------------------
#
# IMPORT via dependency injection (never directly):
#
#   from app.core.dependencies import get_storage_service, StorageServiceDep
#
#   # In a FastAPI route:
#   async def query_document(
#       ...,
#       storage: StorageServiceDep,
#   ) -> QueryResponse:
#       results = storage.search(
#           query_embedding=query_vector,
#           document_id=req.document_id,
#           top_k=5,
#           similarity_threshold=settings.SIMILARITY_THRESHOLD,
#       )
#
# STORE CHUNKS (called after OCR + chunking + embedding):
#
#   chunks = [
#       DocumentChunk(
#           chunk_id=f"{doc_id}_chunk_{i}",
#           document_id=doc_id,
#           text=chunk_text,
#           page_number=page,
#           section=detected_section,
#           clause_number=detected_clause,
#           start_char=start,
#           end_char=end,
#       )
#       for i, (chunk_text, page, ...) in enumerate(your_chunks)
#   ]
#   embeddings = your_embedding_model.encode([c.text for c in chunks]).tolist()
#   storage.store_chunks(chunks, embeddings)
#
# METADATA SCHEMA (what each result dict contains):
#   {
#       "chunk_id":        "doc-uuid_chunk_0",
#       "text":            "...",
#       "metadata": {
#           "document_id":    "doc-uuid",
#           "page_number":    1,
#           "section":        "Clause 3 — Termination",
#           "clause_number":  "3.1",
#           "start_char":     1024,
#           "end_char":       1824,
#           # + any extra keys you passed via DocumentChunk.metadata
#       },
#       "similarity_score": 0.871234,
#       "page_number":      1,        # convenience alias
#       "section":          "...",    # convenience alias
#   }
