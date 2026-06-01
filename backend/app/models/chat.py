"""
Pydantic models for the chat / RAG query pipeline.

These models define the API contract for conversational document Q&A and
must remain in sync with the Lexify-India PRD specifications.

Phase 2 update: Citation now carries source_type for dual-source RAG,
QueryResponse now carries has_legal_context flag.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Message(BaseModel):
    """A single turn in a conversation (user or assistant)."""

    role: str = Field(
        ...,
        description="Speaker role: 'user' | 'assistant'.",
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Text content of the message turn.",
    )

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        allowed = {"user", "assistant"}
        if value not in allowed:
            raise ValueError(f"role must be one of {allowed}.")
        return value


class Citation(BaseModel):
    """
    A source chunk used to ground an answer.

    source_type determines which fields are populated:
    - "document": page_number, section are populated
    - "legal_reference": act_name, act_section, category are populated
    """

    # Dual-source type — NEW in Phase 2
    source_type: str = Field(
        default="document",
        description="'document' | 'legal_reference'",
    )

    text: str = Field(
        ...,
        description="Verbatim extracted text from the source chunk.",
    )

    # Document citation fields (source_type == "document")
    page_number: Optional[int] = Field(
        default=None,
        description="1-indexed page number where this chunk originates.",
    )
    section: Optional[str] = Field(
        default=None,
        description="Section heading or clause identifier, if detectable.",
    )

    # Legal reference fields (source_type == "legal_reference")
    act_name: Optional[str] = Field(
        default=None,
        description="Name of the Indian Act (e.g. 'Model Tenancy Act 2021').",
    )
    act_section: Optional[str] = Field(
        default=None,
        description="Section of the act (e.g. 'Section 11').",
    )
    category: Optional[str] = Field(
        default=None,
        description="Knowledge category (e.g. 'tenancy_law', 'employment_law').",
    )

    # Common fields
    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity between the query embedding and this chunk.",
    )
    chunk_id: str = Field(
        ...,
        description="Unique identifier for this chunk in the vector store.",
    )


class QueryRequest(BaseModel):
    """
    Incoming query payload for the POST /api/chat endpoint.

    `conversation_history` allows multi-turn dialogue.
    """

    document_id: str = Field(
        ...,
        description="UUID of the document to query against.",
    )
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Natural language question about the document.",
    )
    conversation_history: List[Message] = Field(
        default_factory=list,
        description=(
            "Prior conversation turns for multi-turn context. "
            "Ordered oldest → newest. Empty for first-turn queries."
        ),
    )


class QueryResponse(BaseModel):
    """
    Response returned by the POST /api/chat endpoint.

    `confidence` is a qualitative band derived from the best citation's
    similarity score:
        high   → score ≥ 0.85
        medium → score ≥ 0.75
        low    → any lower match
        none   → no retrievable chunks / fallback answer

    `has_legal_context` indicates whether legal knowledge was used in
    addition to the document, enabling the frontend to show a legal badge.
    """

    answer: str = Field(
        ...,
        description="LLM-generated answer grounded in the document.",
    )
    citations: List[Citation] = Field(
        default_factory=list,
        description="Source chunks used to generate the answer.",
    )
    confidence: str = Field(
        ...,
        description="Confidence band: 'high' | 'medium' | 'low' | 'none'.",
    )
    related_sections: List[str] = Field(
        default_factory=list,
        description=(
            "Section headings or clause titles semantically related to the "
            "question, extracted by the RAG pipeline."
        ),
    )
    has_legal_context: bool = Field(
        default=False,
        description="True when legal knowledge was used alongside document context.",
    )

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, value: str) -> str:
        allowed = {"high", "medium", "low", "none"}
        if value not in allowed:
            raise ValueError(f"confidence must be one of {allowed}.")
        return value


class AssembledContext(BaseModel):
    """Assembled retrieval context for LLM prompt construction."""
    document_chunks: List[dict] = Field(default_factory=list)
    legal_chunks: List[dict] = Field(default_factory=list)
    has_document_context: bool = False
    has_legal_context: bool = False
