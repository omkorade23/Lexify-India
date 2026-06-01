"""
Chat / RAG query API endpoints.

Router prefix: /api/chat
Tags:          Chat

Phase 2 — fully functional dual-source RAG pipeline.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import RAGServiceDep
from app.core.exceptions import DocumentNotFoundException, LexifyException
from app.models.chat import QueryRequest, QueryResponse

router = APIRouter(prefix="/api/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query a document with a natural language question",
    description=(
        "Submit a natural language question about a previously uploaded "
        "document. Uses dual-source RAG: retrieves context from your document "
        "and from a curated Indian legal knowledge base. Returns an LLM-generated "
        "answer with citations from both sources."
    ),
)
async def query_document(
    request: QueryRequest,
    rag_service: RAGServiceDep,
) -> QueryResponse:
    """
    Ask a question about an uploaded legal document.

    **Phase 2 behaviour (active):**
    1. Validates document_id exists in registry → 404 if not found.
    2. Embeds the question using Gemini embedding-001 (768-dim).
    3. Searches document_chunks collection (filtered by document_id) → top 5.
    4. Searches legal_knowledge collection (no filter) → top 3.
    5. Assembles dual-source context with both result sets.
    6. Generates response using Gemini 1.5-flash with citation grounding.
    7. Returns QueryResponse with answer, citations, confidence, and has_legal_context.

    **Raises:**
    - 404: document_id not found in registry.
    - 500: embedding or LLM generation failure.
    """
    logger.info("Query received for document: %s", request.document_id)

    # Validate document exists in registry
    if not rag_service.document_exists(request.document_id):
        raise DocumentNotFoundException(request.document_id)

    try:
        response = rag_service.query(request)

        logger.info(
            "Query complete: confidence=%s, has_legal_context=%s, citations=%d",
            response.confidence,
            response.has_legal_context,
            len(response.citations),
        )

        return response

    except ValueError as e:
        # Raised by RAGService if document_id is not in registry
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    except LexifyException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": e.code, "message": e.message},
        ) from e

    except Exception as e:
        logger.error("Query pipeline error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "QUERY_FAILED", "message": "Failed to process query"},
        ) from e
