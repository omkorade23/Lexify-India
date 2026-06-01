"""State analysis script"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services.storage_service import StorageService

doc = StorageService(settings.DATABASE_PATH, settings.DOCUMENT_COLLECTION_NAME)
legal = StorageService(settings.DATABASE_PATH, settings.LEGAL_COLLECTION_NAME)
ds = doc.collection_stats()
ls = legal.collection_stats()

print("document_chunks :", ds["total_chunks"], "chunks")
print("legal_knowledge :", ls["total_chunks"], "chunks")
print("Embedding model :", settings.EMBEDDING_MODEL)
print("LLM model       :", settings.LLM_MODEL)
gemini_ok = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here")
print("Gemini key set  :", gemini_ok)
