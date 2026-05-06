# Backend — Ask the Classics

FastAPI backend for the RAG pipeline. Handles embeddings, vector search, and LLM generation.

## Stack

- **FastAPI** — async HTTP API
- **LlamaIndex** — RAG orchestration
- **PGVector** — vector store (Postgres extension)
- **OpenAI** — embeddings (`text-embedding-3-small`) + LLM (`gpt-4o-mini`)
- **Langfuse** — observability and tracing

## Running locally

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Copy and fill environment variables
cp ../.env.example .env

# Start the API
uvicorn app.main:app --reload
```

## Project structure

```
app/
├── core/        # Config (env vars) and logging setup
├── api/         # HTTP layer — routes, request/response schemas
├── rag/         # RAG domain logic — chunker, embedder, retriever, generator
├── db/          # Database session and models
└── observability/  # Langfuse tracing client
migrations/      # Versioned SQL files (run once against Postgres)
tests/
├── unit/        # Pure logic tests (no DB, no API calls)
├── integration/ # Tests against a real Postgres instance
└── eval/        # RAG evaluation suite (recall@k, latency)
```

## Running tests

```bash
pytest tests/unit/
pytest tests/integration/   # requires running Postgres
pytest tests/eval/          # requires full stack + ingested data
```
