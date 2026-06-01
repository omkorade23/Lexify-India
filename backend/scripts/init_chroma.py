#!/usr/bin/env python3
"""
Initialize ChromaDB collections for Lexify-India.

Creates two collections:
- document_chunks: Per-document embeddings (populated during upload)
- legal_knowledge: Pre-seeded legal knowledge (populated once by seed script)

Usage:
    python scripts/init_chroma.py
    python scripts/init_chroma.py --reset  # WARNING: Deletes all data

Run from the ``backend/`` directory so relative paths resolve correctly.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the backend package is importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402
from app.services.storage_service import StorageService  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize or inspect Lexify-India ChromaDB collections.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate both collections — WARNING: deletes all stored embeddings.",
    )
    args = parser.parse_args()

    print("\n[DB] Lexify-India -- ChromaDB Initialization")
    print(f"   Database path     : {settings.DATABASE_PATH}")
    print(f"   Document collection: {settings.DOCUMENT_COLLECTION_NAME}")
    print(f"   Legal collection  : {settings.LEGAL_COLLECTION_NAME}")
    print()

    # Initialize both storage services
    doc_storage = StorageService(
        database_path=settings.DATABASE_PATH,
        collection_name=settings.DOCUMENT_COLLECTION_NAME,
    )
    legal_storage = StorageService(
        database_path=settings.DATABASE_PATH,
        collection_name=settings.LEGAL_COLLECTION_NAME,
    )

    if args.reset:
        print("[!] WARNING: --reset will permanently delete ALL stored embeddings in BOTH collections.")
        try:
            confirm = input("   Type 'yes' to confirm: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[X] Reset cancelled.")
            return

        if confirm.lower() == "yes":
            doc_storage.reset_collection()
            legal_storage.reset_collection()
            print("[OK] Both collections reset successfully.")
        else:
            print("[X] Reset cancelled -- no data was modified.")
            return

    # Show stats for both collections
    doc_stats = doc_storage.collection_stats()
    legal_stats = legal_storage.collection_stats()

    print("[*] Collection Status:")
    print(f"   [{doc_stats['collection_name']}] : {doc_stats['total_chunks']} chunks")
    print(f"   [{legal_stats['collection_name']}] : {legal_stats['total_chunks']} chunks")
    print(f"   Database: {doc_stats['database_path']}")
    print("\n[OK] ChromaDB initialized and ready.\n")


if __name__ == "__main__":
    main()
