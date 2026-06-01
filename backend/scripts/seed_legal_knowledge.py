#!/usr/bin/env python3
"""
Seed legal knowledge base into ChromaDB legal_knowledge collection.

Reads data/legal_knowledge_base.json and stores all entries
as Gemini embeddings in the legal_knowledge ChromaDB collection.

Run ONCE after initial setup. Safe to re-run (checks for existing data).

Usage:
    python scripts/seed_legal_knowledge.py
    python scripts/seed_legal_knowledge.py --force  # Re-seed even if data exists

Run from the ``backend/`` directory so relative paths resolve correctly.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.storage_service import StorageService, DocumentChunk
from app.services.embedding_service import EmbeddingService


def seed_legal_knowledge(force: bool = False) -> None:
    """Seed ChromaDB with legal knowledge base."""

    print("🌱 Legal Knowledge Base Seeder\n")

    # Load legal knowledge base
    kb_path = Path(settings.LEGAL_KNOWLEDGE_PATH)
    if not kb_path.exists():
        print(f"❌ Legal knowledge base not found at: {kb_path}")
        print("   Expected: data/legal_knowledge_base.json")
        sys.exit(1)

    with open(kb_path, "r", encoding="utf-8") as f:
        knowledge_entries = json.load(f)

    print(f"📚 Loaded {len(knowledge_entries)} knowledge entries\n")

    # Initialize legal storage collection
    legal_storage = StorageService(
        database_path=settings.DATABASE_PATH,
        collection_name=settings.LEGAL_COLLECTION_NAME,
    )

    # Check existing data
    stats = legal_storage.collection_stats()
    if stats["total_chunks"] > 0 and not force:
        print(f"⚠️  Collection already contains {stats['total_chunks']} chunks")
        print("   Use --force to re-seed")
        return

    if force and stats["total_chunks"] > 0:
        print(f"🔄 Force re-seeding: clearing {stats['total_chunks']} existing chunks...")
        legal_storage.reset_collection()

    # Initialize embedding service
    if not settings.GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not set in .env file")
        print("   Add GEMINI_API_KEY=your_key_here to backend/.env")
        sys.exit(1)

    embedding_service = EmbeddingService(
        api_key=settings.GEMINI_API_KEY,
        model=settings.EMBEDDING_MODEL,
    )

    # Process in batches
    print(f"⚙️  Generating embeddings for {len(knowledge_entries)} entries...")
    print("   This will take approximately 2-3 minutes\n")

    batch_size = 10
    total_stored = 0

    for i in range(0, len(knowledge_entries), batch_size):
        batch = knowledge_entries[i : i + batch_size]

        # Create DocumentChunk objects for legal entries
        chunks = []
        for entry in batch:
            # Handle null risk_relevance — ChromaDB requires str values in metadata
            risk_rel = entry.get("risk_relevance") or ""

            chunk = DocumentChunk(
                chunk_id=entry["id"],
                document_id="legal_knowledge",  # Sentinel value (no real doc)
                text=entry["text"],
                page_number=0,
                section=entry.get("act_section", ""),
                clause_number=None,
                start_char=0,
                end_char=len(entry["text"]),
                metadata={
                    "source_type": "legal_reference",
                    "category": entry.get("category", ""),
                    "title": entry.get("title", ""),
                    "act_name": entry.get("act_name", ""),
                    "act_section": entry.get("act_section", ""),
                    "jurisdiction": entry.get("jurisdiction", "India"),
                    "document_type_relevance": entry.get("document_type_relevance", ""),
                    "risk_relevance": risk_rel,
                },
            )
            chunks.append(chunk)

        # Generate embeddings for batch
        texts = [chunk.text for chunk in chunks]
        embeddings = embedding_service.embed_batch(texts, task_type="retrieval_document")

        # Store batch in legal_knowledge collection
        result = legal_storage.store_chunks(chunks=chunks, embeddings=embeddings)
        total_stored += result["stored"]

        print(
            f"   ✅ Stored batch {i // batch_size + 1}: "
            f"{result['stored']} entries (total: {total_stored}/{len(knowledge_entries)})"
        )

        # Rate limit delay between batches
        if i + batch_size < len(knowledge_entries):
            time.sleep(0.5)

    # Verify final count
    final_stats = legal_storage.collection_stats()

    print(f"\n✅ Legal knowledge base seeded successfully!")
    print(f"   Total chunks: {final_stats['total_chunks']}")
    print(f"   Collection: {final_stats['collection_name']}")
    print(f"   Database: {final_stats['database_path']}")
    print("\n🚀 Legal knowledge is ready for hybrid RAG queries")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed legal knowledge base into ChromaDB")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-seed even if collection already contains data",
    )
    args = parser.parse_args()

    seed_legal_knowledge(force=args.force)
