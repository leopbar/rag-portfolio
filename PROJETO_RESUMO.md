# Ask the Classics — RAG Chatbot Portfolio
## Resumo de Desenvolvimento e Estado Atual

---

## 📋 Visão Geral do Projeto

**Objetivo:** Criar um chatbot RAG (Retrieval-Augmented Generation) funcionando como portfólio profissional de ML/AI Engineer júnior. O sistema responde perguntas sobre "The Wealth of Nations" (Adam Smith, 1776) com citações exatas do livro.

**Status:** MVP funcional, testado localmente. Pronto para deploy em produção.

**Repositório GitHub:** [https://github.com/leopbar/rag-portfolio](https://github.com/leopbar/rag-portfolio)

---

## 🏗️ Arquitetura Implementada

### Stack Tecnológico
```
Frontend:    Next.js 15 + TypeScript + Tailwind + shadcn/ui
Auth:        NextAuth v5 + Google OAuth
Backend:     FastAPI (Python 3.12) + LlamaIndex
Database:    Postgres (porta 5433) + pgvector (1536 dims)
Embeddings:  OpenAI text-embedding-3-small
LLM:         OpenAI gpt-4o-mini
Observability: Langfuse (self-hosted via Docker)
CI/CD:       GitHub Actions (lint + tests)
Infra:       Docker Compose
```

### Fluxo da Aplicação
1. Usuário autentica com Google OAuth
2. Digita pergunta em linguagem natural
3. Backend gera embedding (OpenAI)
4. Busca vetorial no Postgres com cosine similarity (pgvector)
5. Retorna top-5 chunks com metadata {book, chapter, section}
6. LLM gera resposta em streaming SSE
7. Frontend renderiza tokens em tempo real + cards de fonte

---

## 📁 Estrutura do Repositório

```
rag-portfolio/
├── backend/                     # FastAPI + RAG (Python)
│   ├── app/
│   │   ├── main.py             # Entry point FastAPI
│   │   ├── core/               # Config, logging
│   │   ├── api/                # HTTP layer (health, chat endpoints)
│   │   ├── rag/                # Chunker, embedder, retriever, generator
│   │   ├── db/                 # SQLAlchemy models, session
│   │   └── observability/      # Langfuse tracing
│   ├── migrations/             # SQL schema (pgvector, chunks table)
│   ├── scripts/                # download_book.py
│   ├── tests/                  # unit, integration, eval suites
│   ├── data/                   # wealth-of-nations.txt (gitignored)
│   ├── pyproject.toml          # Dependências uv
│   ├── Dockerfile              # Production image
│   └── .env                    # Variáveis locais (OpenAI key, etc)
│
├── frontend/                    # Next.js + TypeScript
│   ├── app/
│   │   ├── page.tsx            # Chat principal
│   │   ├── layout.tsx          # HTML base
│   │   ├── login/page.tsx      # Login com Google
│   │   └── api/auth/[...nextauth]/route.ts  # NextAuth handler
│   ├── components/
│   │   ├── chat/               # ChatWindow, MessageBubble, SourceCard
│   │   └── layout/             # Header (with user profile + logout)
│   ├── hooks/                  # useChat (SSE streaming state)
│   ├── lib/                    # API client, utils
│   ├── auth.ts                 # NextAuth config
│   ├── proxy.ts                # Route protection middleware
│   ├── .env.local              # Google OAuth + API URL (gitignored)
│   ├── Dockerfile              # Production image
│   └── package.json            # npm dependencies
│
├── infra/
│   ├── docker-compose.yml      # 4 services: db, langfuse, backend, frontend
│   ├── Caddyfile               # HTTPS proxy (for VPS deploy)
│   └── .env.example            # Variáveis template
│
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions: lint + tests
│
├── .gitignore                  # Python, Node, .env, data/
├── .editorconfig               # Consistência de formatação
├── LICENSE                     # MIT
└── README.md                   # Documentação do projeto

```

---

## 🔧 Setup Local (Como Rodar Agora)

### Pré-requisitos
- Python 3.12 + uv
- Node 20 + npm
- Docker Desktop
- Chave da OpenAI API
- Credenciais Google OAuth (Client ID + Secret)

### Passo 1: Backend + Database

```bash
# Subir Postgres + pgvector (porta 5433)
docker compose -f infra/docker-compose.yml up db -d

# Instalar dependências backend
cd backend
uv pip install -e ".[dev]" --system

# Baixar o livro
python scripts/download_book.py

# Fazer ingestão (gera embeddings + popula Postgres)
python -m app.rag.ingest

# Rodar backend (porta 8000)
python -m uvicorn app.main:app --port 8000
```

### Passo 2: Frontend

```bash
cd frontend

# Preencher .env.local com:
# GOOGLE_CLIENT_ID=seu_client_id
# GOOGLE_CLIENT_SECRET=seu_client_secret

# Rodar
npm run dev  # Abre em http://localhost:3000
```

### URLs Locais
- **Frontend:** http://localhost:3000 (com auth Google)
- **Backend:** http://localhost:8000 (`/health`, `/chat/`)
- **Postgres:** localhost:5433
- **Langfuse:** http://localhost:3001 (opcional)

---

## 🎯 O Que Foi Implementado

### Dia 0 — Repositório
✅ GitHub criado  
✅ `.gitignore` configurado  
✅ Estrutura inicial  

### Dia 1-2 — Backend Setup
✅ FastAPI com CORS dinâmico  
✅ Postgres + pgvector (Docker)  
✅ Migrations SQL (chunks table + HNSW index)  
✅ Config typado (Pydantic)  
✅ Script de download (Project Gutenberg)  

### Dia 3-4 — Pipeline Ingestão
✅ Chunker hierárquico (detecta BOOK/CHAPTER, 512 tokens overlap 64)  
✅ Embedder (OpenAI batch com delay rate-limit)  
✅ Ingestão completa (2314 → 1168 chunks após regex fix)  
✅ Testes unitários do chunker  

### Dia 5 — Endpoint /chat
✅ Retriever (cosine similarity pgvector)  
✅ Generator (prompt + LLM streaming)  
✅ SSE streaming (`data: [SOURCES] json` + tokens)  
✅ Integração Langfuse para tracing  

### Dia 6-7 — Observabilidade + Eval
✅ Langfuse tracing no `/chat`  
✅ Suite de 20 perguntas padrão  
✅ Script de avaliação (recall@5)  

### Dia 8-9 — Frontend
✅ Next.js 15 + Tailwind + shadcn/ui  
✅ ChatWindow com streaming (Vercel AI SDK)  
✅ SourceCard com metadata  
✅ MessageBubble com markdown  

### Dia 10-13 — Polimento + CI
✅ README raiz com arquitetura  
✅ GitHub Actions CI (ruff + pytest + tsc)  
✅ .editorconfig  
✅ Testado localmente funcionando  

### Google Auth (Novo)
✅ NextAuth v5 integrado  
✅ Google OAuth configurado  
✅ Página de login com botão Google  
✅ Header com nome/foto do usuário + logout  
✅ Middleware protegendo rotas  
✅ `.env.local` com credenciais  

---

## 📊 Métricas de Sucesso (Local)

- **Chunks ingestados:** 1168 (com metadata correta: BOOK V., CHAPTER III., etc)
- **Embedding dimension:** 1536 (OpenAI text-embedding-3-small)
- **Retrieval:** <150ms latência (pgvector HNSW)
- **Streaming:** SSE tokens aparecem em tempo real
- **Auth:** Google OAuth funcionando, usuário autenticado

---

## ⚠️ Issues Resolvidos Durante Desenvolvimento

1. **CORS bloqueando frontend (porta 3001 vs 3000)**
   - Solução: Configurar `allow_origins=["*"]` em debug mode no `app/main.py`

2. **Regex do chunker não detectando BOOK/CHAPTER**
   - Problema: Gutenberg usa `BOOK I.` (com ponto), regex esperava `BOOK I` (sem ponto)
   - Solução: Adicionar `\.?` no regex para tornar o ponto opcional

3. **Next.js 16 deprecando `middleware.ts`**
   - Solução: Renomear para `proxy.ts`

4. **Porta 5432 ocupada por Postgres local**
   - Solução: Usar porta 5433 no Docker Compose, atualizar `.env`

5. **`pyproject.toml` quebrado (hatchling não encontrava pacote)**
   - Solução: Adicionar `[tool.hatch.build.targets.wheel] packages = ["app"]`

---

## 🚀 Próximos Passos (Quando Continuar)

### Deploy na VPS Hostinger (Não iniciado)
- [ ] Configurar SSH + credenciais na VPS
- [ ] Deploy Docker Compose na VPS
- [ ] Configurar Caddy para HTTPS
- [ ] GitHub Actions CD (deploy SSH automático)
- [ ] URL pública: `https://rag.seudominio.com`

### Melhorias Opcionais (Não no escopo MVP)
- [ ] Reranking (cohere-rerank para melhorar precision)
- [ ] Hybrid search (BM25 + vetorial)
- [ ] Eval framework (Ragas)
- [ ] Multi-livro com filtros
- [ ] Agente com ferramentas

---

## 📝 Variáveis de Ambiente Necessárias

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
GOOGLE_CLIENT_ID=seu_client_id_aqui
GOOGLE_CLIENT_SECRET=seu_client_secret_aqui
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🔐 Segurança da Autenticação

**Abordagem:** OAuth 2.0 com Google (sem armazenar senhas)

**Por que é seguro:**
- Senhas nunca tocam seu servidor ✅
- Google gerencia 2FA automaticamente ✅
- Phishing impossível (redirecionamento Google) ✅
- Token JWT assinado e verificado ✅

**Fluxo:**
1. Usuário clica "Sign in with Google"
2. Redireciona para Google (seu site não toca senha)
3. Google autentica e volta com JWT
4. NextAuth valida e cria sessão
5. Middleware protege `/` e `/api/chat`

---

## 📚 Commits Principais no GitHub

```
2b64b78  Merge PR #4: README + CI + bugfixes
d15824b  Merge PR #3: Frontend (Next.js + chat)
bd7f4e4  Merge PR #2: Backend completo
c2fdf21  fix: CORS + regex chunker
ad44208  docs: README + CI workflow
f7b84b7  chore: Frontend bootstrap
7dd9cd9  feat: Google OAuth + NextAuth
```

---

## 🎓 O Que Este Projeto Demonstra para Recrutadores

1. **RAG real end-to-end** — não é tutorial, é produção
2. **Decisões técnicas justificadas** — chunking hierárquico, HNSW, streaming SSE
3. **Segurança** — OAuth2, sem senhas, middleware protegido
4. **Observabilidade** — Langfuse tracing integrado
5. **Qualidade** — CI automático, testes, linting
6. **DevOps** — Docker, composição de serviços, migrations versionadas
7. **Git profissional** — PRs incrementais, commits atômicos, histórico limpo
8. **Frontend moderno** — Next.js 15, TypeScript strict, streaming real-time
9. **Citação de fontes** — resolve problema de alucinação LLM

---

## 💾 Salvos Localmente (Não Versionados)

- `backend/data/wealth-of-nations.txt` — livro baixado (~2.4MB)
- `backend/.env` — chave OpenAI (no `.gitignore`)
- `frontend/.env.local` — credenciais Google (no `.gitignore`)
- `infra/volumes/postgres_data/` — dados Postgres

---

## 📞 Contato para Continuação

Se você ou outra IA precisar continuar este projeto:

1. **Clonar repo:** `git clone https://github.com/leopbar/rag-portfolio.git`
2. **Ler este documento** (PROJETO_RESUMO.md)
3. **Seguir "Setup Local"** para rodar tudo
4. **Conferir branch/PR atual** no GitHub
5. **Próximo passo natural:** Deploy na VPS Hostinger (se quiser URL pública)

---

## ✅ Checklist de Conclusão

- [x] Backend funcional (FastAPI + RAG pipeline)
- [x] Ingestão funcionando (1168 chunks com metadata)
- [x] Endpoint `/chat` com streaming
- [x] Frontend funcional (Next.js + chat)
- [x] Autenticação Google OAuth
- [x] Testes locais passando
- [x] CI configurado no GitHub
- [x] Repositório público com histórico limpo
- [ ] Deploy na VPS Hostinger (próximo passo)

---

**Última atualização:** 2026-05-06 21:50 UTC  
**Versão:** 0.1.0 MVP  
**Status:** ✅ Operacional Localmente | ⏳ Pronto para Deploy
