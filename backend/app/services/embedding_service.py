"""
Embedding generation service using Google Gemini SDK (google-genai).

Generates 768-dimensional embeddings for:
- Document chunks (task_type: RETRIEVAL_DOCUMENT)
- User queries (task_type: RETRIEVAL_QUERY)

Handles batching and rate limiting for reliable API usage.
"""

from __future__ import annotations

import logging
import time
from typing import List

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSION = 3072  # gemini-embedding-001 actual output dimension


class EmbeddingService:
    """
    Gemini embedding service for semantic vector generation.
    Produces 768-dim vectors used for ChromaDB similarity search.
    """

    def __init__(self, api_key: str, model: str = "gemini-embedding-001") -> None:
        self.client = genai.Client(api_key=api_key)
        # Normalise model name — new SDK uses "text-embedding-004" or "embedding-001"
        self.model = model.replace("models/", "")
        self.batch_size = 10
        self.batch_delay_ms = 300

    def embed_query(self, query: str) -> List[float]:
        """Generate 768-dim embedding for a user query."""
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=query,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error("Query embedding failed: %s", e)
            raise RuntimeError(f"Failed to generate query embedding: {e}") from e

    def embed_text(self, text: str) -> List[float]:
        """Generate 768-dim embedding for a document chunk."""
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error("Text embedding failed: %s", e)
            raise RuntimeError(f"Failed to generate text embedding: {e}") from e

    def embed_batch(
        self,
        texts: List[str],
        task_type: str = "retrieval_document",
    ) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        Processes 10 at a time with rate-limit delay between batches.
        """
        if not texts:
            return []

        all_embeddings: List[List[float]] = []
        total = len(texts)
        sdk_task = task_type.upper()  # RETRIEVAL_DOCUMENT / RETRIEVAL_QUERY

        logger.info("Generating embeddings for %d texts in batches of %d", total, self.batch_size)

        for i in range(0, total, self.batch_size):
            batch = texts[i : i + self.batch_size]
            batch_embeddings = []

            for text in batch:
                try:
                    response = self.client.models.embed_content(
                        model=self.model,
                        contents=text,
                        config=types.EmbedContentConfig(task_type=sdk_task),
                    )
                    batch_embeddings.append(response.embeddings[0].values)
                except Exception as e:
                    logger.error("Embedding failed for chunk %d: %s", i, e)
                    batch_embeddings.append([0.0] * EMBEDDING_DIMENSION)

            all_embeddings.extend(batch_embeddings)

            if i + self.batch_size < total:
                time.sleep(self.batch_delay_ms / 1000)

            logger.debug("Embedded batch %d, total: %d/%d", i // self.batch_size + 1, len(all_embeddings), total)

        logger.info("Embedding complete: %d vectors generated", len(all_embeddings))
        return all_embeddings
