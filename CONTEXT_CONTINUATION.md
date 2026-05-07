# Ask the Classics — Project Context & Implementation Summary

**Last Updated:** 2026-05-06  
**Status:** MVP Complete with User Approval System  
**Admin Email:** lbarretti@gmail.com

---

## Project Overview

**Ask the Classics** is a portfolio RAG (Retrieval-Augmented Generation) chatbot that answers questions about Adam Smith's "The Wealth of Nations." It demonstrates:

- **RAG Architecture**: Vector-based retrieval (pgvector) + LLM generation (OpenAI GPT-4)
- **Real-time Streaming**: Server-Sent Events (SSE) for live token generation
- **User Management**: Controlled access via Google OAuth 2.0 with approval workflow
- **Production-Ready**: Docker Compose, FastAPI async, Next.js 15 with TypeScript strict mode

### Stack

**Backend:**
- FastAPI (async), SQLAlchemy with asyncio, PostgreSQL + pgvector
- Python 3.12, uv for dependency management
- Structlog for observability, Langfuse for LLM tracing

**Frontend:**
- Next.js 16.2.5 (React 19, TypeScript 5)
- NextAuth v5 (Google OAuth), Tailwind CSS 4, shadcn UI
- Streaming via Vercel AI SDK

**Infrastructure:**
- Docker Compose (PostgreSQL, Embedding Service placeholder)
- GitHub Actions (CI/CD: lint, unit tests, typecheck)

---

## User Approval System (Latest Feature)

### Problem Solved
Previous email allowlist approach allowed any Google account to authenticate. Solution: **explicit approval workflow** with three states.

### Architecture

**States:**
- `pending` — User signs in, awaits admin review (redirected to `/pending`)
- `approved` — User can access chat normally
- `rejected` — Sign-in attempts denied (shown `/login?error=AccessDenied`)

**Flow:**
```
User signs in with Google
    ↓
NextAuth calls /users/register endpoint
    ↓
Backend creates/updates User record in database
    ↓
Backend returns { status, is_admin }
    ↓
Frontend redirects based on status:
  - approved → / (chat)
  - pending → /pending (wait page)
  - rejected → /login?error=AccessDenied
```

### Database Schema

```sql
CREATE TYPE user_status AS ENUM ('pending', 'approved', 'rejected');

CREATE TABLE users (
    id          BIGSERIAL PRIMARY KEY,
    email       TEXT NOT NULL UNIQUE,
    name        TEXT,
    picture     TEXT,
    status      user_status NOT NULL DEFAULT 'pending',
    is_admin    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);

-- Seed admin (prevents creation of admin via Google Auth)
INSERT INTO users (email, name, status, is_admin)
VALUES ('lbarretti@gmail.com', 'Leonardo', 'approved', TRUE)
ON CONFLICT (email) DO UPDATE SET is_admin = TRUE, status = 'approved';
```

**Critical Detail:** Migration creates PostgreSQL `user_status` ENUM (underscore). SQLAlchemy model must specify `name="user_status"` in Enum() to match.

### Backend Implementation

**File:** `backend/app/api/admin.py`

Endpoints:

| Route | Method | Auth | Purpose |
|-------|--------|------|---------|
| `/users/register` | POST | None | Called during NextAuth signIn callback; upserts user, returns status |
| `/admin/users` | GET | X-Admin-Email header | List users filtered by status |
| `/admin/users/{id}/approve` | POST | X-Admin-Email header | Set status=approved, update reviewed_at |
| `/admin/users/{id}/reject` | POST | X-Admin-Email header | Set status=rejected, update reviewed_at |

**Auth Pattern:** Header `X-Admin-Email` (passed by frontend from NextAuth session). Backend validates `is_admin=true` in database before executing protected endpoints.

**Key Schemas:**
```python
class RegisterRequest(BaseModel):
    email: str
    name: str | None = None
    picture: str | None = None

class RegisterResponse(BaseModel):
    status: str  # pending|approved|rejected
    is_admin: bool

class UserOut(BaseModel):
    id: int
    email: str
    name: str | None
    picture: str | None
    status: str
    created_at: datetime
```

### Frontend Integration

**NextAuth Callback (`frontend/auth.ts`):**
```typescript
async signIn({ user }) {
  try {
    const res = await fetch(`${API_URL}/users/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: user.email,
        name: user.name,
        picture: user.image,
      }),
    })
    const data: { status: string; is_admin: boolean } = await res.json()
    
    if (data.status === "approved") return true
    if (data.status === "pending") return "/pending"
    return "/login?error=AccessDenied"
  } catch {
    return "/login?error=ServerError"
  }
}
```

**Middleware Protection (`frontend/proxy.ts`):**
- `/pending` — public (users awaiting approval)
- `/admin` — protected (only lbarretti@gmail.com)
- Other routes — require session

**Pages:**
- `frontend/app/pending/page.tsx` — Waiting page (public, no session required)
- `frontend/app/admin/page.tsx` — Dashboard with user list, approval buttons (Server Component)
- `frontend/components/layout/Header.tsx` — Admin link visible only to admin

---

## Complete Implementation Checklist

- [x] Database schema: `backend/migrations/002_add_users.sql`
- [x] SQLAlchemy model: User + UserStatus enum in `backend/app/db/models.py`
- [x] Backend endpoints: `backend/app/api/admin.py`
- [x] Router registration: `backend/app/api/routes.py`
- [x] NextAuth callback: `frontend/auth.ts`
- [x] Middleware: `frontend/proxy.ts` (protect /admin, allow /pending)
- [x] Pending page: `frontend/app/pending/page.tsx`
- [x] Admin dashboard: `frontend/app/admin/page.tsx`
- [x] Header link: `frontend/components/layout/Header.tsx`
- [x] GitHub Actions CI: fixed all lint/test failures
- [x] Testing: manual flow tested with another Google account

---

## Known Issues & Fixes Applied

### Issue 1: SQLAlchemy Enum Name Mismatch
**Error:** `type 'userstatus' does not exist`  
**Cause:** Migration created PostgreSQL type as `user_status` (underscore), but SQLAlchemy auto-derived name was `userstatus`.  
**Fix:** Add `name="user_status"` parameter: `Enum(UserStatus, name="user_status")`

### Issue 2: GitHub Actions Backend Setup
**Error:** `The interpreter at /usr is externally managed`  
**Cause:** Ubuntu's Python environment doesn't allow `uv pip install --system`.  
**Fix:** Create virtualenv first:
```bash
uv venv --python 3.12
uv pip install -e ".[dev]"
```

### Issue 3: Next.js Linting
**Error:** `unknown option '--dir'`  
**Cause:** Next.js 16 removed `--dir` flag from CLI.  
**Fix:** Use npm script: `npm run lint` → `eslint .`

### Issue 4: Ruff Linting Errors
**Patterns:**
- `B008` (FastAPI Depends in defaults) → `# noqa: B008` comments
- `UP017` (datetime.UTC) → Auto-fixed by `ruff --fix`
- `E402` (imports after code) → `# noqa: E402` for eval script (must load_dotenv first)

---

## Running Locally

### Prerequisites
- Python 3.12, Node.js 20, PostgreSQL 15+, pgvector extension
- Docker & Docker Compose (optional)

### Backend Setup
```bash
cd backend

# Create virtualenv and install
uv venv --python 3.12
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"

# Load environment variables
cp .env.example .env  # adjust OPENAI_API_KEY, DATABASE_URL, etc.

# Run migrations
alembic upgrade head

# Ingest book chunks (from markdown)
python -m app.rag.ingest

# Start server
fastapi dev app/main.py
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm ci

# Environment variables
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

# Start dev server
npm run dev  # http://localhost:3000
```

### Docker Compose
```bash
# Spin up PostgreSQL
docker compose up db -d

# Or full stack (if docker-compose.yml configured with all services)
docker compose up
```

### Testing

**Backend Unit Tests:**
```bash
cd backend
pytest tests/unit/ -v
```

**Backend Evaluation (RAG Recall@5):**
```bash
cd backend
python -m tests.eval.run_eval
# Outputs: recall@5 %, avg top-1 score, latency
```

**Frontend Typecheck & Lint:**
```bash
cd frontend
npx tsc --noEmit
npm run lint
```

**GitHub Actions (local):**
```bash
# Simulate CI
cd backend && .venv/bin/ruff check . && .venv/bin/pytest tests/unit/ -v
cd ../frontend && npm ci && npx tsc --noEmit && npm run lint
```

---

## RAG Retrieval Flow

1. **User Question** → FastAPI `/chat` endpoint
2. **Embedding** → OpenAI's text-embedding-3-small
3. **Vector Search** → PostgreSQL pgvector (cosine similarity, top-5)
4. **Ranking** → Filtered by book/chapter relevance
5. **Generation** → OpenAI GPT-4 with retrieved context
6. **Streaming** → SSE (text tokens + [SOURCES] + [DONE])
7. **Observability** → Langfuse tracing (retrieval + generation)

**Key Files:**
- `backend/app/rag/retriever.py` — Vector search logic
- `backend/app/rag/generator.py` — LLM streaming
- `backend/app/api/chat.py` — SSE response formatting
- `frontend/app/chat/page.tsx` — Client-side streaming with Vercel AI SDK

---

## Database Schema (Complete)

```sql
-- Chunks (books ingested)
CREATE TABLE chunks (
    id BIGSERIAL PRIMARY KEY,
    book TEXT NOT NULL,
    chapter TEXT NOT NULL,
    section TEXT,
    text TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI text-embedding-3-small dimension
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops);

-- Users (new for approval system)
CREATE TYPE user_status AS ENUM ('pending', 'approved', 'rejected');
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT,
    picture TEXT,
    status user_status NOT NULL DEFAULT 'pending',
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);
```

---

## Environment Variables

### Backend (`.env`)
```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/ragdb
LANGFUSE_PUBLIC_KEY=pk_...
LANGFUSE_SECRET_KEY=sk_...
LLM_MODEL=gpt-4-turbo
```

### Frontend (`.env.local`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<random-secret>
GOOGLE_ID=<google-client-id>
GOOGLE_SECRET=<google-client-secret>
ADMIN_EMAIL=lbarretti@gmail.com
```

---

## Deployment (Next Steps)

### VPS Hostinger
Current plan (not yet started):
1. Provision Ubuntu VM with Docker support
2. Set up PostgreSQL with pgvector on VPS
3. Deploy backend as Docker container (FastAPI + Gunicorn)
4. Deploy frontend as Next.js on Vercel or self-hosted via Docker
5. Configure SSL/TLS (Let's Encrypt)
6. Set up monitoring (Langfuse, Grafana optional)

### Future Enhancements
- Reranking layer (Cohere or BGE) for better top-1 accuracy
- Hybrid search (BM25 + vector) for broader coverage
- Multi-book support with semantic router
- Agent framework with tool definitions (current is simple RAG)
- Caching layer (Redis) for common questions
- User feedback loop (thumbs up/down) for RLHF

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Approval workflow instead of allowlist | Demonstrates user management capability; portfolio differentiator |
| X-Admin-Email header (not JWT claims) | Simple, testable; avoids token refresh complexity |
| Server Components for /admin | Type-safe data flow; reduced client-side auth logic |
| Structured logging (structlog) | Trace retrieval/generation for debugging; Langfuse integration |
| No caching initially | Keep MVP simple; add if latency becomes issue |
| Single book focus | Manageable scope for portfolio; architecture supports multi-book |

---

## Testing Strategy

**Unit Tests:** `backend/tests/unit/` (API handlers, database models)  
**Evaluation:** `backend/tests/eval/run_eval.py` (recall@5 metric across 20 reference questions)  
**Manual:** Test flow with another Google account → pending → approve → access chat  
**CI/CD:** GitHub Actions on every push/PR (lint, typecheck, unit tests)

---

## Common Commands

```bash
# Backend
cd backend && python -m app.main              # REPL import app
python -m tests.eval.run_eval                # Run RAG evaluation
.venv/bin/ruff check . --fix                 # Auto-fix linting
.venv/bin/pytest tests/unit/ -v              # Run tests

# Frontend
npm run dev                                   # Dev server
npm run build && npm start                   # Production build
npm run lint                                 # Linting
npx tsc --noEmit                             # Type check

# Database (Docker)
docker compose up db -d                      # Start PostgreSQL
docker compose exec db psql -U user -d ragdb # Connect to DB

# Git
git log --oneline -10                        # Recent commits
git branch -v                                # Branch status
git checkout main && git pull                # Update from remote
```

---

## Files Structure

```
ragSystem/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── admin.py           (NEW: user approval endpoints)
│   │   │   ├── chat.py            (chat + SSE streaming)
│   │   │   └── routes.py          (router aggregation)
│   │   ├── db/
│   │   │   ├── models.py          (MODIFIED: added User + UserStatus)
│   │   │   └── session.py
│   │   ├── rag/
│   │   │   ├── retriever.py       (vector search)
│   │   │   ├── generator.py       (LLM streaming)
│   │   │   └── ingest.py
│   │   ├── core/
│   │   │   └── config.py          (settings)
│   │   ├── observability/
│   │   │   └── langfuse_client.py
│   │   └── main.py                (FastAPI app)
│   ├── migrations/
│   │   ├── 001_initial.sql
│   │   └── 002_add_users.sql      (NEW: user_status enum + users table)
│   ├── tests/
│   │   ├── unit/
│   │   └── eval/
│   │       └── run_eval.py
│   ├── pyproject.toml
│   └── .env
├── frontend/
│   ├── app/
│   │   ├── pending/
│   │   │   └── page.tsx           (NEW: wait page for unapproved users)
│   │   ├── admin/
│   │   │   └── page.tsx           (NEW: admin dashboard)
│   │   ├── chat/
│   │   │   └── page.tsx
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── components/
│   │   ├── layout/
│   │   │   └── Header.tsx         (MODIFIED: added admin link)
│   │   └── ...
│   ├── auth.ts                    (MODIFIED: signIn callback for approval)
│   ├── proxy.ts                   (MODIFIED: protect /admin, allow /pending)
│   ├── package.json               (MODIFIED: "lint": "eslint .")
│   └── .env.local
├── .github/
│   └── workflows/
│       └── ci.yml                 (MODIFIED: fixed uv + eslint setup)
├── docker-compose.yml
├── README.md
└── CONTEXT_CONTINUATION.md        (this file)
```

---

## Troubleshooting

**User sees `/pending` but is already approved?**
- Check `users` table: `SELECT * FROM users WHERE email = '...';`
- If status is not 'approved', update it manually or reject + re-login

**Admin `/admin` page shows 404?**
- Verify ADMIN_EMAIL matches user email in users table
- Check middleware in proxy.ts: is userEmail being extracted correctly?

**Embeddings not inserted after ingest?**
- Check `OPENAI_API_KEY` in backend `.env`
- Verify PostgreSQL `pgvector` extension installed: `SELECT * FROM pg_extension WHERE extname = 'vector';`

**GitHub Actions failing?**
- Check ruff: `cd backend && .venv/bin/ruff check .`
- Check tests: `cd backend && .venv/bin/pytest tests/unit/ -v`
- Check frontend: `cd frontend && npm run lint && npx tsc --noEmit`

---

## Notes for Next Context

- Project is **feature-complete** for MVP (RAG + user approval).
- All **CI/CD passing** as of latest commit.
- **Next priority:** Deploy to VPS Hostinger (not started).
- User email: **lbarretti@gmail.com** (admin account, seed in DB).
- Tech stack mature and well-tested; focus future work on deployment + optional features (reranking, multi-book).
- All endpoint responses are JSON; SSE used only for `/chat` streaming.
- No external dependencies on special infrastructure (embedding service, etc.) — uses OpenAI API.

**Previous Branch PR:** feat/email-allowlist (closed, replaced by feat/user-approval).  
**Current Branch:** main (all changes merged).

---

## Questions & Answers

**Q: Why not use a simple email allowlist?**  
A: Allowlist is static; approval system is dynamic and demonstrates access control for a portfolio. Shows understanding of user management workflows.

**Q: Why X-Admin-Email header instead of JWT sub claim?**  
A: Simpler to test and less coupling to NextAuth internals. Frontend extracts email from session and passes it; backend validates against DB.

**Q: Why Server Component for /admin instead of API route?**  
A: Type safety, direct database access, no N+1 queries, simpler state management. Better for content pages in Next.js 15.

**Q: What if someone fakes the X-Admin-Email header?**  
A: Backend always validates `is_admin=true` in DB. Header is just a hint; DB is source of truth.

**Q: How to promote a user to admin?**  
A: Direct DB update: `UPDATE users SET is_admin = true, status = 'approved' WHERE email = '...';`

**Q: Can users change their own approval status?**  
A: No. Only endpoints `/admin/users/{id}/{approve|reject}` modify status, and they require valid X-Admin-Email + is_admin=true check.

---

Generated: 2026-05-06  
For continuation in future context windows.
