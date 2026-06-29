"""
LLM generation service using Google Gemini SDK (google-genai).

Handles:
- Response generation with dual-source context
- Citation building from retrieved chunks
- Confidence scoring based on similarity scores
"""

from __future__ import annotations

import logging
from typing import List, Optional

from google import genai
from google.genai import types

from app.models.chat import Citation, QueryResponse, AssembledContext
from app.core.prompts import (
    DUAL_SOURCE_SYSTEM_PROMPT, DUAL_SOURCE_USER_TEMPLATE,
    DOCUMENT_ONLY_SYSTEM_PROMPT, DOCUMENT_ONLY_USER_TEMPLATE,
    LEGAL_ONLY_SYSTEM_PROMPT, LEGAL_ONLY_USER_TEMPLATE,
    NOT_FOUND_TEMPLATE,
    format_document_context, format_legal_context, format_conversation_history,
)

logger = logging.getLogger(__name__)


class LLMService:
    """Gemini LLM service for grounded response generation."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", max_tokens: int = 1500) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model_name = model
        self.max_tokens = max_tokens

    def generate_response(
        self,
        question: str,
        context: AssembledContext,
        conversation_history: Optional[list] = None,
    ) -> QueryResponse:
        """Generate grounded response from assembled dual-source context."""
        history = conversation_history or []

        if not context.has_document_context and not context.has_legal_context:
            return QueryResponse(
                answer=NOT_FOUND_TEMPLATE.format(question=question),
                citations=[], confidence="none", related_sections=[], has_legal_context=False,
            )

        if context.has_document_context and context.has_legal_context:
            system_prompt = DUAL_SOURCE_SYSTEM_PROMPT
            user_message = DUAL_SOURCE_USER_TEMPLATE.format(
                document_context=format_document_context(context.document_chunks),
                legal_context=format_legal_context(context.legal_chunks),
                conversation_history=format_conversation_history(history),
                question=question,
            )
        elif context.has_document_context and not context.has_legal_context:
            system_prompt = DOCUMENT_ONLY_SYSTEM_PROMPT
            user_message = DOCUMENT_ONLY_USER_TEMPLATE.format(
                document_context=format_document_context(context.document_chunks),
                conversation_history=format_conversation_history(history),
                question=question,
            )
        elif not context.has_document_context and context.has_legal_context:
            system_prompt = LEGAL_ONLY_SYSTEM_PROMPT
            user_message = LEGAL_ONLY_USER_TEMPLATE.format(
                legal_context=format_legal_context(context.legal_chunks),
                conversation_history=format_conversation_history(history),
                question=question,
            )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=self.max_tokens,
                    temperature=0.1,
                    top_p=0.95,
                ),
            )
            answer_text = response.text
        except Exception as e:
            logger.error("LLM generation failed: %s", e)
            raise RuntimeError(f"Failed to generate response: {e}") from e

        citations = self._build_citations(context)
        confidence = self._calculate_confidence(context.document_chunks, context.legal_chunks)
        related_sections = self._extract_related_sections(context.document_chunks)

        return QueryResponse(
            answer=answer_text,
            citations=citations,
            confidence=confidence,
            related_sections=related_sections,
            has_legal_context=context.has_legal_context,
        )

    def _build_citations(self, context: AssembledContext) -> List[Citation]:
        citations = []
        for chunk in context.document_chunks:
            citations.append(Citation(
                source_type="document",
                text=chunk.get("text", "")[:300],
                page_number=chunk.get("page_number"),
                section=chunk.get("section") or None,
                similarity_score=round(chunk.get("similarity_score", 0.0), 3),
                chunk_id=chunk.get("chunk_id", ""),
            ))
        for chunk in context.legal_chunks:
            meta = chunk.get("metadata", {})
            citations.append(Citation(
                source_type="legal_reference",
                text=chunk.get("text", "")[:300],
                act_name=meta.get("act_name") or None,
                act_section=meta.get("act_section") or None,
                category=meta.get("category") or None,
                similarity_score=round(chunk.get("similarity_score", 0.0), 3),
                chunk_id=chunk.get("chunk_id", ""),
            ))
        return citations

    def _calculate_confidence(self, document_chunks: list, legal_chunks: list = None) -> str:
        # Prefer document chunks for confidence; fall back to legal chunks for legal-only queries.
        chunks = document_chunks if document_chunks else (legal_chunks or [])
        if not chunks:
            return "none"
        top = chunks[0].get("similarity_score", 0.0)
        if top >= 0.85: return "high"
        elif top >= 0.70: return "medium"
        else: return "low"

    def _extract_related_sections(self, document_chunks: list) -> List[str]:
        seen: set = set()
        sections = []
        for c in document_chunks:
            s = c.get("section")
            if s and s not in seen:
                sections.append(s); seen.add(s)
        return sections[:5]
