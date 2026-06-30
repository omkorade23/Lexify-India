# Deployment Readiness Assessment — Lexify India

**Date:** 2026-06-29  
**Assessor:** Deployment planning review (read-only)  
**Repository:** [omkorade23/Lexify-India](https://github.com/omkorade23/Lexify-India)  
**Latest remote commit:** `e8b06d9757170cfbbd68e789ec57511992ff3f0e` — *docs: add github checkpoint report*

---

## Executive Summary

Lexify India is a **functionally complete local application** with a verified frontend production build and a fully wired backend RAG/OCR pipeline. However, the repository is **not ready for production deployment as-is**.

The application code, API contracts, and environment templates are sufficient for local development. What is missing is the **production deployment layer**: platform configuration, production secrets, cross-origin alignment, persistent storage provisioning, and one-time backend initialization (ChromaDB legal knowledge seeding).

**Recommended deployment topology:**

| Component | Platform | Root directory |
|-----------|----------|----------------|
| Next.js frontend | Vercel | `frontend/` |
| FastAPI backend (OCR + RAG + embedded ChromaDB) | Railway | `backend/` |

**Verdict:** **NOT READY FOR DEPLOYMENT**

---

## Repository Assessment

### Layout

The repository is a **monorepo** with two deployable units and extensive project documentation at the root:

```
Lexify-India/
├── backend/          # FastAPI + OCR + RAG + ChromaDB (Python)
├── frontend/         # Next.js 16 App Router (TypeScript)
├── *.md              # PRD, phase reports, completion reports
└── .gitignore        # Secrets, venv, chroma_db, uploads, node_modules
```

| Observation | Why it matters | Status |
|-------------|----------------|--------|
| Monorepo with separate `backend/` and `frontend/` | Each hosting platform must be configured with a **root directory**; default repo-root detection will fail | **Not satisfied** — no platform config files exist |
| No `Dockerfile`, `railway.toml`, `Procfile`, `vercel.json`, or `.github/workflows/` | Platforms cannot infer build/start commands, volumes, or CI without manual dashboard setup or new config files | **Not satisfied** |
| `.gitignore` excludes secrets, `chroma_db/`, `uploads/`, `venv/`, `.next/` | Correct hygiene; production data must be created at runtime on persistent volumes | **Satisfied** (for git) / **Not satisfied** (for runtime persistence) |
| Environment templates exist | `backend/.env.example`, `frontend/.env.local.example` document required variables | **Satisfied** |
| Tracked `document_registry.json` contains dev entries | Production may inherit stale document metadata unless reset | **Partially satisfied** — functional but not clean for prod |
| `legal_knowledge_base.json` tracked (49 entries) | Source data for seeding is in git; **embeddings are not** | **Partially satisfied** |

### Git history (GitHub MCP verified)

| Item | Detail |
|------|--------|
| Remote | `https://github.com/omkorade23/Lexify-India.git` |
| Default branch | `main` |
| Visibility | Public |
| Latest commits | Phase 4 complete (`4418dac`), then checkpoint docs (`e8b06d9`) |
| `.github/` workflows | **None** (path does not exist on remote) |
| Permissions | Admin/push access confirmed via MCP |

---

## Backend Deployment Assessment

### Startup process

| Item | Why it matters | Status |
|------|----------------|--------|
| Entry point | `uvicorn app.main:app` from `backend/` directory | Documented in README and `start_server.bat` |
| Working directory | Relative paths (`data/chroma_db`, `data/uploads`) assume CWD = `backend/` | **Must be enforced** on Railway |
| Lifespan hooks | Create `UPLOAD_DIR` on startup | **Satisfied** in code |
| Legal KB seeding | `scripts/seed_legal_knowledge.py` must run once with valid `GEMINI_API_KEY` | **Not automated** — required before general legal chat works |
| ChromaDB init | Collections created lazily on first use | **Satisfied** in code |
| Production start command | Must bind `0.0.0.0` and use platform `$PORT` | **Not defined** in repo (local uses port 8000) |

**Required before deployment:**
```bash
# From backend/ directory
pip install -r requirements.txt
python scripts/seed_legal_knowledge.py   # one-time, requires GEMINI_API_KEY
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Python runtime

| Item | Why it matters | Status |
|------|----------------|--------|
| Documented requirement | Python 3.11+ (`backend/README.md`) | **Satisfied** (documented) |
| `runtime.txt` / `.python-version` | Railway/Nixpacks use these to pin Python version | **Not present** |
| `requirements.txt` | Lists core dependencies with `>=` pins | **Present** — key packages verified: `fastapi`, `uvicorn`, `paddleocr`, `opencv-python`, `chromadb`, `google-genai`, `pdfplumber` |

### PaddleOCR deployment requirements

| Item | Why it matters | Status |
|------|----------------|--------|
| PaddleOCR lazy-loaded on first OCR request | First upload/OCR call downloads model weights; needs memory and time | **Code satisfied** — ops must size instance accordingly |
| OpenCV (`opencv-python`) | Native wheels usually work on Linux; increases image size | In `requirements.txt` |
| CPU mode (`use_gpu=False`) | Compatible with Railway default compute | **Satisfied** in `ocr_service.py` |
| `pdf2image` in requirements | Listed but **not imported anywhere** in codebase; OCR uses pdfplumber rasterization instead | Dead dependency — low risk but adds install weight |
| Instance sizing | OCR + embedding batches are CPU/memory intensive | **Not configured** — Railway plan must allow ≥2 GB RAM recommended |

**Required before deployment:** Dockerfile or Railway build config that successfully installs PaddleOCR + OpenCV on Linux; smoke-test OCR on deployed instance.

### ChromaDB persistence

| Item | Why it matters | Status |
|------|----------------|--------|
| Embedded `PersistentClient` at `data/chroma_db` | All vectors stored locally on filesystem | **Satisfied** for single-node deployment |
| Gitignored at runtime | Fresh deploy starts with **empty** vector DB | **Not satisfied** for prod without volume + seed |
| Two collections | `document_chunks`, `legal_knowledge` | **Satisfied** in code |
| Railway volume | Required so redeploys do not wipe embeddings and uploads | **Not configured** |

**Required before deployment:**
- Mount Railway volume to `backend/data/` (or at minimum `data/chroma_db` and `data/uploads`)
- Run `seed_legal_knowledge.py` after first deploy (or add startup check)

### Uploaded document persistence

| Item | Why it matters | Status |
|------|----------------|--------|
| Files saved to `data/uploads/{uuid}_{filename}` | Survives only if filesystem persists | **Not satisfied** without volume |
| `document_registry.json` tracks uploads | JSON file on disk; must persist with volume | **Not satisfied** without volume |

### CORS configuration

| Item | Why it matters | Status |
|------|----------------|--------|
| `CORS_ORIGINS` default | `http://localhost:3000,http://localhost:3001,http://localhost:5173` | **Not satisfied** for production |
| Middleware | Reads `settings.cors_origins_list` | **Satisfied** in code |

**Required before deployment:** Set `CORS_ORIGINS` to the exact Vercel production URL (and preview URLs if needed), e.g. `https://lexify-india.vercel.app`.

### API completeness (deployment-relevant)

| Endpoint | Production impact | Status |
|----------|---------------------|--------|
| `POST /api/documents/upload` | Core feature | **Functional** |
| `POST /api/chat` | Core feature | **Functional** |
| `POST /api/legal-chat` | Core feature | **Functional** |
| `GET /health` | Load balancer / monitoring | **Functional** |
| `GET /api/documents/{id}` | Returns mock data | **Not production-ready** — does not block initial deploy but limits document detail pages |

---

## Frontend Deployment Assessment

### Production build (verified locally)

Build executed on 2026-06-29:

```
npm ci && npm run build   →   exit code 0
Next.js 16.2.7 (Turbopack)
✓ Compiled successfully
✓ TypeScript passed
✓ 12 routes generated
```

| Route | Rendering |
|-------|-----------|
| `/`, `/chat`, `/upload`, `/documents`, `/settings/*` | Static |
| `/chat/[documentId]`, `/documents/[id]` | Dynamic (SSR on demand) |

| Item | Why it matters | Status |
|------|----------------|--------|
| `npm run build` succeeds | Vercel build will pass if root directory and env are correct | **Verified satisfied** |
| `npm run start` for production | Standard Next.js production server | **Satisfied** (script exists) |
| No `engines` field in `package.json` | Vercel defaults to supported Node; explicit pin reduces drift | **Not specified** — Node 20 implied by `@types/node` |
| Monorepo root | Vercel must set **Root Directory = `frontend`** | **Not configured** |
| Duplicate config files | Both `next.config.ts` and `next.config.js` exist | **Potential confusion** — only `.ts` is canonical for this project |

### API URL configuration

| Item | Why it matters | Status |
|------|----------------|--------|
| `frontend/lib/api.ts` uses `process.env.NEXT_PUBLIC_API_URL \|\| "http://localhost:8000"` | Client-side fetch target; **baked in at build time** on Vercel | **Not satisfied** for prod until Vercel env var set |
| No hardcoded localhost in components | Confirmed by audit reports and code review | **Satisfied** |
| `NEXT_PUBLIC_` prefix | Required for browser-accessible env vars (Vercel docs) | **Correct pattern** |

**Required before deployment:** Set `NEXT_PUBLIC_API_URL=https://<railway-backend-domain>` in Vercel **Production** environment before first production build.

---

## GitHub Assessment

**MCP status:** Connected and operational.

| Item | Why it matters | Status |
|------|----------------|--------|
| Repository exists and is public | Vercel/Railway can connect via GitHub integration | **Satisfied** |
| `main` branch up to date with Phase 4 work | Deployable source of truth | **Satisfied** (latest push 2026-06-29) |
| No GitHub Actions workflows | No automated build/test/deploy on push | **Not satisfied** for CI/CD (optional for manual deploy) |
| Secrets not in tracked files | `.env` gitignored; `.env.example` has placeholders | **Satisfied** |
| No deployment environments configured in GitHub | GitHub Environments / branch protection not set up | **Not configured** (optional) |

**Conclusion:** GitHub is **ready as a source repository** for platform Git integrations. It is **not configured** for automated deployment pipelines.

---

## Railway Assessment

**MCP status:** **Not connected** (`whoami` and `list-projects` returned `"Not connected"`). Assessment below uses repository inspection and Railway public platform documentation.

| Item | Why it matters | Status |
|------|----------------|--------|
| Existing Railway project | None found via Vercel MCP cross-check; Railway MCP unavailable | **Not created** |
| Service root directory | Must deploy from `backend/`, not repo root | **Must be set manually** |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | **Must be configured** |
| `GEMINI_API_KEY` | Required for embeddings and LLM; empty default in code | **Must be set** in Railway variables |
| `ENVIRONMENT=production` | Enables production mode flag in settings | **Recommended** |
| `CORS_ORIGINS` | Must include Vercel frontend URL | **Must be set** |
| Persistent volumes | Mount to `data/` for ChromaDB + uploads + registry | **Must be provisioned** |
| Public domain | Frontend needs HTTPS backend URL | **Must be generated** |
| Build method | PaddleOCR + OpenCV likely need **Dockerfile** rather than default Nixpacks | **Not present** — high risk of build/runtime failure without Dockerfile |
| Memory/CPU | OCR model load + embedding batches | Recommend ≥2 GB RAM service tier |
| Health check | `/health` endpoint available | **Satisfied** in code — configure in Railway |
| Embedded ChromaDB vs separate service | Current code uses embedded PersistentClient; separate ChromaDB Docker service would require **code changes** | Current architecture: single backend service + volume |

**Railway will require (minimum):**
1. New Railway project linked to `omkorade23/Lexify-India`
2. Backend service with root directory `backend/`
3. Dockerfile (recommended) or custom Nixpacks config for PaddleOCR/OpenCV
4. Volume mounted at `data/`
5. Environment variables (see Environment Variable Assessment)
6. One-time or startup seed: `python scripts/seed_legal_knowledge.py`
7. Public networking enabled for external API access from Vercel

---

## Vercel Assessment

**MCP status:** Connected. Team **"Om Korade's projects"** (`team_NKja2QdqUC8EnLxPd2E9ByqK`). **Zero projects** currently deployed.

| Item | Why it matters | Status |
|------|----------------|--------|
| Vercel project | Must be created and linked to GitHub repo | **Not created** |
| Root directory | Must be `frontend/` (monorepo) | **Not configured** |
| Framework preset | Next.js 16 — auto-detected when root is correct | **Will work** once configured |
| Build command | Default `next build` | **Verified working** |
| Output | Next.js App Router standard output | **Verified working** |
| `NEXT_PUBLIC_API_URL` | Must be set for Production (and Preview if testing PRs) | **Not set** |
| Environment variable timing | `NEXT_PUBLIC_*` vars are inlined at **build time** | Must set before deploy; changing requires rebuild |
| Serverless constraints | Frontend is mostly static/client-side; no Next.js API routes used for backend | **Compatible** with Vercel |
| Backend on Vercel | FastAPI + PaddleOCR + ChromaDB is **not suitable** for Vercel serverless | Correctly excluded — backend goes to Railway |

**Vercel will require (minimum):**
1. Import GitHub repo `omkorade23/Lexify-India`
2. Set Root Directory → `frontend`
3. Add `NEXT_PUBLIC_API_URL` → Railway backend HTTPS URL (Production)
4. Deploy (automatic on push once linked)

---

## Environment Variable Assessment

### Backend (Railway)

| Variable | Required for prod | Current default | Action needed |
|----------|-------------------|-----------------|---------------|
| `GEMINI_API_KEY` | **Yes** | Empty string | Set secret in Railway |
| `CORS_ORIGINS` | **Yes** | localhost only | Set to Vercel production URL(s) |
| `ENVIRONMENT` | Recommended | `development` | Set to `production` |
| `DATABASE_PATH` | Yes | `data/chroma_db` | Keep if volume mounted at `data/` |
| `UPLOAD_DIR` | Yes | `data/uploads` | Keep if volume mounted at `data/` |
| `DOCUMENT_REGISTRY_PATH` | Yes | `data/document_registry.json` | Keep on volume |
| `LEGAL_KNOWLEDGE_PATH` | Yes | `data/legal_knowledge_base.json` | Bundled in repo — OK |
| `EMBEDDING_MODEL` | No change | `gemini-embedding-001` | OK |
| `LLM_MODEL` | No change | `gemini-2.5-flash` | OK |
| `DOCUMENT_SIMILARITY_THRESHOLD` | No change | `0.40` | OK |
| `LEGAL_SIMILARITY_THRESHOLD` | No change | `0.35` | OK |
| `PORT` | Auto | — | Railway injects `$PORT`; uvicorn must use it |

### Frontend (Vercel)

| Variable | Required for prod | Current default | Action needed |
|----------|-------------------|-----------------|---------------|
| `NEXT_PUBLIC_API_URL` | **Yes** | `http://localhost:8000` (fallback) | Set to Railway public HTTPS URL before build |

### Cross-platform alignment checklist

1. Deploy Railway backend first → obtain public URL
2. Set Railway `CORS_ORIGINS` to Vercel URL
3. Set Vercel `NEXT_PUBLIC_API_URL` to Railway URL
4. Redeploy frontend if backend URL changes

---

## Deployment Requirements

### Pre-deployment (must complete)

| # | Requirement | Owner |
|---|-------------|-------|
| 1 | Create Railway project; configure backend service from `backend/` | Platform setup |
| 2 | Add Dockerfile or proven build config for PaddleOCR + OpenCV on Linux | Platform setup |
| 3 | Provision Railway volume for `data/` (ChromaDB + uploads + registry) | Platform setup |
| 4 | Set Railway secrets: `GEMINI_API_KEY`, `CORS_ORIGINS`, `ENVIRONMENT=production` | Platform setup |
| 5 | Configure Railway start command using `$PORT` | Platform setup |
| 6 | Run `seed_legal_knowledge.py` on production backend (one-time) | Ops |
| 7 | Generate Railway public domain; verify `GET /health` | Ops |
| 8 | Create Vercel project; root directory `frontend/` | Platform setup |
| 9 | Set Vercel `NEXT_PUBLIC_API_URL` to Railway URL | Platform setup |
| 10 | Deploy frontend; verify browser can call backend (no CORS errors) | Ops |
| 11 | End-to-end smoke test: general chat, upload, document chat | Ops |

### Post-deployment (functional but degraded without)

| # | Requirement | Impact if skipped |
|---|-------------|-------------------|
| 1 | Document list API (`GET /api/documents`) | Document library relies on localStorage only |
| 2 | Real `GET /api/documents/{id}` | Document detail page may show incorrect metadata |
| 3 | Auth layer | All routes publicly accessible |
| 4 | Conversation persistence | Chat history lost on refresh |

---

## Critical Blockers

These items **would realistically prevent a successful production deployment** if not addressed:

| # | Blocker | Why critical |
|---|---------|--------------|
| 1 | **No production environment variables configured** | Backend cannot call Gemini; frontend calls localhost |
| 2 | **CORS restricted to localhost** | Browser requests from Vercel frontend will be blocked |
| 3 | **No deployment/platform configuration** | No Dockerfile, Railway service config, or Vercel root directory — platforms cannot deploy correctly from monorepo without manual setup |
| 4 | **No persistent storage on Railway** | ChromaDB embeddings, uploads, and registry wiped on every redeploy |
| 5 | **Legal knowledge not seeded on fresh ChromaDB** | `/api/legal-chat` and legal context in document chat return empty/fallback until `seed_legal_knowledge.py` runs |
| 6 | **No Railway or Vercel projects exist** | Nothing is linked or deployed yet |
| 7 | **Backend production start command not defined** | Railway needs explicit uvicorn command bound to `$PORT` |
| 8 | **Heavy OCR dependencies unvalidated on target platform** | PaddleOCR + OpenCV may fail default Railway Nixpacks build without Dockerfile |

---

## Recommended Improvements

These do not necessarily block a **minimal** production launch but should be addressed early:

| # | Improvement | Rationale |
|---|-------------|-----------|
| 1 | Add `Dockerfile` in `backend/` | Reliable PaddleOCR/OpenCV install on Railway |
| 2 | Add `railway.toml` or documented Railway settings | Reproducible backend deploys |
| 3 | Add startup script that seeds legal KB if collection is empty | Avoids manual one-time ops step |
| 4 | Pin Python version (`runtime.txt`) and Node `engines` | Reproducible builds across platforms |
| 5 | Add `GET /api/documents` and wire frontend off localStorage | Cross-device document library |
| 6 | Fix `GET /api/documents/{id}` to read registry | Accurate document detail pages |
| 7 | GitHub Actions CI (lint + frontend build) | Catch regressions before deploy |
| 8 | Health check extension (verify ChromaDB + Gemini connectivity) | Better monitoring |
| 9 | Remove unused `pdf2image` from requirements | Smaller install footprint |
| 10 | Connect Railway MCP for operational visibility | Currently unavailable in this session |

---

## Optional Enhancements

| # | Enhancement | Notes |
|---|-------------|-------|
| 1 | JWT/OAuth authentication | Listed as Phase 4C+ in project state |
| 2 | Conversation persistence API | Session history across refreshes |
| 3 | Separate ChromaDB Railway service | Would require refactoring from embedded PersistentClient |
| 4 | Custom domain + HTTPS on both platforms | Branding |
| 5 | Preview environment CORS entries | For Vercel preview deployments |
| 6 | Rate limiting / API key for backend | Abuse prevention on public endpoints |
| 7 | GitHub Environments with required reviewers | Safer production promotions |

---

## Final Deployment Verdict

# NOT READY FOR DEPLOYMENT

The Lexify India **application is development-complete and locally verified**, including a successful frontend production build (12 routes, exit code 0) and a functional backend API design. The **repository itself lacks the production deployment configuration** required to run on Railway and Vercel.

Deployment can proceed once the **eight critical blockers** above are resolved through platform setup (not application code changes). The most efficient path is:

1. **Railway:** backend service from `backend/` + volume + secrets + seed script + public domain  
2. **Vercel:** frontend from `frontend/` + `NEXT_PUBLIC_API_URL` pointing to Railway  
3. **Align CORS** on backend with Vercel URL  
4. **Smoke test** all three chat flows end-to-end  

No deployments, code changes, or commits were made during this assessment.

---

## MCP Tools Used

| MCP | Status | Usage |
|-----|--------|-------|
| GitHub | Connected | Repository search, root contents, commits, `.env.example` verification |
| Vercel | Connected | Team listing, project listing (0 projects), documentation search |
| Railway | **Not connected** | Could not inspect projects or account; assessment based on repo + public Railway docs |
