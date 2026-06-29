# Project State Report — Lexify India
**Date:** 2026-06-29
**Phase:** 4B complete (Legal KB expansion, UI simplification, E2E verification)
**Build:** ✅ Exit code 0 · 0 TypeScript errors · 12 routes

---

## Product Summary

Lexify India is an AI-powered legal assistant for Indian citizens. The frontend is a
Next.js 16 (App Router) application styled with Tailwind CSS v4. The product has two
modes that coexist in a single chat workspace:

1. **General Legal Assistant** — user asks legal questions without uploading a document
2. **Document Analysis** — user uploads a legal document, then questions are answered
   using dual-source RAG (document chunks + legal knowledge base)

The primary entry point is `/chat`. `/upload` is a secondary action accessible from the
chat workspace and sidebar. There is no dashboard.

---

## Route Map

| Route | Type | Description |
|-------|------|-------------|
| `/` | Static | Landing page — hero, how-it-works, document types, features, footer |
| `/chat` | Static | General chat workspace — primary entry point |
| `/chat/[documentId]` | Dynamic | Document-specific chat workspace |
| `/documents` | Static | Document library — searchable/filterable grid |
| `/documents/[id]` | Dynamic | Individual document detail view |
| `/upload` | Static | Document upload — multi-state (idle/uploading/processing/complete/error) |
| `/settings` | Static | Redirects to /settings/appearance |
| `/settings/appearance` | Static | Typography + Accessibility toggles |
| `/settings/account` | Static | Account settings |
| `/settings/ai` | Static | AI settings |
| `/settings/documents` | Static | Document settings |

---

## Component Inventory

### Layout
| Component | File | Status |
|-----------|------|--------|
| AppShell | components/layout/AppShell.tsx | ✅ Complete |
| Sidebar | components/layout/Sidebar.tsx | ✅ Complete — Chat-first nav |
| TopBar | components/layout/TopBar.tsx | ✅ Complete |
| BottomNav | components/layout/BottomNav.tsx | ✅ Complete — Chat/Docs/Upload/Settings |
| MobileDrawer | components/layout/MobileDrawer.tsx | ✅ Complete |

### Landing
| Component | File | Status |
|-----------|------|--------|
| LandingNav | components/landing/LandingNav.tsx | ✅ Complete — smooth-scroll |
| HeroSection | components/landing/HeroSection.tsx | ✅ Complete — /chat CTA |
| HowItWorks | components/landing/HowItWorks.tsx | ✅ Complete |
| DocumentTypeCards | components/landing/DocumentTypeCards.tsx | ✅ Complete |
| FeatureHighlights | components/landing/FeatureHighlights.tsx | ✅ Complete |
| Footer | components/landing/Footer.tsx | ✅ Complete — 4-column grid |

### Chat
| Component | File | Status |
|-----------|------|--------|
| ChatInput | components/chat/ChatInput.tsx | ✅ Complete — pill shape, 760px constrained, no mic, no focus border |
| MessageBubble | components/chat/MessageBubble.tsx | ✅ Complete — max-w-[72%] right-aligned |
| AIResponseBlock | components/chat/AIResponseBlock.tsx | ✅ Complete — flex-1 full width |
| SourcesSection | components/chat/SourcesSection.tsx | ✅ Complete — compact collapsible "View Sources (N)" button |
| CitationCard | components/chat/CitationCard.tsx | ✅ Complete — preserved, not called from SourcesSection |
| ConfidenceBadge | components/chat/ConfidenceBadge.tsx | ✅ Complete — preserved, not rendered |
| LegalContextBadge | components/chat/LegalContextBadge.tsx | ✅ Complete — preserved, not rendered |
| SuggestedChips | components/chat/SuggestedChips.tsx | ✅ Complete — 48px indent |
| ConversationTimestamp | components/chat/ConversationTimestamp.tsx | ✅ Complete — my-4 |

### Upload
| Component | File | Status |
|-----------|------|--------|
| UploadZone | components/upload/UploadZone.tsx | ✅ Complete |
| UploadProgressTimeline | components/upload/UploadProgressTimeline.tsx | ✅ Complete |

### Documents
| Component | File | Status |
|-----------|------|--------|
| DocumentCard | components/documents/DocumentCard.tsx | ✅ Complete |
| DocumentFilter | components/documents/DocumentFilter.tsx | ✅ Complete |

### Settings
| Component | File | Status |
|-----------|------|--------|
| SettingsNav | components/settings/SettingsNav.tsx | ✅ Complete |
| TypographySlider | components/settings/TypographySlider.tsx | ✅ Complete |
| ToggleRow | components/settings/ToggleRow.tsx | ✅ Complete |

---

## Chat Workspace Layout Specification (as implemented)

### Conversation Column
- Max-width: 760px
- Centering: margin 0 auto
- Horizontal padding: 24px both sides
- Applies to: empty state, active feed, loading dots — all states
- Outer panel (ambient glow) fills 100% of the content area to the right of the sidebar

### Message Feed
- padding-top: 32px (first message doesn't touch top bar)
- padding-bottom: 120px (last message doesn't sit behind composer)
- User bubble: max-w-[72%], right-aligned, wrapped in mb-24px div
- AI block: flex-1 (no max-width), left-aligned, wrapped in mb-32px div
- ConversationTimestamp: my-4 (16px above + below), centered in column

### Composer
- Position: direct child of flex column (naturally bottom-anchored, no position:fixed)
- Outer wrapper: shrink-0 w-full bg-bg-base, no separator line, pt-16 pb-24
- Inner: maxWidth 760px margin 0 auto px-24
- Input pill: minHeight 52px, borderRadius 26px, padding 14px 20px, items-center
- Pill: always bg-bg-input, NO border in any state (focused or unfocused)
- Focus state: visually neutral — no border, no glow, no color change. `outline: none` on textarea + buttons overrides global `*:focus-visible` rule
- Paperclip: 20px, #4A4A4A, hover #888888, outline: none
- Mic: removed
- Send: 36px circle, #22C55E when text present, hover #16A34A + box-shadow 0 0 12px rgba(34,197,94,0.30), outline: none

### SuggestedChips
- margin-left: 48px (w-9=36px avatar + gap-3=12px)
- margin-top: 16px, margin-bottom: 8px
- Chips: fit-content width, gap 8px, wrap naturally

### Top Bar
- General chat (/chat): quiet chrome — spacer + Upload Doc button only (no title label)
- Document chat (/chat/[documentId]): document filename, type badge, confidence badge, actions

### Empty State (/chat)
- Vertically centered via min-h-full flex column
- Icon → heading (mb-12) → subheading
- Cards: flex-row on sm+, gap-16, mt-32, each max-w-380px flex-1
- Chips: max 4, gap 8px, mt-16 from description

---

## Design System

| Token | Value |
|-------|-------|
| Background base | #080C08 |
| Background sidebar | #1A1A1A |
| Background surface | #252525 |
| Accent | #22C55E |
| Accent hover | #16A34A |
| Text primary | #FFFFFF |
| Text body | #EFEFEF |
| Text secondary | #888888 |
| Text muted | #666666 |
| Text placeholder | #4A4A4A |
| Border default | rgba(255,255,255,0.06) |
| Border hover | rgba(255,255,255,0.10) |
| Font | Inter, system-ui, sans-serif |
| Scroll behavior | smooth (html element) |

---

## State Management

| Concern | Mechanism |
|---------|-----------|
| Chat messages | React state via useChat hook |
| Document upload state | React state via useDocumentUpload hook |
| Document registry | localStorage (key: `lexify_documents`) |
| Theme | Hardcoded dark premium (ThemeSelector removed) |
| Sidebar collapse | Local React state per page |
| Mobile drawer | Local React state per page |

---

## API Integration (Frontend Layer)

All calls go to `NEXT_PUBLIC_API_URL` (default: `http://localhost:8000`).

| Frontend Action | API Call | Status |
|----------------|----------|--------|
| Upload document | POST /api/documents/upload | ✅ Wired |
| Document chat | POST /api/chat | ✅ Wired (via useChat) |
| General legal chat | POST /api/legal-chat | ✅ Wired |
| List documents | (no endpoint yet) | ⏳ localStorage fallback |
| Chat history | (no endpoint yet) | ⏳ Session-only state |

---

## Backend Status

- Framework: FastAPI (Python)
- CORS: localhost:3000 allowed
- Endpoints: POST /api/documents/upload, POST /api/chat, POST /api/legal-chat, GET /health
- Vector DB: ChromaDB with 49 seeded Indian legal entries
- Similarity Thresholds: `DOCUMENT_SIMILARITY_THRESHOLD = 0.40`, `LEGAL_SIMILARITY_THRESHOLD = 0.35`
- Embedding model: gemini-embedding-001 (3072-dim)
- LLM: gemini-2.5-flash
- OCR: PaddleOCR with PDF-direct + image fallback

---

## Known Limitations

| Area | Limitation | Impact |
|------|-----------|--------|
| Conversation history | Lost on page refresh | No persistence |
| Document list | localStorage only | Not synced to backend (API not yet added) |
| Auth | No authentication gate | Anyone can access all routes |
| LandingNav | Log In uses window.location.href | Minor — functional but not Link |
| Deployment | CORS Config | Backend CORS limits origin strictly to localhost |
| Deployment | GEMINI_API_KEY | Production deployment must dynamically inject valid token |

---

## Phase History

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 1 | Backend foundation (FastAPI, models, endpoints) | ✅ Complete |
| Phase 2 | RAG pipeline (ChromaDB, embeddings, Gemini, OCR) | ✅ Complete |
| Phase 3A | Frontend foundation (Next.js, design system, all pages) | ✅ Complete |
| Phase 3B | Chat-first pivot (remove dashboard, /chat entry, footer, nav) | ✅ Complete |
| Phase 3C | Chat workspace layout refinements (column constraint, composer, empty state) | ✅ Complete |
| Phase 3D | Composer focus-state cleanup (no border/glow/outline on focus) | ✅ Complete |
| Phase 4A | General Legal Chat Integration | ✅ Complete |
| Phase 4B | Legal KB expansion (49 entries), Chat UI simplification, E2E verification | ✅ Complete |

---

## Recommended Phase 4C Work

Phase 4B is fully complete. The following integration items remain:

### Priority 1 — Phase 4C: Document Library API
Add `GET /api/documents` endpoint returning user-scoped document list.
Update `getStoredDocuments()` in `lib/utils.ts` to call API instead of localStorage.

### Priority 2 — Phase 4D: Conversation Persistence
Add session and history endpoints. Update `useChat` to load history on mount and persist on send.

### Priority 3 — Auth Layer
Add JWT or OAuth authentication.
Add Next.js middleware to protect `/chat`, `/documents`, `/upload`, `/settings` routes.
Add login/signup pages.

### Priority 4 — Production Deployment
Inject correct `GEMINI_API_KEY` into production environment variables.
Configure `CORS_ORIGINS` to allow traffic from the deployed frontend domains instead of localhost only.
