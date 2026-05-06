"""
RAG Evaluation Suite — measures retrieval recall@k across 20 reference questions.

Usage:
    python -m tests.eval.run_eval

Requires:
    - Running Postgres with ingested chunks (docker compose up db && python -m app.rag.ingest)
    - OPENAI_API_KEY set in .env

Metrics:
    - recall@k: % of questions where the expected book+chapter appears in top-k results
    - avg_score: mean cosine similarity of the top-1 result
    - avg_latency_ms: mean retrieval latency
"""

import asyncio
import json
import time
from pathlib import Path

import structlog
from dotenv import load_dotenv

load_dotenv()

from app.db.session import AsyncSessionLocal
from app.rag.retriever import retrieve

log = structlog.get_logger()

QUESTIONS_PATH = Path(__file__).parent / "questions.json"


async def evaluate_question(
    question: str,
    expected_book: str,
    expected_chapter: str,
    top_k: int = 5,
) -> dict:
    t0 = time.perf_counter()
    async with AsyncSessionLocal() as session:
        chunks = await retrieve(question, session, top_k=top_k)
    latency_ms = (time.perf_counter() - t0) * 1000

    retrieved_pairs = [(c.book, c.chapter) for c in chunks]
    hit = any(
        book == expected_book and chapter == expected_chapter
        for book, chapter in retrieved_pairs
    )
    top1_score = chunks[0].score if chunks else 0.0

    return {
        "hit": hit,
        "top1_score": top1_score,
        "latency_ms": round(latency_ms, 1),
        "retrieved": retrieved_pairs,
    }


async def run() -> None:
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    total = len(questions)
    hits = 0
    scores: list[float] = []
    latencies: list[float] = []

    print(f"\nEvaluating {total} questions (recall@5)\n{'─' * 60}")

    for q in questions:
        result = await evaluate_question(
            question=q["question"],
            expected_book=q["expected_book"],
            expected_chapter=q["expected_chapter"],
        )
        hits += result["hit"]
        scores.append(result["top1_score"])
        latencies.append(result["latency_ms"])

        status = "✓" if result["hit"] else "✗"
        print(
            f"[{status}] Q{q['id']:02d} | {q['expected_book']} {q['expected_chapter']}"
            f" | score={result['top1_score']:.3f} | {result['latency_ms']:.0f}ms"
        )

    recall = hits / total * 100
    avg_score = sum(scores) / len(scores)
    avg_latency = sum(latencies) / len(latencies)

    print(f"\n{'─' * 60}")
    print(f"Recall@5:        {recall:.1f}%  ({hits}/{total} hits)")
    print(f"Avg top-1 score: {avg_score:.4f}")
    print(f"Avg latency:     {avg_latency:.0f}ms")
    print(f"{'─' * 60}\n")

    if recall < 80:
        print("⚠  Target is ≥80% recall@5 — consider re-tuning chunk size or embeddings.")
    else:
        print("✅ Target met!")


if __name__ == "__main__":
    asyncio.run(run())
