# RAG System Testing Suite - Quick Start

## Files Created

### 1. **test_queries.json** (24 structured questions)
- **Core Concepts** (C1-C4): Fundamental concepts from the book
- **Historical Examples** (H1-H3): Specific examples cited by Smith
- **Philosophical Positions** (P1-P3): Views on government, monopolies, self-interest
- **Hallucination Tests** (HALL1-HALL5): Questions about things NOT in the book
- **Ambiguous/Multi-part** (AMB1-AMB3): Complex questions
- **Edge Cases** (EDGE1-EDGE3): Robustness tests

### 2. **TESTING_GUIDE.md** (Detailed testing manual)
- Step-by-step instructions (manual and automatic)
- Checklist of 24 questions for evaluation
- Scoring metrics
- Debugging guide per category
- Final report template

### 3. **backend/scripts/test_rag_system.py** (Automation)
- Python script for batch testing
- Modes: full suite, single query, or interactive
- Generates JSON report with metrics

---

## How to Use (3 Options)

### Option 1: Manual Test via UI (Fastest)

```bash
# Terminal 1 - Database
docker compose -f infra/docker-compose.yml up db -d

# Terminal 2 - Backend
cd backend
python -m uvicorn app.main:app --port 8000

# Terminal 3 - Frontend
cd frontend
npm run dev

# Open browser at http://localhost:3000
```

Then:
1. Copy the **24 questions** from `test_queries.json`
2. Paste in the chat one by one
3. Fill in the **checklist in TESTING_GUIDE.md**
4. Calculate final score (expected >= 20/24)

---

### Option 2: Automated Test (For Report)

```bash
cd backend

# Install dependency if needed
pip install httpx

# Run complete test
python scripts/test_rag_system.py --queries-file ../test_queries.json

# Output: test_results.json with metrics
```

Result:
- Tests all 24 queries automatically
- Captures responses and sources
- Generates `test_results.json` with success/failure per query

---

### Option 3: Interactive Test (For Exploration)

```bash
cd backend
python scripts/test_rag_system.py --interactive

# Type questions and see responses in real-time
Enter query: What is the division of labor?
[OK] Response: Adam Smith describes...
[SOURCES] (5 found):
  - The Wealth of Nations Book I, Chapter I
  ...
```

---

## Key Questions (Minimum to Pass)

If you want to test quickly, start with these 5:

| ID | Question | Expected | Type |
|---|---|---|---|
| **C1** | "What is the division of labor?" | Finds Book I, Chapter I | Core |
| **H1** | "What is the pin factory example?" | ~18 operations, 48,000 pins/day | Historical |
| **P1** | "What is the role of government?" | Laissez-faire, defense, justice | Philosophical |
| **HALL1** | "What does Smith say about Bitcoin?" | **REJECTS** inventing info | Hallucination |
| **EDGE3** | "Complete: 'It is not from benevolence...'" | Finds exact phrase from Book I, Chapter II | Edge |

If all 5 pass, the system is **functional**.

---

## Quick Scoring

```
Success = number of passed / 24

24/24 (100%)  → Ready for deployment
20-23 (83%)   → Very good, can deploy
16-19 (67%)   → Acceptable, some gaps
12-15 (50%)   → Issues, needs debugging
<12 (<50%)    → Not ready
```

---

## What Each Category Tests

### Core Concepts (C1-C4)
- Can system retrieve basic concepts?
- Are sources actually from the book?

### Historical Examples (H1-H3)
- Does retriever find specific examples?
- Does response cite exact data (e.g., "18 workers")?

### Philosophical (P1-P3)
- Does system understand Smith's complex arguments?
- Explains nuances (e.g., "government is bad BUT exceptions")?

### Hallucination Tests (CRITICAL)
- **HALL1-5:** Does system REJECT inventing about topics outside the book?
- If it fails here, the system is dangerous (hallucinates)
- This is the most important test for production

### Ambiguous/Multi-part (AMB1-AMB3)
- Can it handle vague questions?
- Returns multiple perspectives?

### Edge Cases (EDGE1-EDGE3)
- Does not crash with garbage input
- Correctly completes citations

---

## Next Steps

### If Passed (>= 20/24):
1. Document results in `TEST_RESULTS.md`
2. Commit: `git add -A && git commit -m "docs: testing results"`
3. Ready for **VPS Deployment**

### If Failed (< 20/24):
1. Identify which category failed (C? H? HALL?)
2. Use "Debugging" section in TESTING_GUIDE.md
3. Fix (could be prompt, retriever, or data)
4. Retest

---

## Extras

### View Ingested Chunks
```bash
psql postgresql://postgres:postgres@localhost:5433/ragdb

SELECT id, book, chapter, content FROM chunks LIMIT 10;
SELECT COUNT(*) FROM chunks;  -- Should be ~1168
```

### Test Retriever Directly
```python
# In backend Python shell
from app.rag.retriever import retrieve_chunks
chunks = retrieve_chunks("division of labor", top_k=5)
for chunk in chunks:
    print(f"{chunk.metadata['chapter']}: {chunk.content[:100]}")
```

### Check Backend Logs
```bash
# If running with logging enabled
tail -f backend/app.log
```

---

## Tips

1. **Save questions in a doc** — makes retesting easier
2. **Note issues** — helps debug patterns
3. **Test HALL queries first** — if it hallucinates, that's the critical issue
4. **Compare with local responses** — read the book if needed to validate
5. **Test at different times** — OpenAI API sometimes has latency issues

---

## Troubleshooting

### "Connection refused" (Backend not running)
```bash
cd backend && python -m uvicorn app.main:app --port 8000
```

### "Database connection failed"
```bash
docker compose -f infra/docker-compose.yml up db -d
```

### "No chunks found" (Ingestion not run)
```bash
cd backend
python scripts/download_book.py
python -m app.rag.ingest
```

### Script returns "HTTP 401" or auth error
- Make sure you are logged in to the frontend first
- Or update the script to pass `Authorization: Bearer <token>`

---

## Summary

| File | What it is | How to use |
|---|---|---|
| `test_queries.json` | 24 organized questions | Paste in chat / use in automated test |
| `TESTING_GUIDE.md` | Checklist + debugging | Fill in while testing manually |
| `test_rag_system.py` | Test automation | `python ... --queries-file ../test_queries.json` |

**Estimated time:** 30 min (manual) or 5 min (automated)

**Success criterion:** >= 20/24 questions pass
