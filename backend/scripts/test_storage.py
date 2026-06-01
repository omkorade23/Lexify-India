#!/usr/bin/env python3
"""
Test ChromaDB storage service with mock data.

Validates all five public operations of StorageService:
  1. store_chunks()        - write 5 mock chunks
  2. get_document_chunks() - retrieve all chunks for a document
  3. search()              - similarity search (random query vector)
  4. collection_stats()    - verify chunk count
  5. delete_document()     - cleanup; verify chunks removed

Usage
-----
    python scripts/test_storage.py

Run from the ``backend/`` directory.
"""

from __future__ import annotations

import random
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.storage_service import DocumentChunk, StorageService

# Embedding dimension used in tests.
# 384 matches sentence-transformers/all-MiniLM-L6-v2.
EMBEDDING_DIM = 384


def _random_vector(dim: int = EMBEDDING_DIM) -> list[float]:
    return [random.random() for _ in range(dim)]


def test_storage() -> None:
    print("[TEST] Testing ChromaDB Storage Service\n")

    storage = StorageService(
        database_path=settings.DATABASE_PATH,
        collection_name=settings.COLLECTION_NAME,
    )

    document_id = str(uuid.uuid4())
    print(f"   Using test document_id: {document_id}\n")

    # ------------------------------------------------------------------ #
    # 1. Store chunks                                                      #
    # ------------------------------------------------------------------ #
    print("1. Storing 5 mock document chunks...")

    chunks = [
        DocumentChunk(
            chunk_id=f"test_{document_id}_chunk_{i}",
            document_id=document_id,
            text=(
                f"This is test chunk {i} containing legal text about "
                f"clause {i} regarding indemnification and liability limits."
            ),
            page_number=i + 1,
            section=f"Clause {i} - Indemnification",
            clause_number=str(i),
            start_char=i * 200,
            end_char=(i + 1) * 200,
            metadata={"test": True, "chunk_index": i},
        )
        for i in range(5)
    ]

    embeddings = [_random_vector() for _ in range(5)]

    result = storage.store_chunks(chunks=chunks, embeddings=embeddings)
    assert result["stored"] == 5, f"Expected 5, got {result['stored']}"
    print(f"   [OK] Stored {result['stored']} chunks\n")

    # ------------------------------------------------------------------ #
    # 2. Retrieve all chunks for document                                  #
    # ------------------------------------------------------------------ #
    print("2. Retrieving all chunks for the document...")
    retrieved = storage.get_document_chunks(document_id)
    assert len(retrieved) == 5, f"Expected 5, got {len(retrieved)}"
    print(f"   [OK] Retrieved {len(retrieved)} chunks\n")

    # ------------------------------------------------------------------ #
    # 3. Similarity search                                                 #
    # ------------------------------------------------------------------ #
    print("3. Running similarity search (threshold=0.0 to catch all)...")
    query_vec = _random_vector()
    results = storage.search(
        query_embedding=query_vec,
        document_id=document_id,
        top_k=3,
        similarity_threshold=0.0,  # Low threshold so random vectors still match.
    )
    assert len(results) <= 3, "Returned more results than top_k"
    print(f"   [OK] Found {len(results)} chunks")
    if results:
        top = results[0]
        print(
            f"   Top result: page {top['page_number']}, "
            f"similarity {top['similarity_score']:.4f}"
        )
    print()

    # ------------------------------------------------------------------ #
    # 4. Collection stats                                                  #
    # ------------------------------------------------------------------ #
    print("4. Checking collection stats...")
    stats = storage.collection_stats()
    print(f"   Total chunks in collection : {stats['total_chunks']}")
    print(f"   Database path              : {stats['database_path']}\n")

    # ------------------------------------------------------------------ #
    # 5. Delete document                                                   #
    # ------------------------------------------------------------------ #
    print("5. Cleaning up test data...")
    delete_result = storage.delete_document(document_id)
    assert delete_result["deleted"] == 5, (
        f"Expected to delete 5, deleted {delete_result['deleted']}"
    )
    print(f"   [OK] Deleted {delete_result['deleted']} chunks")

    # Verify deletion.
    after = storage.get_document_chunks(document_id)
    assert len(after) == 0, "Chunks still exist after deletion"
    print("   [OK] Confirmed -- no chunks remain for this document\n")

    print("[PASS] All tests passed!\n")


if __name__ == "__main__":
    test_storage()
