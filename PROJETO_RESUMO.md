# Ask the Classics — RAG Chatbot Portfolio
## Development Summary and Current Status

---

## Project Overview

**Objective:** Build a RAG (Retrieval-Augmented Generation) chatbot serving as a junior ML/AI Engineer portfolio project. The system answers questions about "The Wealth of Nations" (Adam Smith, 1776) with exact citations from the book.

**Status:** Functional MVP, locally tested. Ready for production deployment.

**GitHub Repository:** [https://github.com/leopbar/rag-portfolio](https://github.com/leopbar/rag-portfolio)

---

## Implemented Architecture

### Tech Stack
```
Frontend:    Next.js 15 + TypeScript + Tailwind + shadcn/ui
Auth:        NextAuth v5 + Google OAuth
Backend:     FastAPI (Python 3.12) + LlamaIndex
Database:    Postgres (port 5433) + pgvector (1536 dims)
Embeddings:  OpenAI text-embedding-3-small
LLM:         OpenAI gpt-4o-mini
Observability: Langfuse (self-hosted via Docker)
CI/CD:       GitHub Actions (lint + tests)
Infrastructure: Docker Compose
```

### Application Flow
1. User authenticates via Google OAuth
2. Types question in natural language
3. Backend generates embedding (OpenAI)
4. Vector search in Postgres with cosine similarity (pgvector)
5. Returns top-5 chunks with metadata {book, chapter, section}
6. LLM generates response in streaming SSE
7. Frontend renders tokens in real-time + source cards

---

## Repository Structure

```
rag-portfolio/
├── backend/                     # FastAPI + RAG (Python)
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── core/               # Config, logging
│   │   ├── api/                # HTTP layer (health, chat endpoints)
│   │   ├── rag/                # Chunker, embedder, retriever, generator
│   │   ├── db/                 # SQLAlchemy models, session
│   │   └── observability/      # Langfuse tracing
│   ├── migrations/             # SQL schema (pgvector, chunks table)
│   ├── scripts/                # download_book.py
│   ├── tests/                  # unit, integration, eval suites
│   ├── data/                   # wealth-of-nations.txt (gitignored)
│   ├── pyproject.toml          # uv dependencies
│   ├── Dockerfile              # Production image
│   └── .env                    # Local environment variables
│
├── frontend/                    # Next.js + TypeScript
│   ├── app/
│   │   ├── page.tsx            # Main chat page
│   │   ├── layout.tsx          # HTML base
│   │   ├── login/page.tsx      # Google login page
│   │   └── api/auth/[...nextauth]/route.ts  # NextAuth handler
│   ├── components/
│   │   ├── chat/               # ChatWindow, MessageBubble, SourceCard
│   │   └── layout/             # Header (user profile + logout)
│   ├── hooks/                  # useChat (SSE streaming state)
│   ├── lib/                    # API client, utilities
│   ├── auth.ts                 # NextAuth configuration
│   ├── proxy.ts                # Route protection middleware
│   ├── .env.local              # Google OAuth + API URL (gitignored)
│   ├── Dockerfile              # Production image
│   └── package.json            # npm dependencies
│
├── infra/
│   ├── docker-compose.yml      # 4 services: db, langfuse, backend, frontend
│   ├── Caddyfile               # HTTPS proxy (for VPS deploy)
│   └── .env.example            # Environment variables template
│
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions: lint + tests
│
├── .gitignore                  # Python, Node, .env, data/
├── .editorconfig               # Formatting consistency
├── LICENSE                     # MIT
└── README.md                   # Project documentation

```

---

## Local Setup (How to Run)

### Prerequisites
- Python 3.12 + uv
- Node 20 + npm
- Docker Desktop
- OpenAI API key
- Google OAuth credentials (Client ID + Secret)

### Step 1: Backend + Database

```bash
# Start Postgres + pgvector (port 5433)
docker compose -f infra/docker-compose.yml up db -d

# Install backend dependencies
cd backend
uv pip install -e ".[dev]" --system

# Download the book
python scripts/download_book.py

# Run ingestion (generates embeddings + populates Postgres)
python -m app.rag.ingest

# Start backend (port 8000)
python -m uvicorn app.main:app --port 8000
```

### Step 2: Frontend

```bash
cd frontend

# Fill .env.local with:
# GOOGLE_CLIENT_ID=your_client_id
# GOOGLE_CLIENT_SECRET=your_client_secret

# Run
npm run dev  # Opens at http://localhost:3000
```

### Local URLs
- **Frontend:** http://localhost:3000 (with Google auth)
- **Backend:** http://localhost:8000 (`/health`, `/chat/`)
- **Postgres:** localhost:5433
- **Langfuse:** http://localhost:3001 (optional)

---

## What Was Implemented

### Day 0 — Repository
- GitHub created
- `.gitignore` configured
- Initial structure

### Day 1-2 — Backend Setup
- FastAPI with dynamic CORS
- Postgres + pgvector (Docker)
- SQL migrations (chunks table + HNSW index)
- Typed config (Pydantic)
- Download script (Project Gutenberg)

### Day 3-4 — Ingestion Pipeline
- Hierarchical chunker (detects BOOK/CHAPTER, 512 tokens overlap 64)
- Embedder (OpenAI batch with rate-limit delay)
- Complete ingestion (2314 → 1168 chunks after regex fix)
- Chunker unit tests

### Day 5 — /chat Endpoint
- Retriever (cosine similarity pgvector)
- Generator (prompt + LLM streaming)
- SSE streaming (`data: [SOURCES] json` + tokens)
- Langfuse tracing integration

### Day 6-7 — Observability + Eval
- Langfuse tracing in `/chat`
- Suite of 20 standard questions
- Evaluation script (recall@5)

### Day 8-9 — Frontend
- Next.js 15 + Tailwind + shadcn/ui
- ChatWindow with streaming (Vercel AI SDK)
- SourceCard with metadata
- MessageBubble with markdown

### Day 10-13 — Polish + CI
- Root README with architecture
- GitHub Actions CI (ruff + pytest + tsc)
- .editorconfig
- Locally tested and working

### Google Auth (Added)
- NextAuth v5 integrated
- Google OAuth configured
- Login page with Google button
- Header with user name/photo + logout
- Middleware protecting routes
- `.env.local` with credentials

---

## Success Metrics (Local)

- **Chunks ingested:** 1168 (with correct metadata: BOOK V., CHAPTER III., etc)
- **Embedding dimension:** 1536 (OpenAI text-embedding-3-small)
- **Retrieval:** <150ms latency (pgvector HNSW)
- **Streaming:** SSE tokens appear in real-time
- **Auth:** Google OAuth working, user authenticated

---

## Issues Resolved During Development

1. **CORS blocking frontend (port 3001 vs 3000)**
   - Solution: Configure `allow_origins=["*"]` in debug mode in `app/main.py`

2. **Chunker regex not detecting BOOK/CHAPTER**
   - Problem: Gutenberg uses `BOOK I.` (with period), regex expected `BOOK I` (no period)
   - Solution: Add `\.?` in regex to make period optional

3. **Next.js 16 deprecating `middleware.ts`**
   - Solution: Rename to `proxy.ts`

4. **Port 5432 occupied by local Postgres**
   - Solution: Use port 5433 in Docker Compose, update `.env`

5. **`pyproject.toml` broken (hatchling couldn't find package)**
   - Solution: Add `[tool.hatch.build.targets.wheel] packages = ["app"]`

---

## Next Steps (When Continuing)

### VPS Hostinger Deployment (Not started)
- [ ] Configure SSH + credentials on VPS
- [ ] Deploy Docker Compose on VPS
- [ ] Configure Caddy for HTTPS
- [ ] GitHub Actions CD (automatic SSH deployment)
- [ ] Public URL: `https://rag.yourdomain.com`

### Optional Improvements (Out of MVP scope)
- [ ] Reranking (cohere-rerank for better precision)
- [ ] Hybrid search (BM25 + vector)
- [ ] Eval framework (Ragas)
- [ ] Multi-book with filters
- [ ] Agent with tools

---

## Required Environment Variables

### Backend (`backend/.env`)
```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/ragdb
DEBUG=true
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=http://localhost:3001
```

### Frontend (`frontend/.env.local`)
```
NEXTAUTH_SECRET=91oRssoy7A14kbqS/sHG7UM4/1DTFPUBwcofzwuvAck=
NEXTAUTH_URL=http://localhost:3000
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Authentication Security

**Approach:** OAuth 2.0 with Google (no passwords stored)

**Why it's secure:**
- Passwords never touch your server
- Google manages 2FA automatically
- Phishing impossible (Google redirect)
- Signed and verified JWT token

**Flow:**
1. User clicks "Sign in with Google"
2. Redirects to Google (your site never sees password)
3. Google authenticates and returns JWT
4. NextAuth validates and creates session
5. Middleware protects `/` and `/api/chat`

---

## Main Commits on GitHub

```
2b64b78  Merge PR #4: README + CI + bugfixes
d15824b  Merge PR #3: Frontend (Next.js + chat)
bd7f4e4  Merge PR #2: Backend complete
c2fdf21  fix: CORS + regex chunker
ad44208  docs: README + CI workflow
f7b84b7  chore: Frontend bootstrap
7dd9cd9  feat: Google OAuth + NextAuth
```

---

## What This Project Demonstrates to Recruiters

1. **Real end-to-end RAG** — not a tutorial, production-grade
2. **Justified technical decisions** — hierarchical chunking, HNSW, streaming SSE
3. **Security** — OAuth2, no passwords, protected middleware
4. **Observability** — Langfuse tracing integrated
5. **Quality** — automatic CI, tests, linting
6. **DevOps** — Docker, service composition, versioned migrations
7. **Professional git** — incremental PRs, atomic commits, clean history
8. **Modern frontend** — Next.js 15, TypeScript strict, real-time streaming
9. **Source citation** — solves LLM hallucination problem

---

## Saved Locally (Not Versioned)

- `backend/data/wealth-of-nations.txt` — downloaded book (~2.4MB)
- `backend/.env` — OpenAI key (in `.gitignore`)
- `frontend/.env.local` — Google credentials (in `.gitignore`)
- `infra/volumes/postgres_data/` — Postgres data

---

## Contact for Continuation

If you or another AI need to continue this project:

1. **Clone repo:** `git clone https://github.com/leopbar/rag-portfolio.git`
2. **Read this document** (PROJETO_RESUMO.md)
3. **Follow "Local Setup"** to run everything
4. **Check current branch/PR** on GitHub
5. **Next natural step:** VPS Hostinger deployment (for public URL)

---

## Completion Checklist

- [x] Functional backend (FastAPI + RAG pipeline)
- [x] Working ingestion (1168 chunks with metadata)
- [x] `/chat` endpoint with streaming
- [x] Functional frontend (Next.js + chat)
- [x] Google OAuth authentication
- [x] Local tests passing
- [x] CI configured on GitHub
- [x] Public repo with clean history
- [ ] VPS Hostinger deployment (next step)

---

**Last Updated:** 2026-05-07  
**Version:** 0.1.0 MVP  
**Status:** Fully Operational Locally | Ready for Deployment
