"""Step 2: Full import validation"""
from app.core.config import settings
from app.core.exceptions import LexifyException, DocumentNotFoundException
from app.core.prompts import DUAL_SOURCE_SYSTEM_PROMPT, NOT_FOUND_TEMPLATE
from app.models.chat import Citation, QueryRequest, QueryResponse, AssembledContext, Message
from app.models.document import Document, DocumentUploadResponse, DocumentMetadata
from app.services.storage_service import StorageService, DocumentChunk
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService

c = Citation(source_type='document', text='test', similarity_score=0.9, chunk_id='c1', page_number=1)
assert c.source_type == 'document', 'source_type missing'
c2 = Citation(source_type='legal_reference', text='law', similarity_score=0.8, chunk_id='c2', act_name='MTA 2021', act_section='S11')
assert c2.act_name == 'MTA 2021', 'act_name missing'
qr = QueryResponse(answer='test', citations=[], confidence='none', has_legal_context=True)
assert qr.has_legal_context is True, 'has_legal_context missing'

print('ALL IMPORTS AND MODEL VALIDATIONS: PASSED')
print(f'LLM={settings.LLM_MODEL}, embedding={settings.EMBEDDING_MODEL}')
print(f'Collections: doc={settings.DOCUMENT_COLLECTION_NAME}, legal={settings.LEGAL_COLLECTION_NAME}')
gemini_ok = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != 'your_gemini_api_key_here')
print(f'Gemini key set: {gemini_ok}')
if not gemini_ok:
    print('WARNING: Add your GEMINI_API_KEY to backend/.env before seeding')
