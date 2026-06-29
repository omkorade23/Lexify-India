"""
General legal chat endpoint.

Handles user queries that are not tied to a specific document.
Uses only the pre-seeded legal_knowledge ChromaDB collection.
Returns responses in the same QueryResponse format as document-specific chat.
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from app.core.config import Settings
from app.core.dependencies import get_embedding_service, get_legal_storage, get_llm_service, get_settings
from app.models.chat import Message, QueryResponse, AssembledContext
from app.services.embedding_service import EmbeddingService
from app.services.storage_service import StorageService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/legal-chat", tags=["Legal Chat"])
logger = logging.getLogger(__name__)


class LegalQueryRequest(BaseModel):
    """Incoming query payload for general legal chat."""
    question: str = Field(..., min_length=3, max_length=2000)
    conversation_history: List[Message] = Field(default_factory=list)


@router.post(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query general Indian legal knowledge",
)
async def query_legal(
    request: LegalQueryRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    legal_storage: StorageService = Depends(get_legal_storage),
    llm_service: LLMService = Depends(get_llm_service),
    settings: Settings = Depends(get_settings),
) -> QueryResponse:
    try:
        query_embedding = embedding_service.embed_query(request.question)
        
        legal_results = legal_storage.search(
            query_embedding=query_embedding,
            document_id=None,
            top_k=settings.LEGAL_TOP_K,
            similarity_threshold=settings.LEGAL_SIMILARITY_THRESHOLD,
        )
        
        if not legal_results:
            return QueryResponse(
                answer="I could not find relevant information about this in my legal knowledge base. Please consult a qualified lawyer for advice specific to your situation.",
                citations=[],
                confidence="none",
                related_sections=[],
                has_legal_context=False
            )
            
        assembled_context = AssembledContext(
            document_chunks=[],
            legal_chunks=legal_results,
            has_document_context=False,
            has_legal_context=True
        )
        
        return llm_service.generate_response(
            question=request.question,
            context=assembled_context,
            conversation_history=request.conversation_history
        )
    except Exception as e:
        logger.error("Legal query failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "QUERY_FAILED", "message": "Failed to process legal query"},
        ) from e
