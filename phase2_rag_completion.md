# Phase 2 RAG Pipeline — Completion & Validation Report

**FROM:** RAG Recovery Agent (Phase 2 Validation Session)  
**TO:** Frontend Foundation Agent, UI Component Agent, Integration Agent  
**STATUS:** COMPLETED ✅  
**DATE:** 2026-05-27  

---

## Validation Results — All 18/18 Checks Passed

| # | Test | Result | Notes |
|---|------|--------|-------|
| 1 | API Health Check | ✅ PASS | `GET /health` → 200 |
| 2 | Legal KB Seeded | ✅ PASS | 37 chunks in `legal_knowledge` |
| 3a | Upload Document | ✅ PASS | `POST /api/documents/upload` → 201 |
| 3b | Document ID Returned | ✅ PASS | UUID assigned |
| 3c | Pages Extracted | ✅ PASS | OCR functional |
| 3d | Doc Type Detected | ✅ PASS | `rental_agreement` |
| 4a | Factual Query → 200 | ✅ PASS | `POST /api/chat` |
| 4b | Answer Text Present | ✅ PASS | "The monthly rent is Rs. 35,000…" |
| 4c | Document Citations | ✅ PASS | 1 document citation |
| 4d | Confidence Not None | ✅ PASS | `low` confidence |
| 5a | Advisory Query → 200 | ✅ PASS | Dual-source RAG triggered |
| 5b | `has_legal_context` Flag | ✅ PASS | `true` |
| 5c | Legal Citations | ✅ PASS | 3 legal references |
| 6a | Not-Found → 200 | ✅ PASS | Graceful handling |
| 6b | Graceful Response | ✅ PASS | No crash, valid answer |
| 7 | Invalid Doc ID → 404 | ✅ PASS | Correct HTTP error |
| 8a | Document Chunks Stored | ✅ PASS | Chunks in `document_chunks` |
| 8b | Legal KB Intact | ✅ PASS | 37 chunks still present |

### Sample Output from Validation

**Factual Query:** "What is the monthly rent?"  
→ `"The monthly rent is Rs. 35,000, payable on the 1st of every month [Your Document, Page 1, Clause 1]."`

**Advisory Query:** "Is the 36-month lock-in period risky?"  
→ `has_legal_context: true`, 3 legal citations including `Registration Act 1908 §17`

---

## Runtime Issues Resolved During Recovery

| Issue | Root Cause | Fix Applied |
|-------|-----------|-------------|
| `ModuleNotFoundError: pydantic_settings` | Global Python missing deps, venv not activated | Use `venv\Scripts\python.exe` explicitly |
| `UnicodeEncodeError` on emoji output | Windows cp1252 terminal encoding | Set `PYTHONUTF8=1` env var |
| `404 NOT_FOUND: models/embedding-001` | Old SDK model name incompatible with google-genai v2 | Updated to `gemini-embedding-001` |
| Embedding dimension mismatch (768 vs 3072) | `gemini-embedding-001` outputs 3072-dim, not 768 | Updated `EMBEDDING_DIMENSION = 3072` |
| Zero retrieval results (0 citations) | Thresholds (0.70/0.65) too high for L2 1/(1+d) formula | Lowered to 0.40 / 0.35 |
| `404 NOT_FOUND: models/gemini-1.5-flash` | Model path format incorrect for v1beta API | Updated to `gemini-2.5-flash` |
| `429 RESOURCE_EXHAUSTED` on gemini-2.0-flash/lite | Daily free quota exhausted on those models | Switched to `gemini-2.5-flash` (confirmed quota) |

---

## Final Configuration (Active)

```env
EMBEDDING_MODEL=gemini-embedding-001        # 3072-dim vectors
LLM_MODEL=gemini-2.5-flash                  # generateContent
DOCUMENT_SIMILARITY_THRESHOLD=0.40          # Calibrated for L2 1/(1+d) formula
LEGAL_SIMILARITY_THRESHOLD=0.35             # Same calibration
DOCUMENT_COLLECTION_NAME=document_chunks
LEGAL_COLLECTION_NAME=legal_knowledge
DATABASE_PATH=data/chroma_db
CHUNK_SIZE=800
CHUNK_OVERLAP=100
```

---

## Architecture Implemented (Phase 2)

### Dual-Source RAG Pipeline

```
User Question
    │
    ├─► EmbeddingService.embed_query()          [gemini-embedding-001, 3072-dim]
    │
    ├─► RetrievalService.retrieve()
    │       ├─► document_chunks (ChromaDB)      [filtered by document_id]
    │       └─► legal_knowledge (ChromaDB)      [global, pre-seeded, 37 entries]
    │
    ├─► AssembledContext (merged results)
    │
    └─► LLMService.generate_response()          [gemini-2.5-flash]
            └─► QueryResponse with Citations
```

### New Files (Phase 2)

| File | Purpose |
|------|---------|
| `app/services/chunking_service.py` | Page-aware recursive text splitting |
| `app/services/embedding_service.py` | Gemini embedding-001 (3072-dim) |
| `app/services/retrieval_service.py` | Dual-collection ChromaDB retrieval |
| `app/services/llm_service.py` | Gemini 2.5-flash response generation |
| `app/services/rag_service.py` | Full orchestration (ingest + query) |
| `app/core/prompts.py` | 3 prompt templates |
| `data/legal_knowledge_base.json` | 37 curated Indian legal knowledge entries |
| `scripts/seed_legal_knowledge.py` | ChromaDB legal KB seeder |
| `scripts/generate_knowledge_base.py` | One-time KB generator |
| `scripts/init_chroma.py` | Dual-collection manager with reset |
| `scripts/test_rag.py` | 18-check E2E validation suite |

### Modified Files (Phase 2)

| File | Change |
|------|--------|
| `app/models/chat.py` | `Citation`: added `source_type`, `act_name`, `act_section`, `category`; `QueryResponse`: added `has_legal_context` |
| `app/core/config.py` | Added all Phase 2 settings; `cors_origins_list` and `allowed_extensions_set` properties |
| `app/core/dependencies.py` | 8-service DI providers (was 2) |
| `app/services/storage_service.py` | `document_id` optional in `search()`; cosine-ready collection creation |
| `app/api/documents.py` | Upload triggers chunk→embed→store after OCR |
| `app/api/chat.py` | Full dual-source RAG (was stub) |

---

## ChromaDB State (Post-Validation)

| Collection | Chunks | Distance Metric | Embedding Dim |
|------------|--------|-----------------|---------------|
| `document_chunks` | 3+ (grows per upload) | L2 (`1/(1+d)` formula) | 3072 |
| `legal_knowledge` | 37 (pre-seeded) | L2 (`1/(1+d)` formula) | 3072 |

---

## Blockers

**None.** Backend Phase 2 is complete and fully validated. Frontend Foundation Agent may begin.
