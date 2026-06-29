"""
Step 2: Diagnostic retrieval test for all 5 queries.
Run from backend/ with: venv\Scripts\python.exe scripts\diag_retrieval.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.storage_service import StorageService
from app.services.embedding_service import EmbeddingService

emb = EmbeddingService(api_key=settings.GEMINI_API_KEY, model=settings.EMBEDDING_MODEL)
legal = StorageService(settings.DATABASE_PATH, settings.LEGAL_COLLECTION_NAME)

stats = legal.collection_stats()
print(f"legal_knowledge collection: {stats['total_chunks']} chunks")
print(f"Active LEGAL_SIMILARITY_THRESHOLD: {settings.LEGAL_SIMILARITY_THRESHOLD}")
print(f"Active DOCUMENT_SIMILARITY_THRESHOLD: {settings.DOCUMENT_SIMILARITY_THRESHOLD}")
print()

queries = [
    "Can I apply for permanent driving licence now?",
    "What is the minimum age to get a driving licence in India?",
    "How many days after learner licence can I get permanent licence?",
    "What is anticipatory bail?",
    "What are tenant rights in India?",
]

DRIVING_IDS = {"motor_vehicles_001", "motor_vehicles_002"}
print("=" * 70)
print("RAW SCORES (threshold=0.0 — all results shown)")
print("=" * 70)

all_scores = {}
for q in queries:
    vec = emb.embed_query(q)
    results = legal.search(query_embedding=vec, document_id=None, top_k=5, similarity_threshold=0.0)
    print(f"\nQuery: {q}")
    scores_for_q = []
    for r in results:
        cid = r["chunk_id"]
        score = r["similarity_score"]
        cat = r["metadata"].get("category", "?")
        marker = " <-- DRIVING" if cid in DRIVING_IDS else ""
        print(f"  score={score:.4f}  id={cid:<30} category={cat}{marker}")
        scores_for_q.append(score)
    all_scores[q] = scores_for_q

print()
print("=" * 70)
print("THRESHOLD EVALUATION")
print("=" * 70)
driving_queries = queries[:3]
above_060 = []
below_060 = []
for q in driving_queries:
    vec = emb.embed_query(q)
    results = legal.search(query_embedding=vec, document_id=None, top_k=3, similarity_threshold=0.0)
    driving_hits = [r for r in results if r["chunk_id"] in DRIVING_IDS]
    max_score = max((r["similarity_score"] for r in driving_hits), default=0.0)
    status = "PASS (>= 0.60)" if max_score >= 0.60 else "FAIL (< 0.60)"
    print(f"  {status}  max_driving_score={max_score:.4f}  query={q[:50]}")
    if max_score >= 0.60:
        above_060.append(q)
    else:
        below_060.append(q)

print()
if below_060:
    print(f"ACTION REQUIRED: {len(below_060)} driving queries score below 0.60")
    print("Recommendation: Lower LEGAL_SIMILARITY_THRESHOLD to 0.55")
else:
    print("All driving queries pass threshold >= 0.60. No config change needed.")
