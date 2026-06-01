# Project State: After Phase 2 RAG Pipeline (Complete)

**DATE:** 2026-05-27 (Validation completed)  
**SESSION:** Recovery session — all 18/18 E2E checks passed  

---

## Complete Project Structure

```
Lexify-India/
├── backend/                                   Phase 2 COMPLETE ✅
│   ├── venv/                                  Python 3.14 virtual environment
│   ├── app/
│   │   ├── main.py                            ✅ FastAPI app + CORS + structured logging
│   │   ├── api/
│   │   │   ├── documents.py                   ✅ Full OCR + RAG ingestion pipeline
│   │   │   └── chat.py                        ✅ Full dual-source RAG query
│   │   ├── models/
│   │   │   ├── document.py                    ✅ DocumentUploadResponse
│   │   │   └── chat.py                        ✅ Citation + QueryResponse (Phase 2 extended)
│   │   ├── services/
│   │   │   ├── storage_service.py             ✅ ChromaDB (document_id optional in search)
│   │   │   ├── ocr_service.py                 ✅ PaddleOCR + pdfplumber
│   │   │   ├── document_processor.py          ✅ Upload orchestration + type detection
│   │   │   ├── chunking_service.py            ✅ NEW Phase 2 — page-aware recursive splitting
│   │   │   ├── embedding_service.py           ✅ NEW Phase 2 — gemini-embedding-001 (3072-dim)
│   │   │   ├── retrieval_service.py           ✅ NEW Phase 2 — dual-collection search
│   │   │   ├── llm_service.py                 ✅ NEW Phase 2 — gemini-2.5-flash generation
│   │   │   └── rag_service.py                 ✅ NEW Phase 2 — full orchestrator
│   │   ├── core/
│   │   │   ├── config.py                      ✅ Phase 2 settings + property accessors
│   │   │   ├── dependencies.py                ✅ 8-service DI provider wiring
│   │   │   ├── prompts.py                     ✅ NEW Phase 2 — 3 prompt templates
│   │   │   └── exceptions.py                  ✅ Custom exception hierarchy
│   │   └── utils/
│   │       └── image_preprocessing.py         ✅ OpenCV helpers for OCR
│   ├── data/
│   │   ├── uploads/                           ✅ Uploaded documents stored here
│   │   ├── chroma_db/                         ✅ Both collections initialized
│   │   │   ├── document_chunks               ✅ Per-document 3072-dim embeddings
│   │   │   └── legal_knowledge               ✅ 37 pre-seeded Indian law entries
│   │   ├── legal_knowledge_base.json          ✅ Curated 37-entry legal knowledge
│   │   └── document_registry.json             ✅ Auto-managed per upload
│   ├── scripts/
│   │   ├── init_chroma.py                     ✅ Dual-collection manager (--reset flag)
│   │   ├── generate_knowledge_base.py         ✅ One-time KB generator
│   │   ├── seed_legal_knowledge.py            ✅ ChromaDB seeder (run once)
│   │   ├── test_rag.py                        ✅ 18-check E2E validation suite
│   │   ├── check_state.py                     ✅ Quick state diagnostic
│   │   ├── debug_chat.py                      ✅ Direct pipeline debugger
│   │   └── test_storage.py / test_ocr.py      ✅ Unit-level tests
│   ├── requirements.txt                        ✅ All deps including google-genai>=2.0.0
│   ├── .env.example                            ✅ Template with all Phase 2 vars
│   ├── .env                                    ✅ Active env (GEMINI_API_KEY set)
│   ├── .gitignore                              ✅ Excludes .env, data/, venv/, __pycache__
│   └── README.md                               ✅ Updated
├── frontend/                                  ⏳ NOT STARTED — Ready to begin
├── phase2_rag_completion.md                   ✅ Phase 2 validation report (18/18 PASS)
├── project_state_phase2_rag.md                ✅ This file
└── Lexify-India_PRD.md                        📋 Source of truth
```

---

## System State

### Backend Services
- **Server start:** `cd backend && venv\Scripts\python.exe -m uvicorn app.main:app --reload`
- **Health:** `GET http://localhost:8000/health` → `{"status": "healthy"}`
- **API docs:** `GET http://localhost:8000/docs`

### Active API Endpoints

| Endpoint | Status | Notes |
|----------|--------|-------|
| `GET /health` | ✅ Live | `{"status": "healthy"}` |
| `GET /docs` | ✅ Live | Full Swagger UI |
| `POST /api/documents/upload` | ✅ Full | OCR → Chunk → Embed → Store |
| `GET /api/documents/{id}` | ⚠️ Stub | Returns mock data (Phase 3 work) |
| `POST /api/chat` | ✅ Full | Dual-source RAG with citations |

### ChromaDB Collections

| Collection | Status | Chunks | Embedding | Distance |
|------------|--------|--------|-----------|----------|
| `document_chunks` | ✅ Active | Grows per upload | gemini-embedding-001 (3072-dim) | L2 |
| `legal_knowledge` | ✅ Seeded | 37 entries | gemini-embedding-001 (3072-dim) | L2 |

---

## Active Configuration

```env
# AI Models (google-genai 2.x SDK)
EMBEDDING_MODEL=gemini-embedding-001        # 3072-dimensional vectors
LLM_MODEL=gemini-2.5-flash                  # generateContent API

# Similarity thresholds — calibrated for L2 1/(1+d) formula
DOCUMENT_SIMILARITY_THRESHOLD=0.40
LEGAL_SIMILARITY_THRESHOLD=0.35

# Collections
DOCUMENT_COLLECTION_NAME=document_chunks
LEGAL_COLLECTION_NAME=legal_knowledge
DATABASE_PATH=data/chroma_db

# Chunking
CHUNK_SIZE=800
CHUNK_OVERLAP=100
```

---

## Runtime Issues Resolved (Recovery Session)

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| `ModuleNotFoundError: pydantic_settings` | Venv not activated in terminal | Use `venv\Scripts\python.exe` explicitly |
| `UnicodeEncodeError` on emoji | Windows cp1252 terminal | Set `PYTHONUTF8=1` |
| `404: models/embedding-001` | Deprecated name in google-genai v2 | → `gemini-embedding-001` |
| Embedding dim 768 vs 3072 | `gemini-embedding-001` outputs 3072 | Updated `EMBEDDING_DIMENSION = 3072` |
| Zero retrieval (0 citations) | Thresholds too high for L2 distance | Lowered to 0.40 / 0.35 |
| `404: models/gemini-1.5-flash` | Old model name for v1beta API | → `gemini-2.5-flash` |
| `429 RESOURCE_EXHAUSTED` | Daily quota exhausted on flash/flash-lite | → `gemini-2.5-flash` |

---

## Environment Setup (Critical for New Sessions)

```powershell
# ALWAYS use venv Python — global Python lacks deps
cd "C:\Users\Om Korade\Lexify-India\backend"
$env:PYTHONUTF8 = "1"

# Start server
venv\Scripts\python.exe -m uvicorn app.main:app --reload

# Re-seed legal KB if chroma_db was wiped
venv\Scripts\python.exe scripts\seed_legal_knowledge.py

# Run E2E validation (server must be running)
venv\Scripts\python.exe scripts\test_rag.py
```

---

## Agent Dependency Status

| Phase | Agent | Status | Notes |
|-------|-------|--------|-------|
| Phase 1 | Backend Architecture | ✅ DONE | |
| Phase 2 | Vector DB | ✅ DONE | |
| Phase 2 | OCR & Document Processing | ✅ DONE | |
| Phase 2 | RAG Pipeline | ✅ DONE | This phase |
| Phase 1 | Frontend Foundation | ⏳ READY | Can start now |
| Phase 2 | UI Components | ⏳ Blocked | Needs Frontend Foundation |
| Phase 3 | Integration & Testing | ⏳ Blocked | Needs Frontend |
| Phase 4 | Deployment | ⏳ Blocked | Needs Integration |

---

## Critical Path

```
BACKEND COMPLETE → Frontend Foundation → UI Components → Integration → Deployment
```

**Next priority:** Frontend Foundation Agent (Next.js, API client, routing)

---

## Frontend Integration Contract

### API Base URL
```
http://localhost:8000   (development)
```

### Endpoint 1: Upload Document
```http
POST /api/documents/upload
Content-Type: multipart/form-data
Field: file (PDF, JPG, PNG — max 10MB)

Response 201:
{
  "document_id": "uuid",
  "filename": "contract.pdf",
  "num_pages": 3,
  "extraction_status": "completed",
  "metadata": {
    "document_type": "rental_agreement",
    "file_size": 123456
  }
}
```

### Endpoint 2: Chat Query
```http
POST /api/chat
Content-Type: application/json

{
  "document_id": "uuid",
  "question": "What is the lock-in period?",
  "conversation_history": []
}

Response 200:
{
  "answer": "The lock-in period is 36 months [Your Document, Page 1]...",
  "citations": [
    {
      "source_type": "document",
      "text": "lock-in period of 36 months...",
      "page_number": 1,
      "section": "Clause 3",
      "similarity_score": 0.62,
      "chunk_id": "uuid_p1_c0"
    },
    {
      "source_type": "legal_reference",
      "text": "Under Indian tenancy law...",
      "act_name": "Registration Act 1908",
      "act_section": "Section 17",
      "category": "tenancy_law",
      "similarity_score": 0.58,
      "chunk_id": "lock_in_001"
    }
  ],
  "confidence": "low",
  "related_sections": [],
  "has_legal_context": true
}
```

### Citation Rendering Rules
```
source_type == "document"        → Blue badge, show page_number + section
source_type == "legal_reference" → Amber badge, show act_name + act_section
has_legal_context == true        → Show "Legal Reference Used" indicator
```

### Confidence Badge Colors
```
"high"   → Green
"medium" → Yellow
"low"    → Red / Orange
"none"   → Gray ("Information not found in document")
```

---

## Architecture Health
- ✅ **Modular** — 8 isolated services with clear interfaces
- ✅ **Dependency-injected** — FastAPI DI pattern throughout
- ✅ **Grounded** — Dual-source RAG prevents hallucination
- ✅ **Type-safe** — Pydantic models end-to-end
- ✅ **Validated** — 18/18 E2E checks passing
- ✅ **Documented** — Prompts, configs, handoff docs complete
