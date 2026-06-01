"""
FastAPI dependency injection providers.

All service instances are created here and injected into route handlers.
Phase 2 (RAG Pipeline) services are now fully wired.

Usage example:
    @router.post("/api/chat")
    async def query_document(
        request: QueryRequest,
        rag_service: RAGServiceDep,
    ) -> QueryResponse:
        return rag_service.query(request)
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, settings as _settings_singleton


# ---------------------------------------------------------------------------
# Settings dependency
# ---------------------------------------------------------------------------


async def get_settings() -> Settings:
    """
    Provide the application settings singleton.

    Returns the module-level singleton to avoid re-parsing the .env file
    on every request while still being mockable in tests via dependency
    override.
    """
    return _settings_singleton


# Convenience type alias — use in route signatures for clean code:
SettingsDep = Annotated[Settings, Depends(get_settings)]


# ---------------------------------------------------------------------------
# Storage Services (Two Collections)
# ---------------------------------------------------------------------------

from app.services.storage_service import StorageService  # noqa: E402

_document_storage: StorageService | None = None
_legal_storage: StorageService | None = None


async def get_document_storage() -> StorageService:
    """
    Provide a shared StorageService for user document chunks.
    Collection: document_chunks (per-document embeddings, filtered by document_id)
    """
    global _document_storage
    if _document_storage is None:
        _document_storage = StorageService(
            database_path=_settings_singleton.DATABASE_PATH,
            collection_name=_settings_singleton.DOCUMENT_COLLECTION_NAME,
        )
    return _document_storage


async def get_legal_storage() -> StorageService:
    """
    Provide a shared StorageService for pre-seeded legal knowledge.
    Collection: legal_knowledge (searched without document_id filter)
    """
    global _legal_storage
    if _legal_storage is None:
        _legal_storage = StorageService(
            database_path=_settings_singleton.DATABASE_PATH,
            collection_name=_settings_singleton.LEGAL_COLLECTION_NAME,
        )
    return _legal_storage


DocumentStorageDep = Annotated[StorageService, Depends(get_document_storage)]
LegalStorageDep = Annotated[StorageService, Depends(get_legal_storage)]


# ---------------------------------------------------------------------------
# Legacy single-storage dependency (kept for backwards compatibility)
# ---------------------------------------------------------------------------

async def get_storage_service() -> StorageService:
    """Legacy storage dependency — returns document_storage."""
    return await get_document_storage()


StorageServiceDep = Annotated[StorageService, Depends(get_storage_service)]


# ---------------------------------------------------------------------------
# OCR Services
# ---------------------------------------------------------------------------

from app.services.ocr_service import OCRService  # noqa: E402
from app.services.document_processor import DocumentProcessor  # noqa: E402

_ocr_service: OCRService | None = None


async def get_ocr_service() -> OCRService:
    """
    Provide a shared OCRService instance.

    The PaddleOCR engine inside OCRService is lazy-loaded on first use,
    so application startup remains fast even when the model weights are large.
    """
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service


OCRServiceDep = Annotated[OCRService, Depends(get_ocr_service)]


async def get_document_processor(
    settings: Settings = Depends(get_settings),
    ocr_service: OCRService = Depends(get_ocr_service),
) -> DocumentProcessor:
    """Provide a DocumentProcessor (new instance per-request, lightweight)."""
    return DocumentProcessor(settings=settings, ocr_service=ocr_service)


DocumentProcessorDep = Annotated[DocumentProcessor, Depends(get_document_processor)]


# ---------------------------------------------------------------------------
# RAG Pipeline Services
# ---------------------------------------------------------------------------

from app.services.chunking_service import ChunkingService    # noqa: E402
from app.services.embedding_service import EmbeddingService  # noqa: E402
from app.services.retrieval_service import RetrievalService  # noqa: E402
from app.services.llm_service import LLMService              # noqa: E402
from app.services.rag_service import RAGService              # noqa: E402

_chunking_service: ChunkingService | None = None
_embedding_service: EmbeddingService | None = None
_llm_service: LLMService | None = None
_rag_service: RAGService | None = None


async def get_chunking_service() -> ChunkingService:
    """Provide a shared ChunkingService instance."""
    global _chunking_service
    if _chunking_service is None:
        _chunking_service = ChunkingService(
            chunk_size=_settings_singleton.CHUNK_SIZE,
            chunk_overlap=_settings_singleton.CHUNK_OVERLAP,
        )
    return _chunking_service


async def get_embedding_service() -> EmbeddingService:
    """Provide a shared EmbeddingService instance (Gemini API)."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(
            api_key=_settings_singleton.GEMINI_API_KEY,
            model=_settings_singleton.EMBEDDING_MODEL,
        )
    return _embedding_service


async def get_retrieval_service(
    document_storage: StorageService = Depends(get_document_storage),
    legal_storage: StorageService = Depends(get_legal_storage),
) -> RetrievalService:
    """Provide a RetrievalService wired to both ChromaDB collections."""
    return RetrievalService(
        document_storage=document_storage,
        legal_storage=legal_storage,
        document_top_k=_settings_singleton.DOCUMENT_TOP_K,
        legal_top_k=_settings_singleton.LEGAL_TOP_K,
        document_threshold=_settings_singleton.DOCUMENT_SIMILARITY_THRESHOLD,
        legal_threshold=_settings_singleton.LEGAL_SIMILARITY_THRESHOLD,
    )


async def get_llm_service() -> LLMService:
    """Provide a shared LLMService instance (Gemini 1.5-flash)."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService(
            api_key=_settings_singleton.GEMINI_API_KEY,
            model=_settings_singleton.LLM_MODEL,
            max_tokens=_settings_singleton.LLM_MAX_TOKENS,
        )
    return _llm_service


async def get_rag_service(
    chunking: ChunkingService = Depends(get_chunking_service),
    embedding: EmbeddingService = Depends(get_embedding_service),
    retrieval: RetrievalService = Depends(get_retrieval_service),
    llm: LLMService = Depends(get_llm_service),
    document_storage: StorageService = Depends(get_document_storage),
) -> RAGService:
    """Provide a RAGService orchestrating the full pipeline."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService(
            chunking_service=chunking,
            embedding_service=embedding,
            retrieval_service=retrieval,
            llm_service=llm,
            document_storage=document_storage,
            registry_path=_settings_singleton.DOCUMENT_REGISTRY_PATH,
        )
    return _rag_service


RAGServiceDep = Annotated[RAGService, Depends(get_rag_service)]
