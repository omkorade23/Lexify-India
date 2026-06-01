# Lexify-India Backend

AI-powered legal document understanding platform — FastAPI backend.

## Quick Start

### 1. Prerequisites

- Python 3.11+
- `pip` or `pip3`

### 2. Setup

```bash
# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# (Edit .env if needed — defaults are fine for local development)
```

### 3. Run the Development Server

```bash
# Run from the backend/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify

| URL | Description |
|-----|-------------|
| http://localhost:8000/health | Liveness check — should return `{"status": "healthy"}` |
| http://localhost:8000/docs | Swagger UI — interactive API explorer |
| http://localhost:8000/redoc | ReDoc — alternate API documentation |

---

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI app, middleware, exception handler
│   ├── api/
│   │   ├── documents.py     # POST /api/documents/upload (OCR active ✅), GET /api/documents/{id}
│   │   └── chat.py          # POST /api/chat (stub — RAG Agent)
│   ├── models/
│   │   ├── document.py      # Document, DocumentUploadResponse, DocumentMetadata
│   │   └── chat.py          # QueryRequest, QueryResponse, Citation, Message
│   ├── core/
│   │   ├── config.py        # Pydantic BaseSettings — env-based configuration
│   │   ├── dependencies.py  # FastAPI Depends() providers (OCR + Storage active)
│   │   └── exceptions.py    # Custom exception hierarchy → structured HTTP errors
│   ├── services/
│   │   ├── ocr_service.py       # ✅ OCR extraction (PaddleOCR + pdfplumber)
│   │   ├── document_processor.py # ✅ Upload orchestration
│   │   └── storage_service.py   # ✅ ChromaDB vector storage
│   └── utils/
│       └── image_preprocessing.py # ✅ Advanced OCR preprocessing helpers
├── scripts/
│   ├── init_chroma.py       # ChromaDB first-time setup
│   ├── test_storage.py      # Vector DB test suite
│   └── test_ocr.py          # ✅ OCR service test script
└── data/
    ├── uploads/             # Uploaded documents (UUID-prefixed)
    └── chroma_db/           # ChromaDB persistent store
```

---

## API Reference

### Documents

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| `POST` | `/api/documents/upload` | 201 | Upload a legal document (PDF/JPG/PNG) |
| `GET` | `/api/documents/{document_id}` | 200 | Retrieve document metadata and OCR status |

**Upload a document**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@my_contract.pdf"
```

**Get document status**
```bash
curl http://localhost:8000/api/documents/<document_id>
```

### Chat

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| `POST` | `/api/chat` | 200 | Ask a natural language question about a document |

**Query a document**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "<document_id>",
    "question": "What are the termination clauses?",
    "conversation_history": []
  }'
```

---

## Phase Status

### ✅ Phase 1 — Backend Foundation

- [x] FastAPI application scaffold with JSON logging
- [x] CORS middleware (permissive for local development)
- [x] Pydantic models aligned to PRD specifications
- [x] Stub API endpoints with structured mock responses
- [x] Custom exception hierarchy → consistent JSON error shape
- [x] Dependency injection setup ready for service plug-in
- [x] Environment-based configuration via `.env`

### ✅ Phase 2 — OCR & Document Processing (Complete)

- [x] **OCR Agent** → `app/services/ocr_service.py` ✅
  PaddleOCR extraction with direct PDF + OCR fallback, image preprocessing
- [x] **Document Processor** → `app/services/document_processor.py` ✅
  Upload orchestration, file persistence, document-type detection
- [x] `POST /api/documents/upload` → **FUNCTIONAL** (real OCR results) ✅
- [x] **Vector DB Agent** → ChromaDB collection setup ✅
  Implements `app/services/storage_service.py`
- [ ] **RAG Agent** → `app/services/rag_service.py`
  Implements Gemini + LangChain pipeline, plugs into `POST /api/chat`

---

## OCR & Document Processing

PaddleOCR + pdfplumber are used for text extraction from legal documents.

### Processing Pipeline

```
Upload → Validate → Save → Extract (direct PDF or OCR fallback) → Type detection → Response
```

### Supported Formats

| Format | Method |
|--------|--------|
| PDF (text-based) | Direct pdfplumber extraction (~100ms/page, 100% accuracy) |
| PDF (scanned/image) | PaddleOCR fallback (~2-4s/page, ~85-95% accuracy) |
| JPG / PNG | PaddleOCR with preprocessing (~1-2s/image) |

### Upload a Document

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@rental_agreement.pdf"
```

Response:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "rental_agreement.pdf",
  "num_pages": 12,
  "extraction_status": "completed",
  "preview_text": "RENTAL AGREEMENT\nThis agreement is made between...",
  "metadata": {
    "file_size": 2048576,
    "language": "en",
    "document_type": "rental_agreement"
  }
}
```

### OCR Test Script

```bash
# Generate a sample PDF and test
python scripts/test_ocr.py --generate-sample

# Test with a specific file
python scripts/test_ocr.py --file path/to/document.pdf

# Test against files already in data/uploads/
python scripts/test_ocr.py
```

### Document Types Detected

| Type | Trigger Keywords |
|------|------------------|
| `rental_agreement` | rental agreement, tenancy, lease deed, landlord, tenant |
| `employment_contract` | employment agreement, offer letter, salary, designation |
| `nda` | non-disclosure, confidentiality agreement, trade secret |
| `property_document` | sale deed, conveyance deed, stamp duty |
| `court_notice` | court, summons, petition, plaintiff, defendant |
| `legal_document` | fallback for all other documents |


ChromaDB is used for persistent vector storage of document chunk embeddings.
All data is stored locally at `data/chroma_db/` (SQLite-backed).

### Storage Service Usage

```python
from app.services.storage_service import StorageService, DocumentChunk

# Initialize (use Depends(get_storage_service) in routes instead)
storage = StorageService(database_path="data/chroma_db")

# Store chunks with embeddings (RAG Agent calls this after embedding)
storage.store_chunks(chunks=chunks, embeddings=embeddings)

# Similarity search scoped to one document
results = storage.search(
    query_embedding=query_vector,
    document_id="doc-uuid",
    top_k=5,
    similarity_threshold=0.7,
)

# Retrieve all chunks for a document
chunks = storage.get_document_chunks(document_id="doc-uuid")

# Delete all chunks for a document
storage.delete_document(document_id="doc-uuid")

# Collection statistics
stats = storage.collection_stats()
```

### Dependency Injection (Route Handlers)

```python
from app.core.dependencies import StorageServiceDep

@router.post("/api/chat")
async def query_document(
    request: QueryRequest,
    storage: StorageServiceDep,
) -> QueryResponse:
    results = storage.search(
        query_embedding=query_vector,
        document_id=request.document_id,
    )
```

### CLI Scripts

```bash
# First-time setup / health check
python scripts/init_chroma.py

# Reset collection — deletes ALL embeddings (prompts for confirmation)
python scripts/init_chroma.py --reset

# Run full test suite against live ChromaDB
python scripts/test_storage.py
```

### Result Schema

Each `search()` result dict contains:

| Field | Type | Description |
|-------|------|-------------|
| `chunk_id` | str | Unique chunk identifier |
| `text` | str | Raw chunk text |
| `metadata` | dict | Full metadata (see below) |
| `similarity_score` | float | L2-derived score in (0, 1] |
| `page_number` | int | Convenience alias from metadata |
| `section` | str | Clause/section name |

Metadata fields: `document_id`, `page_number`, `section`, `clause_number`, `start_char`, `end_char`, plus any custom fields passed via `DocumentChunk.metadata`.

---

### Adding a New Service

1. Create `app/services/<name>_service.py`.
2. Add a `get_<name>_service()` dependency in `app/core/dependencies.py`.
3. Inject via `Depends(get_<name>_service)` in the relevant route.
4. Uncomment the corresponding config block in `app/core/config.py`.
5. Uncomment the corresponding env vars in `.env.example`.

### Error Handling

All domain errors must use the custom exceptions in `app/core/exceptions.py`.  
The global handler in `app/main.py` converts them to this JSON shape:

```json
{
  "error": {
    "code": "document_not_found",
    "message": "No document with id 'abc' exists.",
    "details": "document_id=abc"
  }
}
```

### Validation

Input validation is handled by Pydantic models — add constraints directly on
model fields using `Field(...)` arguments. Never write manual `if` guards for
type or format checks.

### Environment Variables

All settings live in `app/core/config.py`. Never read `os.environ` directly in
application code — always use `Depends(get_settings)` or the `settings`
singleton.

---

## Integration Handoff

```
FROM: Backend Architecture Agent
TO:   OCR Agent, RAG Agent, Vector DB Agent, Frontend Foundation Agent
STATUS: COMPLETED ✅

OUTPUT:
  - FastAPI backend running at http://localhost:8000
  - API contracts at http://localhost:8000/docs
  - Pydantic models matching PRD specifications
  - Stub endpoints ready for service integration

INTEGRATION_NOTES:
  OCR Agent    → Implement file saving + PaddleOCR in POST /api/documents/upload
                 See TODO in app/api/documents.py:upload_document()
  RAG Agent    → Implement retrieval + generation in POST /api/chat
                 See TODO in app/api/chat.py:query_document()
  Vector DB    → Can start ChromaDB setup independently in app/services/
  Frontend     → Consume API contracts at /docs, CORS allows localhost:3000/5173

BLOCKERS: None
```
