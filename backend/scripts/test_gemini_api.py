"""Step 6: Test Gemini API embedding"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.embedding_service import EmbeddingService

print(f"Embedding model: {settings.EMBEDDING_MODEL}")
print("Testing Gemini embedding API...")

emb = EmbeddingService(api_key=settings.GEMINI_API_KEY, model=settings.EMBEDDING_MODEL)
vec = emb.embed_query("test query for validation")
print(f"Embedding dimension: {len(vec)}")
assert len(vec) in (768, 3072), f"Unexpected dim {len(vec)}"
print(f"Gemini API: WORKING -- {len(vec)}-dim vectors")
