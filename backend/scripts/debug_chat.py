"""Debug chat endpoint directly"""
import sys, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.storage_service import StorageService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.models.chat import QueryRequest

import json
from pathlib import Path as P

# Get last doc_id from registry
registry = json.loads(P("data/document_registry.json").read_text(encoding="utf-8"))
doc_id = list(registry.keys())[-1]
print(f"Testing with doc_id: {doc_id}")

# Build all services
chunking = ChunkingService(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
embedding = EmbeddingService(api_key=settings.GEMINI_API_KEY, model=settings.EMBEDDING_MODEL)
doc_storage = StorageService(settings.DATABASE_PATH, settings.DOCUMENT_COLLECTION_NAME)
legal_storage = StorageService(settings.DATABASE_PATH, settings.LEGAL_COLLECTION_NAME)
retrieval = RetrievalService(
    document_storage=doc_storage,
    legal_storage=legal_storage,
    document_top_k=settings.DOCUMENT_TOP_K,
    legal_top_k=settings.LEGAL_TOP_K,
    document_threshold=settings.DOCUMENT_SIMILARITY_THRESHOLD,
    legal_threshold=settings.LEGAL_SIMILARITY_THRESHOLD,
)
llm = LLMService(api_key=settings.GEMINI_API_KEY, model=settings.LLM_MODEL, max_tokens=settings.LLM_MAX_TOKENS)
rag = RAGService(
    chunking_service=chunking,
    embedding_service=embedding,
    retrieval_service=retrieval,
    llm_service=llm,
    document_storage=doc_storage,
    registry_path=settings.DOCUMENT_REGISTRY_PATH,
)

print(f"Document exists in registry: {rag.document_exists(doc_id)}")
print(f"Thresholds: doc={settings.DOCUMENT_SIMILARITY_THRESHOLD}, legal={settings.LEGAL_SIMILARITY_THRESHOLD}")

req = QueryRequest(document_id=doc_id, question="What is the monthly rent?")

try:
    result = rag.query(req)
    print(f"Answer: {result.answer[:150]}")
    print(f"Confidence: {result.confidence}")
    print(f"Citations: {len(result.citations)}")
    print(f"Has legal context: {result.has_legal_context}")
    print("SUCCESS")
except Exception:
    print("TRACEBACK:")
    traceback.print_exc()
