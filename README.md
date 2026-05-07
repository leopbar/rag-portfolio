<div align="center">

# Ask the Classics

### A production-grade RAG chatbot that answers questions about *The Wealth of Nations* (Adam Smith, 1776) — citing exact passages from the book.

[![CI](https://github.com/leopbar/rag-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/leopbar/rag-portfolio/actions/workflows/ci.yml)
&nbsp;
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-RAG-7C3AED)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?logo=openai&logoColor=white)
![Postgres](https://img.shields.io/badge/PostgreSQL-pgvector-336791?logo=postgresql&logoColor=white)
![Langfuse](https://img.shields.io/badge/Langfuse-Observability-F97316)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Deploy](https://img.shields.io/badge/Deploy-Hostinger_VPS-1A56DB)

<br/>

[![LinkedIn](https://img.shields.io/badge/Leonardo_Barretti-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/leonardo-barretti/)
[![Email](https://img.shields.io/badge/lbarretti@gmail.com-EA4335?logo=gmail&logoColor=white)](mailto:lbarretti@gmail.com)
[![Request Access](https://img.shields.io/badge/Request_Demo_Access-28A745?logo=googleforms&logoColor=white)](mailto:lbarretti@gmail.com?subject=Demo%20Access%20Request%20-%20Ask%20the%20Classics)

</div>

---

## What Is This?

**Ask the Classics** is a full-stack AI application that lets you have a real conversation with a 250-year-old economics book.

You ask a question in plain English — the system finds the most relevant passages from *The Wealth of Nations*, sends them to an LLM, and streams back an answer that is **grounded in the actual text**, not invented. Every response shows exactly which Book and Chapter the information came from.

This is a **portfolio project** demonstrating production-level RAG (Retrieval-Augmented Generation) engineering, from ingestion pipeline to observability.

---

## See It In Action

> *A demo GIF will be added here shortly showing the full flow: login → question → streaming response → source citations.*

---

## How It Works — Step by Step

Here is the complete flow from the moment you type a question to the moment you see the answer:

```
You type: "What is the pin factory example?"
              │
              ▼
┌─────────────────────────────┐
│  1. EMBEDDING               │  Your question is converted into
│  OpenAI text-embedding-3    │  a 1536-dimensional vector that
│  small (1536 dimensions)    │  captures its semantic meaning.
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  2. VECTOR SEARCH           │  The system searches 1,168 text
│  PostgreSQL + pgvector      │  chunks from the book using cosine
│  HNSW index, <150ms         │  similarity — finding the 5 most
└──────────────┬──────────────┘  relevant passages.
               │
               ▼
┌─────────────────────────────┐
│  3. CONTEXT ASSEMBLY        │  The 5 chunks are assembled into
│  Ranked by relevance score  │  a structured prompt with their
│  with book/chapter metadata │  metadata: Book I, Chapter I, etc.
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  4. LLM GENERATION          │  GPT-4o-mini receives the context
│  OpenAI gpt-4o-mini         │  and your question, generates an
│  Streaming SSE response     │  answer grounded ONLY in the text.
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  5. STREAMING TO UI         │  Tokens arrive in real time via
│  Next.js + Server-Sent      │  Server-Sent Events. Source cards
│  Events                     │  appear at the end showing the
└─────────────────────────────┘  exact Book and Chapter cited.
```

**The key property:** if the book doesn't contain the answer, the system says so. It does not hallucinate.

---

## Architecture

```
┌────────────────────┐         ┌────────────────────────────────────────┐
│    Next.js 15      │         │            FastAPI Backend              │
│                    │         │                                         │
│  ┌──────────────┐  │         │  ┌─────────────┐   ┌────────────────┐  │
│  │  ChatWindow  │  │◄──SSE──►│  │  Retriever  │   │  LLM Client   │  │
│  │  SourceCard  │  │         │  │ (pgvector)  │   │ (gpt-4o-mini) │  │
│  │  MessageBubble│ │         │  └──────┬──────┘   └───────┬────────┘  │
│  └──────────────┘  │         │         │                  │           │
│                    │         │  ┌──────▼──────────────────▼────────┐  │
│  ┌──────────────┐  │         │  │   PostgreSQL + pgvector           │  │
│  │  NextAuth v5 │  │         │  │   ├─ chunks (1,168 rows, RAG)    │  │
│  │  Google OAuth│  │         │  │   └─ langfuse schema (tracing)   │  │
│  └──────────────┘  │         │  └───────────────────────────────────┘ │
└────────────────────┘         └────────────────────────────────────────┘
                                          Docker Compose — Hostinger VPS
```

---

## Tech Stack

| Layer | Technology | Details |
|---|---|---|
| **Backend** | FastAPI 0.109+ | Native async, SSE streaming, auto OpenAPI docs |
| **RAG Framework** | LlamaIndex + custom chunker | Hierarchical chunking preserving book/chapter structure |
| **Embeddings** | OpenAI `text-embedding-3-small` | 1536 dimensions — $0.02/1M tokens |
| **Vector Store** | PostgreSQL + pgvector | HNSW index, cosine similarity, <150ms retrieval |
| **LLM** | OpenAI `gpt-4o-mini` | Streaming, ~$0.15/1M tokens, high quality |
| **Observability** | Langfuse (self-hosted) | Full trace: chunks used, latency, token cost per query |
| **Frontend** | Next.js 15 + shadcn/ui | App Router, SSE streaming, TypeScript strict mode |
| **Auth** | NextAuth v5 + Google OAuth | No passwords stored — Google manages authentication |
| **Infrastructure** | Docker Compose + Caddy | HTTPS via Let's Encrypt, one-command deployment |
| **CI/CD** | GitHub Actions | Lint (ruff + eslint) + tests on every push |

---

## Key Engineering Decisions

### Hierarchical Chunking
Most RAG tutorials chunk blindly by character count. This project detects the book's structure (BOOK → CHAPTER → SECTION) and attaches metadata to every chunk: `{book: "BOOK I.", chapter: "CHAPTER I.", section: "..."}`.

This makes source citations meaningful — not just a text snippet, but an exact location in the book.

**Chunk size:** 512 tokens with 64-token overlap (using `tiktoken`, the same tokenizer OpenAI uses internally).

### PostgreSQL + pgvector Instead of a Dedicated Vector DB
Pinecone and Weaviate are excellent — but for 1,168 chunks (one book), Postgres + pgvector is the right-sized tool. It shares one Docker container with Langfuse, eliminates a managed service dependency, and demonstrates real SQL skills.

### HNSW Index
```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);
```
HNSW (Hierarchical Navigable Small World) requires no training step, supports incremental inserts, and delivers sub-millisecond search at this scale. Better choice than IVFFlat for datasets under ~1M vectors.

### Server-Sent Events Over WebSocket
SSE is unidirectional (server → client only), which is all token streaming needs. Simpler than WebSocket, works through all proxies and CDNs without configuration, and is natively supported by every modern browser.

### Hallucination Resistance
The LLM prompt explicitly instructs the model to answer only from the provided context. If the retrieved chunks don't contain the answer (e.g., "What does Smith say about Bitcoin?"), the system responds with "The book does not address this topic." It does not invent an answer.

---

## Try the Demo

The application is deployed with Google OAuth, which requires users to be pre-approved before accessing the chat.

**To request demo access:**

1. Send an email to [lbarretti@gmail.com](mailto:lbarretti@gmail.com?subject=Demo%20Access%20Request%20-%20Ask%20the%20Classics) with the subject **"Demo Access Request — Ask the Classics"**
2. Include the **Gmail address** you want to use for login
3. I will approve your account within 24 hours
4. Once approved, visit the app URL and click "Sign in with Google" — no password needed

This approval system exists because the live instance runs on a paid VPS and uses a paid OpenAI API key. Each approved user gets full access to the chat interface.

---

## Running Locally

### Prerequisites
- Docker & Docker Compose
- Python 3.12 + [uv](https://docs.astral.sh/uv/) (modern Python package manager)
- Node.js 20+
- OpenAI API key
- Google OAuth credentials (Client ID + Secret) — [guide here](https://next-auth.js.org/providers/google)

### Step 1 — Clone and configure

```bash
git clone https://github.com/leopbar/rag-portfolio.git
cd rag-portfolio

# Copy the environment template
cp infra/.env.example infra/.env
```

Edit `infra/.env` and fill in:
```env
OPENAI_API_KEY=sk-...
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
NEXTAUTH_SECRET=any_random_32_char_string
```

### Step 2 — Start the database

```bash
docker compose -f infra/docker-compose.yml up db -d
```

This starts PostgreSQL on port 5433 with the pgvector extension enabled.

### Step 3 — Ingest the book

```bash
cd backend

# Install dependencies
uv pip install -e ".[dev]" --system

# Download The Wealth of Nations from Project Gutenberg (free, public domain)
python scripts/download_book.py

# Chunk, embed and store in Postgres (~5 minutes, ~$0.10 in OpenAI API cost)
python -m app.rag.ingest
```

After this step, your database contains 1,168 chunks with embeddings and metadata.

### Step 4 — Start the backend

```bash
# From the backend/ directory
uvicorn app.main:app --reload --port 8000
```

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Step 5 — Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) and sign in with Google.

---

## Evaluation Suite

The project ships with 24 structured test questions measuring retrieval accuracy and hallucination resistance:

```bash
cd backend
python scripts/test_rag_system.py --queries-file ../test_queries.json
```

Test categories:
- **Core Concepts** (C1–C4): Division of labor, invisible hand, natural vs market price
- **Historical Examples** (H1–H3): Pin factory, England-Portugal trade, weavers
- **Philosophical Positions** (P1–P3): Role of government, self-interest, monopolies
- **Hallucination Tests** (HALL1–HALL5): Bitcoin, solar energy, AI — system must refuse
- **Ambiguous Multi-Part** (AMB1–AMB3): Labor & wages, origin of money, guilds
- **Edge Cases** (EDGE1–EDGE3): Gibberish input, single-word query, quote completion

Expected results:
```
Total Queries:  24
Successful:     24 (100%)
Hallucination:  0 fabricated answers
Avg sources:    4.8 per response
```

---

## Project Structure

```
rag-portfolio/
├── backend/                    # FastAPI + RAG pipeline (Python 3.12)
│   ├── app/
│   │   ├── api/                # HTTP endpoints (health, chat)
│   │   ├── core/               # Config (Pydantic Settings), logging
│   │   ├── rag/                # chunker → embedder → retriever → generator
│   │   ├── db/                 # SQLAlchemy models + async session
│   │   └── observability/      # Langfuse tracing integration
│   ├── migrations/             # SQL schema (pgvector, chunks, HNSW index)
│   ├── scripts/                # download_book.py, test_rag_system.py
│   └── tests/                  # Unit, integration, evaluation suites
│
├── frontend/                   # Next.js 15 + TypeScript
│   ├── app/                    # App Router pages (chat, login)
│   ├── components/
│   │   ├── chat/               # ChatWindow, MessageBubble, SourceCard
│   │   └── layout/             # Header with user profile + logout
│   └── hooks/                  # useChat — SSE streaming state management
│
├── infra/
│   ├── docker-compose.yml      # 4 services: db, langfuse, backend, frontend
│   ├── Caddyfile               # Reverse proxy with automatic HTTPS
│   └── .env.example            # Environment variable template
│
└── .github/workflows/
    └── ci.yml                  # Lint (ruff + eslint) + tests on every push
```

---

## What This Project Demonstrates

| Skill | Implementation |
|---|---|
| **RAG Engineering** | Full pipeline: ingestion → chunking → embedding → retrieval → generation |
| **Hallucination Resistance** | Prompt design + retrieval grounding — 0 fabricated answers in eval suite |
| **Vector Search** | pgvector HNSW index, cosine similarity, metadata-enriched chunks |
| **Real-time Streaming** | Server-Sent Events from FastAPI to Next.js, token-by-token delivery |
| **Observability** | Langfuse traces every query: chunks retrieved, latency, token cost |
| **Authentication** | Google OAuth via NextAuth v5 — no passwords, no security risk |
| **Containerization** | Docker Compose with 4 services, production Caddyfile for HTTPS |
| **CI/CD** | GitHub Actions: ruff + eslint + pytest on every push |
| **TypeScript** | Strict mode, typed API client, typed SSE event parsing |

---

## Contact

**Leonardo Barretti**

[![LinkedIn](https://img.shields.io/badge/linkedin.com/in/leonardo--barretti-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/leonardo-barretti/)
[![Email](https://img.shields.io/badge/lbarretti@gmail.com-EA4335?logo=gmail&logoColor=white)](mailto:lbarretti@gmail.com)

---

<div align="center">
<sub>MIT License — Built with FastAPI, Next.js, LlamaIndex, and OpenAI</sub>
</div>
