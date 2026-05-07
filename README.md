# Ask the Classics — RAG Chatbot Portfolio

> A production-grade Retrieval-Augmented Generation (RAG) chatbot that answers questions about **The Wealth of Nations** by Adam Smith (1776), citing exact passages from the book.

[![CI](https://github.com/leopbar/rag-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/leopbar/rag-portfolio/actions/workflows/ci.yml)

---

## What it does

You type a question in natural language. The system:

1. Converts your question into a vector embedding (OpenAI `text-embedding-3-small`)
2. Finds the 5 most relevant passages from the book using cosine similarity (PGVector)
3. Feeds those passages + your question to an LLM (`gpt-4o-mini`)
4. Streams the answer back in real time, with source cards showing **Book** and **Chapter**

Every interaction is traced in Langfuse (latency, tokens, cost per query).

---

## Architecture

```
┌─────────────────┐         ┌──────────────────────────────────────┐
│   Next.js UI    │◄──SSE──►│           FastAPI Backend            │
│  (chat, sources)│         │  ┌────────────┐   ┌───────────────┐  │
└─────────────────┘         │  │ Retriever  │   │  LLM Client   │  │
                            │  │ (pgvector) │   │  (OpenAI)     │  │
                            │  └─────┬──────┘   └──────┬────────┘  │
                            │        │                  │           │
                            │  ┌─────▼──────────────────────────┐  │
                            │  │  Postgres + PGVector            │  │
                            │  │  ├─ chunks table  (RAG)        │  │
                            │  │  └─ langfuse schema (tracing)  │  │
                            │  └────────────────────────────────┘  │
                            └──────────────────────────────────────┘
                                    Docker Compose on VPS
```

---

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| API | FastAPI | Native async, SSE streaming, auto OpenAPI docs |
| RAG | LlamaIndex + custom chunker | Hierarchical chunking with book/chapter metadata |
| Embeddings | OpenAI `text-embedding-3-small` | $0.02/1M tokens, 1536 dims, excellent quality |
| Vector store | PGVector (Postgres extension) | Single DB for both RAG and Langfuse, SQL transparency |
| LLM | OpenAI `gpt-4o-mini` | Fast, cheap (~$0.15/1M tokens), high quality |
| Observability | Langfuse (self-hosted) | Full trace of every query: chunks, latency, cost |
| Frontend | Next.js 15 + shadcn/ui | App Router, SSE streaming, TypeScript strict |
| Infra | Docker Compose + Caddy | HTTPS via Let's Encrypt, single-command deploy |
| CI/CD | GitHub Actions | Lint + unit tests on every push |

---

## Key technical decisions

### Hierarchical chunking
Each text chunk carries metadata `{book, chapter, section}`. This allows the retriever to return not just relevant text, but *where* in the book it comes from — enabling accurate citations.

Chunk size: **512 tokens** with **64-token overlap** (using `tiktoken`, same tokenizer as OpenAI models).

### PGVector over dedicated vector DBs
Pinecone and Weaviate are excellent, but for ~8,000 chunks (one book), Postgres + pgvector is the right tool. It shares the same instance as Langfuse, reduces infrastructure complexity, and demonstrates real SQL skills.

### HNSW index
```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);
```
HNSW (Hierarchical Navigable Small World) outperforms IVFFlat for this volume: no training step, incremental inserts, and sub-millisecond search at 8k vectors.

### SSE over WebSocket
Server-Sent Events are unidirectional (server → client), which is all we need for token streaming. Simpler than WebSocket, works through proxies and CDNs without configuration.

---

## Running locally

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### Setup

```bash
# Clone
git clone https://github.com/leopbar/rag-portfolio.git
cd rag-portfolio

# Configure environment
cp infra/.env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start infrastructure (Postgres + Langfuse)
docker compose -f infra/docker-compose.yml up db langfuse -d

# Install backend dependencies
cd backend && uv pip install -e ".[dev]" --system

# Download the book (one-time)
python scripts/download_book.py

# Ingest into Postgres (one-time, ~5 min, costs ~$0.10 in embeddings)
python -m app.rag.ingest

# Start backend
uvicorn app.main:app --reload

# In another terminal — start frontend
cd frontend && npm install && npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Evaluation

The project ships with a 20-question evaluation suite measuring **retrieval recall@5**:

```bash
cd backend
python -m tests.eval.run_eval
```

Expected output:
```
[✓] Q01 | BOOK I CHAPTER I   | score=0.891 | 142ms
[✓] Q02 | BOOK I CHAPTER IV  | score=0.847 | 138ms
...
──────────────────────────────────────────────────────
Recall@5:        85.0%  (17/20 hits)
Avg top-1 score: 0.8612
Avg latency:     145ms
```

---

## Project structure

```
rag-portfolio/
├── backend/          # FastAPI + RAG pipeline (Python 3.12, uv)
│   ├── app/
│   │   ├── api/          # HTTP layer (health, chat endpoints)
│   │   ├── core/         # Config, logging
│   │   ├── rag/          # Chunker, embedder, retriever, generator
│   │   ├── db/           # SQLAlchemy models, session
│   │   └── observability/ # Langfuse tracing
│   ├── migrations/   # Versioned SQL (pgvector setup)
│   └── tests/        # Unit, integration, eval suites
├── frontend/         # Next.js 15 (TypeScript, Tailwind, shadcn/ui)
│   ├── app/          # App Router pages
│   ├── components/   # ChatWindow, MessageBubble, SourceCard
│   └── hooks/        # useChat (SSE state management)
├── infra/            # Docker Compose, Caddyfile, .env.example
└── .github/
    └── workflows/    # CI (lint + tests), CD (deploy to VPS)
```

---

## License

MIT — see [LICENSE](LICENSE).
