"""Diagnose retrieval pipeline - check embeddings and similarity scores"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from app.core.config import settings
from app.services.storage_service import StorageService
from app.services.embedding_service import EmbeddingService

# Load registry to get the last uploaded doc_id
registry_path = Path("data/document_registry.json")
if registry_path.exists():
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    print(f"Registry entries: {len(registry)}")
    for doc_id, info in registry.items():
        print(f"  {doc_id}: chunks_stored={info.get('chunks_stored')}, filename={info.get('filename')}")
    last_doc_id = list(registry.keys())[-1]
else:
    print("No registry - need to upload first")
    sys.exit(1)

print(f"\nDiagnosing retrieval for doc_id: {last_doc_id}")

# Generate a real query embedding
emb_svc = EmbeddingService(api_key=settings.GEMINI_API_KEY, model=settings.EMBEDDING_MODEL)
query = "What is the monthly rent?"
query_vec = emb_svc.embed_query(query)
print(f"Query embedding dim: {len(query_vec)}")
print(f"Query vec sample (first 5): {query_vec[:5]}")

# Check document chunks stored
doc_storage = StorageService(settings.DATABASE_PATH, settings.DOCUMENT_COLLECTION_NAME)
stats = doc_storage.collection_stats()
print(f"\ndocument_chunks total: {stats['total_chunks']}")

# Try to retrieve WITHOUT threshold (raw ChromaDB)
import chromadb
client = chromadb.PersistentClient(path=settings.DATABASE_PATH)
col = client.get_collection("document_chunks")
raw_results = col.query(
    query_embeddings=[query_vec],
    n_results=min(3, stats["total_chunks"]),
    include=["documents", "metadatas", "distances"],
)
print("\nRaw ChromaDB results:")
if raw_results["documents"] and raw_results["documents"][0]:
    for i, (doc, meta, dist) in enumerate(zip(
        raw_results["documents"][0],
        raw_results["metadatas"][0],
        raw_results["distances"][0],
    )):
        sim = 1 - dist  # cosine: distance = 1 - similarity
        print(f"  [{i}] sim={sim:.4f}, dist={dist:.4f}, doc_id={meta.get('document_id','?')}")
        print(f"       text={doc[:80]}")
else:
    print("  No results from raw query")

# Check what threshold is set
print(f"\nDocument threshold: {settings.DOCUMENT_SIMILARITY_THRESHOLD}")
print(f"Legal threshold:    {settings.LEGAL_SIMILARITY_THRESHOLD}")

# Also check legal KB retrieval
legal_storage = StorageService(settings.DATABASE_PATH, settings.LEGAL_COLLECTION_NAME)
legal_stats = legal_storage.collection_stats()
print(f"\nlegal_knowledge total: {legal_stats['total_chunks']}")
legal_col = client.get_collection("legal_knowledge")
legal_raw = legal_col.query(
    query_embeddings=[query_vec],
    n_results=3,
    include=["documents", "metadatas", "distances"],
)
print("Raw legal results:")
if legal_raw["documents"] and legal_raw["documents"][0]:
    for i, (doc, meta, dist) in enumerate(zip(
        legal_raw["documents"][0],
        legal_raw["metadatas"][0],
        legal_raw["distances"][0],
    )):
        sim = 1 - dist
        print(f"  [{i}] sim={sim:.4f}, dist={dist:.4f}, title={meta.get('title','?')}")
else:
    print("  No legal results")
