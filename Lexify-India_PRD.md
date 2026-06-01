# Lexify-India: Product Requirements Document

**Version:** 1.0  
**Date:** May 25, 2026  
**Status:** Active Development Blueprint  
**Project Type:** AI-Assisted Hackathon MVP  

---

## Executive Summary

**Lexify-India** is an AI-powered legal document understanding platform designed to help ordinary Indian citizens comprehend complex legal documents before signing them. The system uses RAG (Retrieval-Augmented Generation) to provide document-grounded answers, reducing confusion caused by legal jargon and improving legal accessibility across India.

**Core Value Proposition:**  
"Upload your legal document. Ask questions. Get clear answers with exact references."

**Target Timeline:** 4-day hackathon sprint  
**Development Model:** Multi-agent AI-assisted execution  
**Architecture Philosophy:** Modular, integration-safe, deployment-ready  

---

## Project Vision & Philosophy

### Problem Statement
Indian citizens frequently encounter complex legal documents (rental agreements, employment contracts, NDAs, property documents) without understanding their rights, obligations, or risks. Legal consultation is expensive and often inaccessible.

### Solution Approach
A document-centric AI system that:
- Extracts text from legal documents (PDFs, scans)
- Answers user questions using only document content
- Provides citations for every claim
- Simplifies legal language without fabricating advice
- Remains grounded in source material

### Product Philosophy

**What Lexify-India IS:**
- A document reading companion
- A citation-based explanation system
- A legal jargon translator
- A grounded AI assistant

**What Lexify-India IS NOT:**
- A generic chatbot
- A legal advisor
- A document generator
- A case law research tool

**Design Principles:**
1. **Trust Through Transparency**: Always cite sources
2. **Grounding Over Generation**: Answer only from documents
3. **Clarity Over Complexity**: Simplify without oversimplifying
4. **Accessibility First**: Design for Indian users, mobile-first
5. **Modular Architecture**: Build for maintainability and iteration

---

## Multi-Agent Architecture

This project will be executed using specialized AI agents within the Antigravity workspace. Each agent owns specific domains, follows clear boundaries, and coordinates through defined integration points.

### Agent Roster & Responsibilities

#### **1. Backend Architecture Agent**
**Agent Name:** `backend-architect`  
**Model Recommendation:** Claude Sonnet 4.5  

**Core Responsibility:**  
Design and implement the core FastAPI backend architecture, service layer, and API contracts.

**Scope Boundaries:**
- FastAPI application setup and configuration
- API endpoint design and implementation
- Service layer architecture (abstract interfaces)
- Core configuration management (`core/config.py`)
- Middleware, CORS, error handling
- Request/response models (Pydantic schemas)
- API documentation (OpenAPI/Swagger)

**Primary Ownership:**
```
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── documents.py
│   │   └── chat.py
│   ├── models/
│   │   ├── document.py
│   │   └── chat.py
│   └── core/
│       ├── config.py
│       ├── dependencies.py
│       └── exceptions.py
```

**Input Expectations:**
- PRD technical specifications
- API design requirements
- Integration requirements from other agents

**Output Deliverables:**
- FastAPI application scaffold
- API endpoint definitions
- Pydantic models
- Configuration system
- API documentation

**Integration Points:**
- Receives service implementations from specialized agents
- Provides API contracts to Frontend Agent
- Coordinates with Integration Agent for end-to-end testing

**Execution Rules:**
- NEVER implement service logic (OCR, RAG, embeddings) - only coordinate
- ALWAYS define clear interfaces for services
- MUST maintain API versioning structure
- MUST document all endpoints with OpenAPI standards

---

#### **2. OCR & Document Processing Agent**
**Agent Name:** `ocr-processor`  
**Model Recommendation:** Claude Sonnet 4.5  

**Core Responsibility:**  
Implement text extraction from uploaded documents with structure preservation.

**Scope Boundaries:**
- PaddleOCR integration
- PDF text extraction
- Image preprocessing (deskew, denoise)
- Text structure preservation (pages, sections)
- Fallback mechanisms for poor-quality scans
- Document metadata extraction

**Primary Ownership:**
```
backend/
├── app/
│   ├── services/
│   │   ├── ocr_service.py
│   │   └── document_processor.py
│   └── utils/
│       └── image_preprocessing.py
├── data/
│   └── uploads/
```

**Input Expectations:**
- Uploaded file path (PDF, image)
- Processing configuration from Backend Architect

**Output Deliverables:**
- Extracted text with metadata (pages, sections)
- Structured document object
- Quality metrics (confidence scores)
- Error handling for failed extractions

**Integration Points:**
- Called by Backend API endpoints
- Passes extracted text to Chunking Agent
- Reports processing status to Frontend

**Execution Rules:**
- MUST handle multiple file formats (PDF, JPG, PNG)
- MUST preserve page numbers and structure
- MUST implement fallback for failed OCR
- NEVER store sensitive document content permanently without user consent

---

#### **3. RAG Pipeline Agent**
**Agent Name:** `rag-engine`  
**Model Recommendation:** Claude Sonnet 4.5  

**Core Responsibility:**  
Implement the complete RAG pipeline: chunking, embedding, retrieval, and response generation.

**Scope Boundaries:**
- Document chunking with metadata preservation
- Embedding generation (Gemini API)
- Vector database operations (ChromaDB)
- Similarity search and retrieval
- Context assembly for LLM
- Response generation with citations
- Prompt engineering

**Primary Ownership:**
```
backend/
├── app/
│   ├── services/
│   │   ├── chunking_service.py
│   │   ├── embedding_service.py
│   │   ├── rag_service.py
│   │   └── retrieval_service.py
│   └── core/
│       └── prompts.py
├── data/
│   └── chroma_db/
```

**Input Expectations:**
- Extracted document text from OCR Agent
- User query from API endpoint
- Document ID for context filtering

**Output Deliverables:**
- Document chunks with embeddings stored in ChromaDB
- Retrieved context for queries
- Generated responses with citations
- Confidence scores

**Integration Points:**
- Receives processed text from OCR Agent
- Integrates with Vector DB Agent for storage
- Provides responses to Backend API
- Coordinates with Prompt Engineering (embedded in this agent)

**Execution Rules:**
- MUST preserve chunk metadata (page, section, clause)
- MUST implement similarity threshold filtering
- MUST generate citations for all claims
- MUST handle "information not found" cases gracefully
- NEVER hallucinate information not in document

---

#### **4. Vector Database Agent**
**Agent Name:** `vector-db-manager`  
**Model Recommendation:** Claude Sonnet 4.5  

**Core Responsibility:**  
Manage ChromaDB operations, schema design, and query optimization.

**Scope Boundaries:**
- ChromaDB setup and configuration
- Collection management
- Metadata schema design
- Query optimization
- Index management
- Data persistence strategy

**Primary Ownership:**
```
backend/
├── app/
│   └── services/
│       └── storage_service.py
├── data/
│   └── chroma_db/
└── scripts/
    └── init_chroma.py
```

**Input Expectations:**
- Embeddings from RAG Agent
- Metadata structure requirements
- Query patterns for optimization

**Output Deliverables:**
- Configured ChromaDB instance
- Storage service interface
- Query methods (similarity search, filtering)
- Data migration scripts if needed

**Integration Points:**
- Provides storage interface to RAG Agent
- Coordinates with Deployment Agent for database setup
- Ensures data persistence across deployments

**Execution Rules:**
- MUST design schema with document_id filtering
- MUST optimize for fast similarity search
- MUST handle concurrent access safely
- NEVER expose raw database interface to API layer

---

#### **5. Frontend Foundation Agent**
**Agent Name:** `frontend-foundation`  
**Model Recommendation:** Claude Sonnet 4.5  

**Core Responsibility:**  
Establish Next.js architecture, routing, state management, and API client foundation.

**Scope Boundaries:**
- Next.js project setup (App Router)
- Tailwind CSS + shadcn/ui configuration
- API client layer (`lib/api.ts`)
- TypeScript types and interfaces
- Route structure and navigation
- State management patterns
- Error boundary implementation

**Primary Ownership:**
```
frontend/
├── app/
│   ├── page.tsx
│   ├── upload/
│   ├── chat/
│   └── layout.tsx
├── lib/
│   ├── api.ts
│   ├── types.ts
│   └── utils.ts
├── styles/
└── public/
```

**Input Expectations:**
- API contracts from Backend Architect
- Design system requirements
- Routing structure

**Output Deliverables:**
- Configured Next.js application
- API client with type safety
- Base layouts and routing
- Global styles and theme

**Integration Points:**
- Implements API contracts from Backend
- Provides structure for UI Component Agent
- Coordinates with Frontend MCP workflows

**Execution Rules:**
- MUST use TypeScript strictly
- MUST create reusable API client functions
- MUST implement proper error handling
- MUST structure for component modularity
- SHOULD design for MCP integration (Stitch, Figma)

---

#### **6. UI Component Agent**
**Agent Name:** `ui-components`  
**Model Recommendation:** Claude Sonnet 4.5  

**Core Responsibility:**  
Build React components for upload, chat, document viewing, and citation display.

**Scope Boundaries:**
- Component implementation (shadcn/ui + custom)
- Component composition and layouts
- Interactive UI elements
- Loading states and animations
- Mobile responsiveness
- Accessibility (ARIA labels, keyboard navigation)

**Primary Ownership:**
```
frontend/
├── components/
│   ├── ui/              # shadcn components
│   ├── UploadZone.tsx
│   ├── ChatInterface.tsx
│   ├── DocumentViewer.tsx
│   ├── MessageBubble.tsx
│   ├── CitationCard.tsx
│   └── LoadingStates.tsx
```

**Input Expectations:**
- Design requirements from PRD
- API response types from Frontend Foundation
- Component specifications

**Output Deliverables:**
- Reusable React components
- Component documentation
- Usage examples
- Responsive designs

**Integration Points:**
- Uses API client from Frontend Foundation
- May receive initial designs from Figma MCP
- Coordinates with UX Agent for refinements

**Execution Rules:**
- MUST follow shadcn/ui patterns
- MUST implement proper TypeScript types
- MUST design for reusability
- MUST handle loading/error states
- SHOULD support future AI-generated UI modifications
- NEVER tightly couple to specific data sources

---

#### **7. Integration & Testing Agent**
**Agent Name:** `integration-coordinator`  
**Model Recommendation:** Claude Sonnet 4.5  

**Core Responsibility:**  
Coordinate cross-agent integration, test end-to-end flows, and ensure system coherence.

**Scope Boundaries:**
- Integration testing (frontend ↔ backend)
- End-to-end flow validation
- API contract verification
- Error flow testing
- Performance testing
- Integration documentation

**Primary Ownership:**
```
backend/
└── tests/
    ├── integration/
    └── test_e2e.py

frontend/
└── tests/
    └── integration/

scripts/
├── test_upload_flow.py
└── test_query_flow.py
```

**Input Expectations:**
- Completed modules from all agents
- API documentation
- Integration requirements

**Output Deliverables:**
- Integration test suite
- End-to-end test scenarios
- Bug reports and coordination
- Integration checklist

**Integration Points:**
- Tests all agent outputs together
- Coordinates bug fixes across agents
- Validates API contracts
- Reports to all agents

**Execution Rules:**
- MUST test critical path: Upload → OCR → Embed → Query → Response
- MUST validate API contracts match implementation
- MUST test error scenarios
- MUST coordinate fixes without modifying core logic
- NEVER implement features - only test and coordinate

---

#### **8. Deployment Agent**
**Agent Name:** `deployment-engineer`  
**Model Recommendation:** Claude Sonnet 4.5  

**Core Responsibility:**  
Prepare deployment configurations, environment setup, and production readiness.

**Scope Boundaries:**
- Vercel configuration (frontend)
- Render/Railway configuration (backend)
- Environment variable management
- Docker configuration (if needed)
- Production security setup
- Deployment scripts

**Primary Ownership:**
```
backend/
├── Dockerfile
├── requirements.txt
├── .env.example
└── render.yaml

frontend/
├── next.config.js
├── vercel.json
└── .env.local.example

scripts/
├── deploy_backend.sh
└── setup_production.sh
```

**Input Expectations:**
- Stable codebase from all agents
- Environment requirements
- Production configuration needs

**Output Deliverables:**
- Deployment-ready configurations
- Environment setup documentation
- Production deployment guide
- Monitoring setup (basic)

**Integration Points:**
- Coordinates with all agents for dependencies
- Ensures Vector DB persistence
- Validates API connectivity in production

**Execution Rules:**
- MUST document all environment variables
- MUST test deployment in staging first
- MUST ensure data persistence strategy
- NEVER expose secrets in code

---

### Agent Execution Hierarchy

```
Phase 1: Foundation (Parallel Execution)
├── Backend Architecture Agent → API scaffold
├── Frontend Foundation Agent → Next.js scaffold
└── Vector DB Agent → ChromaDB setup

Phase 2: Core Services (Sequential with Dependencies)
├── OCR Agent → Document processing
│   └── Depends on: Backend Architect (API endpoints)
│
├── RAG Pipeline Agent → Chunking, embedding, retrieval
│   └── Depends on: OCR Agent (text output), Vector DB Agent (storage)
│
└── UI Component Agent → Upload & Chat components
    └── Depends on: Frontend Foundation (API client)

Phase 3: Integration (Parallel Testing)
├── Integration Agent → Test all flows
│   └── Depends on: All previous agents
│
└── UI Refinement → Polish and responsiveness
    └── Depends on: Integration Agent (identified issues)

Phase 4: Deployment (Sequential)
└── Deployment Agent → Production setup
    └── Depends on: Integration Agent (validated system)
```

---

### Inter-Agent Workflow & Coordination

#### **Communication Protocol**

**Agent Handoff Format:**
```markdown
FROM: [Agent Name]
TO: [Target Agent Name]
STATUS: [COMPLETED | IN_PROGRESS | BLOCKED]
OUTPUT: [Deliverable description]
LOCATION: [File paths]
INTEGRATION_NOTES: [Any special requirements]
BLOCKERS: [Issues affecting downstream agents]
```

#### **Integration Checkpoints**

**Checkpoint 1: API Contract Validation**
- **Trigger**: Backend Architect completes API definitions
- **Participants**: Backend Architect, Frontend Foundation, RAG Agent
- **Validation**: API schemas match expected input/output
- **Gate**: Frontend can mock API responses

**Checkpoint 2: OCR → RAG Handoff**
- **Trigger**: OCR Agent completes text extraction
- **Participants**: OCR Agent, RAG Agent
- **Validation**: Text structure preserves metadata
- **Gate**: RAG Agent can chunk and embed

**Checkpoint 3: Backend → Frontend Integration**
- **Trigger**: All backend services deployed
- **Participants**: All Backend Agents, Frontend Agents, Integration Agent
- **Validation**: End-to-end upload → query flow works
- **Gate**: Integration tests pass

**Checkpoint 4: Pre-Deployment Validation**
- **Trigger**: All features complete
- **Participants**: Integration Agent, Deployment Agent
- **Validation**: System works in staging environment
- **Gate**: Ready for production deployment

---

### Workspace Operating System

#### **PRD-Centric Execution Model**

This PRD serves as the **single source of truth** for all agents. Agents MUST:
1. Reference the PRD before starting any implementation
2. Follow defined boundaries strictly
3. Update status in agent handoff format
4. Flag architecture changes for review

#### **Dynamic Project Structure Management**

**Execution Prompts Generate Structure:**
Claude should generate prompts that:
- Create folder structures on-demand
- Scaffold new modules progressively
- Generate integration layers when needed
- Update configurations dynamically

**Example Execution Prompt Structure:**
```markdown
I am the [Agent Name] implementing [Feature].

According to the PRD:
- My responsibility: [Scope from PRD]
- My boundaries: [What I should NOT touch]
- Integration points: [Who I work with]

Implementation Plan:
1. Create folder structure: [List]
2. Implement modules: [List]
3. Test integration with: [Agents]
4. Handoff to: [Next Agent]

Generate the implementation following PRD architecture.
```

#### **Architecture Stability Strategy**

**Governance Rules:**
1. **No Cross-Boundary Modifications**: Agents NEVER modify files outside their ownership
2. **Integration-First Design**: All features designed with future integration in mind
3. **Interface Stability**: Once APIs defined, changes require coordination
4. **Progressive Integration**: Features integrated incrementally, not all at once
5. **Rollback Safety**: Each phase independently testable

**Architecture Change Protocol:**
If an agent needs to modify architecture:
1. Flag the issue with reasoning
2. Propose change in agent handoff
3. Wait for coordination decision
4. Update PRD if approved
5. Notify affected agents

---

### Frontend MCP Integration Strategy

#### **Design-to-Code Workflow Support**

The frontend architecture supports:

**1. Stitch MCP Integration**
- Component structure compatible with Stitch-generated UI
- Clean component boundaries for AI regeneration
- Props interfaces support dynamic generation
- Styling remains consistent across generations

**2. Figma MCP Integration**
- Design tokens from Figma translate to Tailwind classes
- Component variants align with Figma component structure
- Responsive breakpoints match Figma frames

**3. Hybrid Development Approach**
```
AI-Generated UI → Manual Refinement → AI Re-generation

Supported patterns:
- Generate initial UI with MCP
- Manually refine logic/state
- Regenerate styling/layout later
- Component structure remains stable
```

#### **Frontend Flexibility Requirements**

**Architecture Must Support:**
- Component replacement without breaking integrations
- Partial UI regeneration (one component at a time)
- Manual override of AI-generated styles
- Gradual migration from AI-generated to manual code

**Components Must Be:**
- Self-contained (props in, JSX out)
- Loosely coupled to data sources
- Style-agnostic (Tailwind classes, not hardcoded)
- Refactorable without API changes

**Example: Upload Component Evolution**
```typescript
// Phase 1: AI-generated from Stitch
<UploadZone onUpload={handleUpload} />

// Phase 2: Manually refined with validation
<UploadZone 
  onUpload={handleUpload}
  validateFile={customValidation}
  maxSize={10 * 1024 * 1024}
/>

// Phase 3: Regenerated with new design
// Component interface stays same, UI regenerated
<UploadZone onUpload={handleUpload} /> // New styling
```

---

## Technical Specifications

### Technology Stack

#### **Frontend**
- **Framework**: Next.js 14+ (App Router)
- **Styling**: Tailwind CSS 3.4+
- **UI Library**: shadcn/ui
- **Language**: TypeScript 5.0+
- **State Management**: React hooks (useState, useContext)
- **HTTP Client**: fetch API with custom wrapper

#### **Backend**
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Async Runtime**: asyncio
- **Validation**: Pydantic 2.0+
- **CORS**: FastAPI CORS middleware

#### **AI/ML Stack**
- **LLM**: Gemini API (gemini-pro)
- **Embeddings**: Gemini embeddings (embedding-001)
- **OCR**: PaddleOCR 2.7+
- **RAG Framework**: LangChain 0.1+
- **Vector DB**: ChromaDB 0.4+

#### **Deployment**
- **Frontend Hosting**: Vercel
- **Backend Hosting**: Render / Railway
- **File Storage**: Local filesystem (MVP) → S3 (production)
- **Database**: ChromaDB (persistent volume)

---

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Upload Page  │  │  Chat Page   │  │  Document Viewer   │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS/REST API
┌────────────────────────────▼────────────────────────────────────┐
│                        API Gateway (FastAPI)                     │
│  ┌─────────────────────┐         ┌─────────────────────┐       │
│  │  /api/documents/    │         │    /api/chat        │       │
│  │  - POST /upload     │         │    - POST /query    │       │
│  │  - GET /{doc_id}    │         │    - GET /history   │       │
│  └─────────────────────┘         └─────────────────────┘       │
└────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                         Service Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │ OCR Service  │  │ RAG Service  │  │ Storage Service  │     │
│  │              │  │              │  │                  │     │
│  │ - Extract    │  │ - Chunk      │  │ - Save files     │     │
│  │ - Preprocess │  │ - Embed      │  │ - Manage docs    │     │
│  │ - Structure  │  │ - Retrieve   │  │ - Query DB       │     │
│  │              │  │ - Generate   │  │                  │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    External Integrations                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │  Gemini API  │  │  ChromaDB    │  │  File System     │     │
│  │              │  │              │  │                  │     │
│  │ - LLM calls  │  │ - Embeddings │  │ - PDF storage    │     │
│  │ - Embeddings │  │ - Similarity │  │ - Temp files     │     │
│  │              │  │   search     │  │                  │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

---

### Data Models

#### **Document Model**
```python
class Document(BaseModel):
    document_id: str          # UUID
    filename: str
    upload_date: datetime
    file_path: str
    file_size: int
    num_pages: int
    extraction_status: str    # "pending" | "completed" | "failed"
    metadata: Dict[str, Any]  # Language, type, etc.
```

#### **DocumentChunk Model**
```python
class DocumentChunk(BaseModel):
    chunk_id: str             # UUID
    document_id: str
    text: str
    page_number: int
    section: Optional[str]
    clause_number: Optional[str]
    start_char: int
    end_char: int
    metadata: Dict[str, Any]
```

#### **Query Model**
```python
class QueryRequest(BaseModel):
    document_id: str
    question: str
    conversation_history: List[Message] = []
    
class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: str          # "high" | "medium" | "low"
    related_sections: List[str]
```

#### **Citation Model**
```python
class Citation(BaseModel):
    text: str                # Cited text
    page_number: int
    section: Optional[str]
    similarity_score: float
    chunk_id: str
```

---

### API Specification

#### **1. Document Upload**

**Endpoint:** `POST /api/documents/upload`

**Request:**
```http
POST /api/documents/upload HTTP/1.1
Content-Type: multipart/form-data

file: [binary file data]
```

**Response:** `201 Created`
```json
{
  "document_id": "uuid-xxx-xxx",
  "filename": "rental_agreement.pdf",
  "num_pages": 12,
  "extraction_status": "completed",
  "preview_text": "This Rental Agreement is entered into...",
  "metadata": {
    "file_size": 2048576,
    "language": "en",
    "document_type": "rental_agreement"
  }
}
```

**Error Response:** `400 Bad Request`
```json
{
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "Only PDF and image files are supported",
    "details": "Received file type: .docx"
  }
}
```

---

#### **2. Document Query**

**Endpoint:** `POST /api/chat`

**Request:**
```json
{
  "document_id": "uuid-xxx-xxx",
  "question": "What is the notice period for termination?",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is the monthly rent?"
    },
    {
      "role": "assistant",
      "content": "The monthly rent is ₹25,000..."
    }
  ]
}
```

**Response:** `200 OK`
```json
{
  "answer": "According to Clause 8.2, either party must provide 1 month's written notice before terminating the agreement.",
  "citations": [
    {
      "text": "Either party may terminate this Agreement by providing one (1) month's written notice to the other party.",
      "page_number": 5,
      "section": "Clause 8.2 - Termination",
      "similarity_score": 0.92,
      "chunk_id": "chunk-xxx"
    }
  ],
  "confidence": "high",
  "related_sections": [
    "Clause 8.1 - Duration",
    "Clause 9 - Consequences of Termination"
  ]
}
```

**Error Response:** `404 Not Found`
```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "The specified document does not exist",
    "suggestion": "Please upload the document first"
  }
}
```

---

#### **3. Document Retrieval**

**Endpoint:** `GET /api/documents/{document_id}`

**Response:** `200 OK`
```json
{
  "document_id": "uuid-xxx-xxx",
  "filename": "rental_agreement.pdf",
  "upload_date": "2024-01-15T10:30:00Z",
  "num_pages": 12,
  "extraction_status": "completed",
  "metadata": {
    "file_size": 2048576,
    "language": "en",
    "document_type": "rental_agreement"
  },
  "download_url": "/api/documents/uuid-xxx-xxx/download"
}
```

---

### RAG Pipeline Specification

#### **1. Document Processing Flow**

```python
# Step 1: OCR Extraction
extracted_text = ocr_service.extract_text(pdf_path)
# Output: List[PageText] with structure

# Step 2: Chunking
chunks = chunking_service.chunk_document(
    text=extracted_text,
    chunk_size=800,        # tokens
    chunk_overlap=100,     # tokens
    preserve_structure=True
)
# Output: List[DocumentChunk] with metadata

# Step 3: Embedding Generation
embeddings = embedding_service.generate_embeddings(
    chunks=chunks,
    batch_size=10
)
# Output: List[float] vectors

# Step 4: Vector Storage
storage_service.store_chunks(
    document_id=doc_id,
    chunks=chunks,
    embeddings=embeddings
)
# Output: Stored in ChromaDB with metadata
```

#### **2. Query Processing Flow**

```python
# Step 1: Query Embedding
query_embedding = embedding_service.embed_query(question)

# Step 2: Similarity Search
retrieved_chunks = retrieval_service.search(
    query_embedding=query_embedding,
    document_id=doc_id,
    top_k=5,
    similarity_threshold=0.7
)

# Step 3: Context Assembly
context = rag_service.assemble_context(
    chunks=retrieved_chunks,
    max_tokens=3000
)

# Step 4: Prompt Construction
prompt = rag_service.build_prompt(
    context=context,
    question=question,
    conversation_history=history
)

# Step 5: LLM Generation
response = llm.generate(prompt)

# Step 6: Citation Extraction
answer_with_citations = rag_service.extract_citations(
    response=response,
    retrieved_chunks=retrieved_chunks
)
```

---

### Prompt Engineering Specifications

#### **System Prompt (RAG)**

```python
SYSTEM_PROMPT = """You are a legal document analysis assistant for Lexify-India.

Your purpose is to help users understand their legal documents by answering questions based ONLY on the provided document context.

CRITICAL RULES:
1. Answer ONLY using information from the provided context below
2. If the answer is not in the context, respond: "I cannot find this information in the document."
3. ALWAYS cite the specific page and section where you found the information
4. NEVER make assumptions or add external legal knowledge
5. If you are uncertain, express it clearly
6. Use simple language to explain legal terms
7. Highlight important obligations, penalties, and deadlines

Context format:
[Page X, Section Y]: <relevant text>

Your responses MUST include:
- Direct answer based on context
- Citation in format: [Page X, Section Y]
- Explanation in simple language if legal jargon is involved

Remember: You are a document reading assistant, not a legal advisor. Stay grounded in the document content."""
```

#### **User Query Template**

```python
USER_QUERY_TEMPLATE = """Document Context:
{context}

User Question: {question}

Provide a clear, concise answer with citations."""
```

#### **Simplification Prompt (Stretch Feature)**

```python
SIMPLIFICATION_PROMPT = """Explain the following legal clause in simple language that a non-lawyer can understand:

Clause: {clause_text}

Explain:
1. What it means in everyday language
2. What obligations it creates
3. Any important deadlines or penalties
4. Any risks or things to watch out for

Use simple words and short sentences."""
```

---

### Chunking Strategy

#### **Recursive Chunking with Metadata Preservation**

**Parameters:**
- **Chunk Size**: 600-800 tokens (~400-600 words)
- **Overlap**: 100 tokens (~80 words)
- **Separators**: `["\n\n", "\n", ". ", " "]` (in priority order)

**Metadata Preserved:**
- `page_number`: Source page in PDF
- `section`: Extracted section heading (Clause X, Article Y)
- `clause_number`: Legal clause identifier
- `start_char`, `end_char`: Position in document
- `document_id`: Parent document reference

**Special Handling:**
```python
# Preserve clause boundaries
if text.startswith("Clause") or text.startswith("Article"):
    # Ensure clause stays within one chunk
    chunk_strategy = "preserve_clause"

# Preserve numbered lists
if re.match(r"^\d+\.", text):
    # Keep numbered items together when possible
    chunk_strategy = "preserve_list"
```

---

### Error Handling Strategy

#### **Error Categories & Responses**

**1. OCR Failures**
```python
{
  "error": {
    "code": "OCR_EXTRACTION_FAILED",
    "message": "Unable to extract text from document",
    "details": "Image quality too low or unsupported format",
    "suggestion": "Try uploading a clearer scan or manually paste the text",
    "fallback_available": true
  }
}
```

**2. Empty Retrieval**
```python
{
  "answer": "I cannot find information about that in the document.",
  "confidence": "none",
  "suggestion": "Try rephrasing your question or asking about a different topic covered in the document."
}
```

**3. API Rate Limits**
```python
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again in a few moments.",
    "retry_after": 60  // seconds
  }
}
```

**4. Document Not Found**
```python
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "The specified document does not exist or has been deleted",
    "suggestion": "Please upload the document again"
  }
}
```

---

## Implementation Roadmap

### Phase 1: Foundation Setup (Day 1)

**Duration:** 8 hours  
**Goal:** Establish working backend and frontend scaffolds

#### **Backend Architecture Agent Tasks**
- [ ] Initialize FastAPI project structure
- [ ] Setup CORS middleware
- [ ] Implement configuration management (`core/config.py`)
- [ ] Define Pydantic models for Document and Query
- [ ] Create API endpoints (stub implementations)
- [ ] Setup logging and error handling
- [ ] Generate OpenAPI documentation

**Deliverables:**
- FastAPI app running on `localhost:8000`
- API docs accessible at `/docs`
- Health check endpoint: `GET /health`

---

#### **Frontend Foundation Agent Tasks**
- [ ] Initialize Next.js 14 project with App Router
- [ ] Configure Tailwind CSS and shadcn/ui
- [ ] Setup TypeScript strict mode
- [ ] Create API client layer (`lib/api.ts`)
- [ ] Define TypeScript interfaces matching backend models
- [ ] Implement basic routing structure
- [ ] Setup error boundaries

**Deliverables:**
- Next.js app running on `localhost:3000`
- API client with type-safe methods
- Base layouts and routing working

---

#### **Vector DB Agent Tasks**
- [ ] Install and configure ChromaDB
- [ ] Design collection schema with metadata
- [ ] Implement storage service interface
- [ ] Test basic CRUD operations
- [ ] Setup persistent storage path

**Deliverables:**
- ChromaDB initialized at `/data/chroma_db`
- Storage service with basic methods
- Connection tested

---

**Integration Checkpoint 1:**
- Verify: Backend API responds to health checks
- Verify: Frontend can make API calls
- Verify: ChromaDB accepts test data

---

### Phase 2: Core Features (Day 2)

**Duration:** 10 hours  
**Goal:** Complete upload, OCR, and basic RAG functionality

#### **OCR & Document Processing Agent Tasks**
- [ ] Implement PaddleOCR integration
- [ ] Add PDF text extraction (PyPDF2/pdfplumber)
- [ ] Implement image preprocessing (deskew, denoise)
- [ ] Preserve structure (pages, sections)
- [ ] Create document processing endpoint handler
- [ ] Implement error handling and fallbacks

**Deliverables:**
- `POST /api/documents/upload` endpoint functional
- Text extraction working for PDFs and images
- Structured output with page numbers

---

#### **RAG Pipeline Agent Tasks**
- [ ] Implement chunking service with metadata preservation
- [ ] Integrate Gemini embeddings API
- [ ] Create embedding generation pipeline
- [ ] Implement context assembly logic
- [ ] Engineer RAG system prompt
- [ ] Build LLM query pipeline
- [ ] Implement citation extraction logic

**Deliverables:**
- Document chunks stored in ChromaDB with embeddings
- Query endpoint returns answers with citations
- Basic RAG flow working end-to-end

---

#### **UI Component Agent Tasks**
- [ ] Build UploadZone component
- [ ] Create file upload handler
- [ ] Implement upload progress indicator
- [ ] Build ChatInterface component
- [ ] Create MessageBubble component
- [ ] Implement CitationCard component
- [ ] Add loading states

**Deliverables:**
- Functional upload UI
- Working chat interface
- Citation display component

---

**Integration Checkpoint 2:**
- Verify: Can upload PDF and see extracted text
- Verify: Can ask question and receive answer
- Verify: Citations displayed correctly
- Test: End-to-end flow with real document

---

### Phase 3: UX Polish & Integration (Day 3)

**Duration:** 10 hours  
**Goal:** Polish UI, improve UX, ensure stability

#### **UI Component Agent Tasks**
- [ ] Build DocumentViewer component (PDF display)
- [ ] Implement citation highlighting in viewer
- [ ] Add mobile responsiveness
- [ ] Improve loading animations
- [ ] Add empty states and error messages
- [ ] Implement suggested questions feature
- [ ] Add document summary on upload completion

**Deliverables:**
- Polished, professional UI
- Mobile-responsive design
- Improved user feedback

---

#### **Integration & Testing Agent Tasks**
- [ ] Test upload → OCR → embed flow
- [ ] Test query → retrieve → generate flow
- [ ] Test error scenarios (bad file, empty query)
- [ ] Validate API contracts
- [ ] Test on real Indian legal documents
- [ ] Performance testing (large documents)
- [ ] Create integration test suite

**Deliverables:**
- Integration test results
- Bug reports filed
- Performance benchmarks

---

#### **RAG Pipeline Agent Refinement**
- [ ] Improve prompt based on testing
- [ ] Tune similarity thresholds
- [ ] Optimize chunking parameters
- [ ] Add confidence scoring
- [ ] Implement "information not found" handling

**Deliverables:**
- Improved response quality
- Better hallucination prevention
- Optimized retrieval

---

**Integration Checkpoint 3:**
- Verify: All critical flows tested
- Verify: Mobile experience acceptable
- Verify: Error handling works gracefully
- Verify: Performance acceptable (<5s for queries)

---

### Phase 4: Deployment & Final Polish (Day 4)

**Duration:** 8 hours  
**Goal:** Deploy to production and prepare demo

#### **Deployment Agent Tasks**
- [ ] Configure Vercel for frontend
- [ ] Setup Render/Railway for backend
- [ ] Configure environment variables
- [ ] Setup persistent storage for ChromaDB
- [ ] Configure CORS for production domains
- [ ] Test deployment in staging
- [ ] Deploy to production
- [ ] Setup monitoring (basic logging)

**Deliverables:**
- Frontend deployed on Vercel
- Backend deployed on Render
- Production URLs working
- Environment configured

---

#### **Integration Agent Final Validation**
- [ ] Test production deployment
- [ ] Verify all features working in prod
- [ ] Load test with multiple users
- [ ] Prepare demo scenarios
- [ ] Document known limitations

**Deliverables:**
- Production validation report
- Demo script
- Known issues list

---

#### **Stretch Features (If Time Permits)**
- [ ] Clause detection and highlighting
- [ ] "Explain Simply" mode
- [ ] Hindi translation support
- [ ] Document summary generation

---

**Final Checkpoint:**
- Verify: System deployed and accessible
- Verify: Demo scenarios tested
- Verify: Critical bugs resolved
- Verify: Documentation complete

---

## Success Metrics

### MVP Success Criteria

**Functional Requirements:**
1. ✅ User can upload PDF legal documents
2. ✅ System extracts text with >80% accuracy
3. ✅ User can ask questions about the document
4. ✅ Responses include citations (page numbers)
5. ✅ System clearly states when info not found
6. ✅ UI is mobile-responsive

**Quality Requirements:**
1. ✅ Query response time <5 seconds
2. ✅ OCR accuracy >80% on clear scans
3. ✅ Zero hallucinations (answers not in doc)
4. ✅ All citations verifiable
5. ✅ System handles errors gracefully

**UX Requirements:**
1. ✅ Upload process clear and simple
2. ✅ Chat interface intuitive
3. ✅ Citations easily readable
4. ✅ Mobile experience usable
5. ✅ Professional, trustworthy design

### Hackathon Demo Criteria

**Demo Flow:**
1. Show landing page (30 seconds)
2. Upload sample rental agreement (30 seconds)
3. System processes and shows summary (30 seconds)
4. Ask 3 questions demonstrating:
   - Accurate retrieval with citations
   - Simplified explanation of legal terms
   - "Not found" scenario
5. Show document viewer with highlighted citations (30 seconds)
6. Explain technical architecture briefly (1 minute)

**Total Demo Time:** 3-4 minutes

---

## Deployment Strategy

### Frontend Deployment (Vercel)

**Configuration:**
```json
// vercel.json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url"
  }
}
```

**Environment Variables:**
- `NEXT_PUBLIC_API_URL`: Backend API base URL

---

### Backend Deployment (Render)

**Configuration:**
```yaml
# render.yaml
services:
  - type: web
    name: lexify-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: DATABASE_PATH
        value: /data/chroma_db
      - key: UPLOAD_DIR
        value: /data/uploads
```

**Environment Variables:**
- `GEMINI_API_KEY`: Gemini API credentials
- `DATABASE_PATH`: ChromaDB storage path
- `UPLOAD_DIR`: File upload directory
- `CORS_ORIGINS`: Allowed frontend origins

**Persistent Disk:**
- Mount persistent disk at `/data` for ChromaDB and uploads

---

### Production Considerations

**Security:**
- File upload size limits (10MB)
- Rate limiting on API endpoints
- Input validation on all endpoints
- CORS restricted to production domains
- No API key exposure in frontend

**Monitoring:**
- Basic logging to stdout
- Track API response times
- Monitor ChromaDB storage usage
- Track error rates

**Backup Strategy:**
- Periodic ChromaDB backups
- Document metadata backups
- Configuration backups

---

## Risk Mitigation

### Technical Risks

**Risk 1: OCR Quality on Poor Scans**
- **Mitigation**: Implement image preprocessing; provide manual text paste fallback
- **Contingency**: Focus demo on high-quality documents

**Risk 2: Gemini API Rate Limits**
- **Mitigation**: Implement request batching; cache embeddings
- **Contingency**: Switch to local embedding model if needed

**Risk 3: ChromaDB Performance with Large Documents**
- **Mitigation**: Optimize chunk size; implement pagination
- **Contingency**: Limit document size for MVP

**Risk 4: Frontend-Backend Integration Issues**
- **Mitigation**: Define API contracts early; use TypeScript for safety
- **Contingency**: Integration Agent coordinates fixes

**Risk 5: Deployment Problems**
- **Mitigation**: Test deployment early (Day 2); use proven platforms
- **Contingency**: Local deployment as fallback for demo

---

## Agent Coordination Rules

### Cross-Agent Communication Guidelines

**DO:**
- ✅ Reference PRD before any implementation
- ✅ Stay within defined boundaries
- ✅ Document handoffs clearly
- ✅ Test integrations at checkpoints
- ✅ Flag blockers immediately
- ✅ Update status regularly

**DON'T:**
- ❌ Modify files outside your ownership
- ❌ Change APIs without coordination
- ❌ Skip integration checkpoints
- ❌ Implement features outside your scope
- ❌ Make architecture changes unilaterally

### Conflict Resolution

**If boundaries are unclear:**
1. Flag the issue in handoff message
2. Reference PRD section for clarification
3. Propose solution with reasoning
4. Wait for coordination decision

**If integration fails:**
1. Integration Agent investigates
2. Identifies responsible agent(s)
3. Coordinates fix without assigning blame
4. Updates PRD if needed

**If architecture needs change:**
1. Agent proposes change with reasoning
2. All affected agents review
3. Update PRD if approved
4. Re-test integration checkpoints

---

## Appendix

### Folder Structure Reference

```
lexify-india/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── documents.py
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ocr_service.py
│   │   │   ├── document_processor.py
│   │   │   ├── chunking_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── retrieval_service.py
│   │   │   └── storage_service.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   └── chat.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── dependencies.py
│   │   │   ├── exceptions.py
│   │   │   └── prompts.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── image_preprocessing.py
│   ├── data/
│   │   ├── uploads/
│   │   └── chroma_db/
│   ├── tests/
│   │   ├── integration/
│   │   └── unit/
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── README.md
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   ├── upload/
│   │   │   └── page.tsx
│   │   └── chat/
│   │       └── [documentId]/
│   │           └── page.tsx
│   ├── components/
│   │   ├── ui/           # shadcn components
│   │   ├── UploadZone.tsx
│   │   ├── ChatInterface.tsx
│   │   ├── DocumentViewer.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── CitationCard.tsx
│   │   └── LoadingStates.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── utils.ts
│   ├── styles/
│   │   └── globals.css
│   ├── public/
│   ├── package.json
│   └── next.config.js
│
├── scripts/
│   ├── deploy_backend.sh
│   ├── test_integration.py
│   └── init_project.sh
│
└── Lexify-India_PRD.md  # This document
```

---

### Glossary

**RAG (Retrieval-Augmented Generation)**: AI technique that retrieves relevant context before generating responses, reducing hallucinations.

**Chunking**: Breaking documents into smaller segments for embedding and retrieval.

**Embedding**: Vector representation of text for semantic similarity search.

**ChromaDB**: Open-source vector database for storing and querying embeddings.

**Citation**: Reference to source document location (page, section) that supports a claim.

**Hallucination**: AI-generated information not present in source document (to be avoided).

**OCR (Optical Character Recognition)**: Technology to extract text from images and scanned documents.

**Semantic Search**: Finding relevant content based on meaning, not just keywords.

**MCP (Model Context Protocol)**: Integration framework for connecting AI to external tools and services.

---

### Document Version History

**v1.0 (May 25, 2026)**
- Initial PRD with complete multi-agent architecture
- Defined all agent responsibilities and boundaries
- Established integration checkpoints
- Documented API specifications
- Created implementation roadmap
- Added frontend MCP integration strategy

---

## Final Notes for AI Agents

This PRD is your **single source of truth**. Before implementing anything:

1. ✅ Read your agent section thoroughly
2. ✅ Understand your boundaries
3. ✅ Check integration dependencies
4. ✅ Follow the execution hierarchy
5. ✅ Communicate through defined protocols
6. ✅ Test at checkpoints
7. ✅ Stay modular and integration-safe

**Remember:** This is a coordinated AI engineering team, not individual code generation. Your work affects other agents. Stay within boundaries, communicate clearly, and build for integration.

**Primary Goal:** Ship a working, polished MVP in 4 days that demonstrates the value of AI-powered legal document understanding.

**Secondary Goal:** Maintain clean architecture that can scale post-hackathon.

**Success Indicator:** A demo that makes people say "I would actually use this."

---

**END OF PRD**
