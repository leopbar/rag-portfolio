"""
Full ingestion pipeline. Run once after downloading the book:

    python -m app.rag.ingest

Steps:
  1. Read the book from data/wealth-of-nations.txt
  2. Chunk hierarchically with metadata
  3. Generate OpenAI embeddings in batches
  4. Bulk-insert into Postgres chunks table
"""

import asyncio
import time
from pathlib import Path

import structlog
from sqlalchemy import delete

from app.db.models import Chunk
from app.db.session import AsyncSessionLocal
from app.rag.chunker import ChunkData, chunk_book
from app.rag.embedder import embed_texts

log = structlog.get_logger()

BOOK_PATH = Path(__file__).parent.parent.parent / "data" / "wealth-of-nations.txt"


async def _clear_existing(session: object) -> None:
    from sqlalchemy.ext.asyncio import AsyncSession
    assert isinstance(session, AsyncSession)
    await session.execute(delete(Chunk))
    await session.commit()
    log.info("Cleared existing chunks")


async def _insert_chunks(chunks: list[ChunkData], embeddings: list[list[float]]) -> None:
    async with AsyncSessionLocal() as session:
        await _clear_existing(session)

        db_chunks = [
            Chunk(
                content=chunk.content,
                embedding=embedding,
                book=chunk.book,
                chapter=chunk.chapter,
                section=chunk.section,
                chunk_type=chunk.chunk_type,
                token_count=chunk.token_count,
            )
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]

        session.add_all(db_chunks)
        await session.commit()
        log.info("Inserted chunks", count=len(db_chunks))


async def run() -> None:
    if not BOOK_PATH.exists():
        raise FileNotFoundError(
            f"Book not found at {BOOK_PATH}. "
            "Run: python scripts/download_book.py"
        )

    log.info("Reading book", path=str(BOOK_PATH))
    text = BOOK_PATH.read_text(encoding="utf-8")

    log.info("Chunking book...")
    t0 = time.perf_counter()
    chunks = chunk_book(text)
    log.info("Chunking complete", chunks=len(chunks), seconds=round(time.perf_counter() - t0, 2))

    log.info("Generating embeddings...", batches=len(chunks) // 100 + 1)
    t0 = time.perf_counter()
    embeddings = await embed_texts([c.content for c in chunks])
    log.info("Embeddings ready", seconds=round(time.perf_counter() - t0, 2))

    log.info("Inserting into database...")
    await _insert_chunks(chunks, embeddings)

    log.info("Ingestion complete", total_chunks=len(chunks))


if __name__ == "__main__":
    asyncio.run(run())
