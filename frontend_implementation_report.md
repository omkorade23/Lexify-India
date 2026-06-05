# Lexify India — Frontend Implementation Report
**Phase 3 — Frontend Foundation & UI Components**
**Date:** 2026-06-04

---

## Complete File Tree

```
frontend/
├── app/
│   ├── globals.css                      ✅ Tailwind v4 @theme tokens + utilities
│   ├── layout.tsx                       ✅ Root layout, Inter font, SEO metadata
│   ├── page.tsx                         ✅ Landing page
│   ├── dashboard/
│   │   ├── page.tsx                     ✅ Dashboard with command center
│   │   └── loading.tsx                  ✅ Skeleton loader
│   ├── documents/
│   │   ├── page.tsx                     ✅ Document library
│   │   └── [id]/page.tsx               ✅ Document detail
│   ├── chat/
│   │   └── [documentId]/page.tsx       ✅ Chat workspace
│   ├── upload/
│   │   └── page.tsx                     ✅ Upload flow (all 6 states)
│   └── settings/
│       ├── page.tsx                     ✅ Redirects to /settings/appearance
│       ├── appearance/page.tsx          ✅ Theme + typography + accessibility
│       ├── ai/page.tsx                  ✅ AI model preferences
│       ├── documents/page.tsx           ✅ Upload/processing preferences
│       └── account/page.tsx            ✅ Data management + app info
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx                  ✅ 268px persistent, collapsible
│   │   ├── AppShell.tsx                 ✅ Responsive shell (desktop/tablet/mobile)
│   │   ├── TopBar.tsx                   ✅ Mobile-aware top bar
│   │   ├── BottomNav.tsx                ✅ Mobile bottom tab bar
│   │   └── MobileDrawer.tsx             ✅ Mobile slide-in drawer
│   ├── landing/
│   │   ├── HeroSection.tsx              ✅ Glow, badge, CTAs, trust signals
│   │   ├── DocumentTypeCards.tsx        ✅ 6 document type cards
│   │   ├── HowItWorks.tsx               ✅ 4-step process with connecting line
│   │   ├── FeatureHighlights.tsx        ✅ 6 feature cards
│   │   └── LandingNav.tsx              ✅ Scroll-triggered glassmorphism nav
│   ├── dashboard/
│   │   ├── CommandCenterCard.tsx        ✅ Greeting + stats grid
│   │   ├── StatsCard.tsx               ✅ Stat display card
│   │   ├── QuickStartGrid.tsx          ✅ 4-card quick action grid
│   │   ├── RecentDocuments.tsx         ✅ Last 5 docs, navigates to chat
│   │   └── RecentConversations.tsx     ✅ Recent sessions list
│   ├── documents/
│   │   ├── DocumentCard.tsx            ✅ Grid card with type badge + hover
│   │   ├── DocumentGrid.tsx            ✅ Responsive grid with empty state
│   │   ├── DocumentTypeBadge.tsx       ✅ Green accent badge
│   │   ├── DocumentSearchBar.tsx       ✅ Search with focus treatment
│   │   └── FilterChips.tsx             ✅ Multi-filter chip group
│   ├── chat/
│   │   ├── ChatInput.tsx               ✅ Dark green input, auto-resize, send glow
│   │   ├── MessageBubble.tsx           ✅ User bubble right-aligned
│   │   ├── AIResponseBlock.tsx         ✅ Green avatar, badges, inline citations
│   │   ├── CitationCard.tsx            ✅ Document + legal_reference variants
│   │   ├── SourcesSection.tsx          ✅ SOURCES REFERENCED section
│   │   ├── SuggestedChips.tsx          ✅ Follow-up question chips
│   │   ├── ConfidenceBadge.tsx         ✅ Achromatic + semantic dot
│   │   ├── LegalContextBadge.tsx       ✅ Legal reference indicator
│   │   └── ConversationTimestamp.tsx   ✅ Centered date divider
│   ├── upload/
│   │   ├── UploadZone.tsx              ✅ Drag-drop, validation, drag-over green
│   │   ├── FilePreview.tsx             ✅ File card + Upload CTA
│   │   ├── ProcessingCard.tsx          ✅ Glassmorphism card with progress timeline
│   │   ├── ProcessingTimeline.tsx      ✅ Step-by-step progress indicators
│   │   └── UploadComplete.tsx          ✅ Success state with document preview
│   └── settings/
│       ├── SettingsNav.tsx             ✅ Inner nav matching sidebar treatment
│       ├── ThemeSelector.tsx           ✅ Theme cards with preview swatches
│       ├── TypographySlider.tsx        ✅ Green slider with live preview
│       └── ToggleRow.tsx               ✅ Green track toggle switch
├── lib/
│   ├── api.ts                          ✅ Typed fetch wrapper for all endpoints
│   ├── types.ts                        ✅ All interfaces matching backend contracts
│   └── utils.ts                        ✅ cn(), localStorage registry, formatters
├── hooks/
│   ├── useDocumentUpload.ts            ✅ 6-state upload state machine
│   ├── useChat.ts                      ✅ Conversation history + API calls
│   └── useDocuments.ts                 ✅ Document list + search + filter
├── tailwind.config.ts                  ✅ v4 compatible (tokens in globals.css)
├── next.config.js                      ✅ App Router, security headers
├── .env.local.example                  ✅ NEXT_PUBLIC_API_URL template
└── package.json                        ✅ All deps installed
```

---

## Component Props Interfaces

### Layout
| Component | Key Props |
|-----------|-----------|
| `Sidebar` | `collapsed?: boolean`, `onMouseEnter?`, `onMouseLeave?`, `className?` |
| `AppShell` | `children: ReactNode` |
| `TopBar` | `title?`, `actions?`, `onHamburger?`, `className?` |
| `BottomNav` | `onHamburger: () => void` |
| `MobileDrawer` | `open: boolean`, `onClose: () => void` |

### Chat
| Component | Key Props |
|-----------|-----------|
| `ChatInput` | `onSend: (msg: string) => void`, `loading?`, `disabled?`, `placeholder?` |
| `MessageBubble` | `content: string`, `timestamp: Date`, `error?` |
| `AIResponseBlock` | `message: ChatMessage` |
| `CitationCard` | `citation: Citation`, `className?` |
| `SourcesSection` | `citations: Citation[]` |
| `SuggestedChips` | `chips: string[]`, `onSelect: (chip: string) => void`, `className?` |
| `ConfidenceBadge` | `confidence: 'high' \| 'medium' \| 'low' \| 'none'`, `className?` |
| `LegalContextBadge` | `className?` |
| `ConversationTimestamp` | `date: Date` |

### Upload
| Component | Key Props |
|-----------|-----------|
| `UploadZone` | `onFileSelect: (file: File) => void`, `disabled?` |
| `FilePreview` | `file: File`, `onRemove`, `onUpload`, `loading?` |
| `ProcessingCard` | `filename: string`, `progress: number` |
| `UploadComplete` | `result: DocumentUploadResponse` |

### Documents
| Component | Key Props |
|-----------|-----------|
| `DocumentCard` | `document: StoredDocument` |
| `DocumentGrid` | `documents: StoredDocument[]` |
| `DocumentTypeBadge` | `type: string`, `className?` |
| `DocumentSearchBar` | `value: string`, `onChange: (v: string) => void` |
| `FilterChips` | `filters: readonly string[]`, `active: string`, `onSelect` |

### Settings
| Component | Key Props |
|-----------|-----------|
| `ThemeSelector` | `value: string`, `onChange: (v: string) => void` |
| `TypographySlider` | `value: number`, `onChange: (v: number) => void`, `min?`, `max?` |
| `ToggleRow` | `label: string`, `description?`, `checked: boolean`, `onChange` |

---

## API Integration Points

| Component/Hook | Endpoint | Method |
|----------------|----------|--------|
| `useDocumentUpload` → `lib/api.ts` | `POST /api/documents/upload` | multipart/form-data |
| `useChat` → `lib/api.ts` | `POST /api/chat` | JSON |
| `app/upload/page.tsx` (indirectly) | `GET /api/documents/{id}` | GET (for status polling) |
| No component yet | `GET /health` | GET (exported from api.ts) |

---

## Known Limitations / Backend Additions Needed

| Limitation | Notes |
|------------|-------|
| No `GET /api/documents` list endpoint | Using localStorage as proxy (`lexify_documents` key) |
| `GET /api/documents/{id}` returns mock data | Only used for potential status polling; upload response is sufficient |
| No pagination | Load More button is static (no backend cursor support) |
| No authentication | All routes are publicly accessible |
| No multi-document comparison | Single document per chat session |
| No streaming responses | Backend would need SSE/WebSocket endpoint |
| Session conversations not persisted | Chat messages live in React state only (cleared on refresh) |

---

## Responsive Breakpoint Decisions

| Breakpoint | Behavior |
|------------|----------|
| `< 768px` (mobile) | Sidebar hidden, BottomNav + MobileDrawer, full-width messages |
| `768px–1279px` (tablet) | Sidebar collapses to 64px icon rail, expands to 240px on hover |
| `≥ 1280px` (desktop) | Persistent 268px sidebar, full layout |

---

## Design Deviations from Stitch (with Justifications)

| Deviation | Justification |
|-----------|---------------|
| Tailwind v4 `@theme` CSS variables instead of JS config | Next.js 16 scaffolds with Tailwind v4 which uses CSS-based config; all design tokens implemented as CSS variables with equivalent class mappings |
| RGBA border values use inline styles where CSS classes not available | Tailwind v4 does not support all arbitrary `rgba()` as static classes; inline styles used for opacity-based values (e.g., `rgba(34,197,94,0.18)`) |
| Conversation persistence: localStorage for document registry, React state for messages | No backend conversation storage endpoint available |
| Stitch MCP project unreadable via browser | Design faithfully implemented from the complete written specification in the prompt which documents all tokens and treatments |

---

## localStorage Schema

**Key:** `lexify_documents`

**Value:** JSON array of `StoredDocument` objects:
```typescript
interface StoredDocument {
  document_id: string;   // UUID from backend
  filename: string;      // Original filename
  document_type: string; // e.g., "rental_agreement"
  num_pages: number;     // Page count from backend
  uploaded_at: string;   // ISO 8601 timestamp
}
```

**Operations:**
- `getStoredDocuments()` — reads array from localStorage
- `saveDocument(doc)` — upserts by document_id, prepends new entries
- `clearDocuments()` — removes key entirely (Account Settings)

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | FastAPI backend base URL |

---

## Build Status

```
✓ TypeScript: 0 errors
✓ Routes: 12 (10 static, 2 dynamic)
✓ Build: Exit code 0
✓ Dev server: Running at http://localhost:3000
```
