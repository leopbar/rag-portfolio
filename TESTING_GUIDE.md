# RAG System Testing Guide

## Objective

Validate that the RAG system:
1. **Retrieves correctly** — finds relevant chunks from the book
2. **Responds accurately** — generates responses based on real sources
3. **Rejects hallucinations** — does NOT invent information about topics outside the book
4. **Cites sources** — provides exact metadata (book, chapter, section)

---

## How to Test

### Method 1: Manual via UI (Fastest)

1. Make sure the system is running:
   ```bash
   # Terminal 1: Backend
   cd backend
   python -m uvicorn app.main:app --port 8000

   # Terminal 2: Frontend
   cd frontend
   npm run dev

   # Terminal 3: Database (if not running)
   docker compose -f infra/docker-compose.yml up db -d
   ```

2. Open http://localhost:3000
3. Sign in with Google (or admin account)
4. Copy a question from `test_queries.json`
5. Paste in the UI and evaluate:
   - Is the response relevant?
   - Are there source citations?
   - Do the citations make sense?

**Example of a good response:**
```
Question: "What is the division of labor?"

Response: Adam Smith argues that the division of labor is
fundamental to increasing productivity. He exemplifies this
with the pin factory...

[Source: The Wealth of Nations, Book I, Chapter I]
[Citation: "The great improvement in the productive powers..."]
```

**Example of hallucination:**
```
Question: "What does Smith say about Bitcoin?"

BAD response: "Smith believed that Bitcoin would..."
GOOD response: "The book does not mention Bitcoin or digital currencies."
```

### Method 2: Automated via Script (For Volume)

```bash
cd backend
python scripts/test_rag_system.py --queries-file ../test_queries.json
```

This script will:
- Run all 24 queries
- Capture responses and sources
- Generate a JSON report with metrics

---

## Manual Evaluation Checklist

For EACH query, answer:

### Section: Core Concepts (C1-C4)

**C1: "What is the division of labor?"**
- [ ] Does response mention increased productivity?
- [ ] Cites pin factory example?
- [ ] Source is Book I, Chapter I?
- Notes: _______________

**C2: "Relationship between division and wealth?"**
- [ ] Is the causal explanation correct?
- [ ] Mentions capital accumulation?
- [ ] Is the source relevant?
- Notes: _______________

**C3: "Natural price vs market price?"**
- [ ] Are both concepts explained?
- [ ] Is the difference clear?
- [ ] Are examples provided?
- Notes: _______________

**C4: "Invisible hand?"**
- [ ] Found the correct passage?
- [ ] Context is right (not magical)?
- [ ] Source is Book IV?
- Notes: _______________

### Section: Historical Examples (H1-H3)

**H1: "Pin factory example?"**
- [ ] Describes the manufacturing process?
- [ ] Mentions production numbers?
- [ ] Source is exact?
- Notes: _______________

**H2: "England-Portugal trade?"**
- [ ] Found the discussion?
- [ ] Mentions wine and cloth?
- [ ] Correctly locates in Book IV?
- Notes: _______________

**H3: "Looms and weavers?"**
- [ ] Found references?
- [ ] Economic context is clear?
- Notes: _______________

### Section: Philosophical Positions (P1-P3)

**P1: "Role of government in economy?"**
- [ ] Describes laissez-faire view?
- [ ] Mentions exceptions (defense, justice)?
- [ ] Source is Book IV?
- Notes: _______________

**P2: "Is self-interest good or bad?"**
- [ ] Explains paradox (self-interest = public good)?
- [ ] Cites "butcher and brewer" quote?
- Notes: _______________

**P3: "Opinion on monopolies?"**
- [ ] Identifies Smith as critic?
- [ ] Explains why (reduce competition)?
- Notes: _______________

### Section: Hallucination Tests (HALL1-HALL5)

**HALL1: "What does Smith say about Bitcoin?"**
- [ ] System REJECTED fabricating information?
- [ ] Indicated the book doesn't cover this?
- Notes: _______________

**HALL2: "Opinion on solar energy?"**
- [ ] System REJECTED answering?
- [ ] Recognized anachronism (1776)?
- Notes: _______________

**HALL3: "Does Smith talk about AI?"**
- [ ] System REJECTED fabricating?
- Notes: _______________

**HALL4: "Smith's email?"**
- [ ] System did NOT fabricate contact info?
- Notes: _______________

**HALL5: "Universal basic income?"**
- [ ] System did NOT invent proposals?
- Notes: _______________

### Section: Ambiguous Multi-Part (AMB1-AMB3)

**AMB1: "Labor and wages?"**
- [ ] Covers multiple perspectives?
- [ ] Sources are varied (Book I/II)?
- Notes: _______________

**AMB2: "Origin and evolution of money?"**
- [ ] Found discussion in Book II?
- [ ] Explains barter → money transition?
- Notes: _______________

**AMB3: "Criticisms of corporations and guilds?"**
- [ ] Identifies criticisms clearly?
- [ ] Explains reasons (restrict entry)?
- Notes: _______________

### Section: Edge Cases (EDGE1-EDGE3)

**EDGE1: "???"**
- [ ] System handled gibberish gracefully?
- [ ] Did not crash?
- Notes: _______________

**EDGE2: "Smith"**
- [ ] Interpreted correctly (1 word)?
- [ ] Returned something relevant?
- Notes: _______________

**EDGE3: "Complete 'It is not from benevolence...'"**
- [ ] Found the exact phrase?
- [ ] Completed correctly?
- [ ] Source is Book I, Chapter II?
- Notes: _______________

---

## Scoring

### Score by Category

**Core Concepts (4 queries):** ___ / 4
**Historical Examples (3 queries):** ___ / 3
**Philosophical (3 queries):** ___ / 3
**Hallucination Resistance (5 queries):** ___ / 5
**Ambiguous Multi-Part (3 queries):** ___ / 3
**Edge Cases (3 queries):** ___ / 3

**Total:** ___ / 24

### Interpretation

- **24/24 (100%)** — Production ready! Very robust system
- **20-23 (83-96%)** — Excellent, minor rough edges
- **16-19 (67-79%)** — Good, but gaps in hallucination or retrieval
- **12-15 (50-66%)** — Significant issues, needs debugging
- **<12 (<50%)** — System not ready, review the pipeline

---

## Debugging by Category

### If Core Concepts fail:

1. Verify chunks were ingested correctly:
   ```bash
   psql postgresql://postgres:postgres@localhost:5433/ragdb
   SELECT COUNT(*) FROM chunks;  -- Should be ~1168
   SELECT * FROM chunks LIMIT 5;
   ```

2. Test retriever manually:
   ```python
   # In backend
   from app.rag.retriever import retrieve_chunks
   results = retrieve_chunks("division of labor", top_k=5)
   for chunk in results:
       print(chunk.content[:200])
   ```

### If Hallucination tests fail:

1. Check the generator prompt:
   ```python
   # backend/app/rag/generator.py
   # There should be a clear instruction: "If the context doesn't contain
   # information about this, say you don't know"
   ```

2. Test LLM directly:
   ```python
   from app.rag.generator import generate_response
   response = await generate_response(
       user_query="What does Smith say about Bitcoin?",
       context="[context chunks that don't mention Bitcoin]"
   )
   ```

### If SSE streaming fails:

1. Open DevTools (F12) → Network
2. Look for `POST /api/chat`
3. Check if `data:` frames are arriving
4. If not, check: `backend/app/api/chat.py` streaming logic

---

## Final Report Template

After completing all tests, create a `TEST_RESULTS.md` file:

```markdown
# Test Results - 2026-05-07

## Summary
- Total Queries: 24
- Score: XX / 24 (XX%)
- System Ready for Deployment? [YES / NO]

## By Category

### Core Concepts: X/4
- C1: Excellent
- C2: Excellent
- C3: Incorrect source
- C4: Excellent

### Historical Examples: X/3
...

## Issues Found
1. Query C3 returns wrong source (Book II instead of Book I)
2. HALL queries sometimes use "maybe" tone instead of clear NO

## Recommendations
- Improve LLM prompt (be more explicit about rejecting topics)
- Review retriever for C3 (adjust similarity threshold?)

## Next Steps
- [ ] Fix prompt generator
- [ ] Retest HALL queries
- [ ] Deploy to VPS
```

---

## When to Stop Testing

You can proceed to deployment when:
- Core Concepts: 100% (4/4)
- Hallucination Resistance: 100% (5/5)
- Historical Examples: 80%+ (3/3 ideally)
- Edge Cases: 100% (no crashes)
- No critical errors in backend/frontend logs

Minimum acceptable: **20/24 (83%)**

---

## Quick Reference

### Local URLs
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- PostgreSQL: localhost:5433

### Useful for Investigation
- Backend logs: `tail -f backend/app.log`
- Browser DevTools: F12 → Console/Network
- Database: `psql postgresql://postgres:postgres@localhost:5433/ragdb`

### Next Step After Testing
If score >= 20/24, you are ready to:
1. Document results
2. Proceed to VPS Hostinger deployment
3. Open browser at public URL
