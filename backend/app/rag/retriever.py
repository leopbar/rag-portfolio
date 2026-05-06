from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.rag.embedder import embed_texts


@dataclass
class RetrievedChunk:
    id: int
    content: str
    book: str
    chapter: str
    section: str | None
    chunk_type: str
    score: float  # cosine similarity: 1.0 = identical, 0.0 = unrelated


async def retrieve(
    query: str,
    session: AsyncSession,
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    """
    Embed the query and return the top-k most similar chunks from Postgres.

    Uses pgvector's <=> operator (cosine distance).
    Cosine distance = 1 - cosine_similarity, so we invert to get similarity score.
    """
    k = top_k or settings.retrieval_top_k
    query_embeddings = await embed_texts([query])
    query_vector = query_embeddings[0]

    # pgvector syntax: embedding <=> :vec returns cosine *distance* (0=identical, 2=opposite)
    sql = text("""
        SELECT
            id,
            content,
            book,
            chapter,
            section,
            chunk_type,
            1 - (embedding <=> CAST(:vec AS vector)) AS score
        FROM chunks
        ORDER BY embedding <=> CAST(:vec AS vector)
        LIMIT :k
    """)

    result = await session.execute(sql, {"vec": str(query_vector), "k": k})
    rows = result.mappings().all()

    return [
        RetrievedChunk(
            id=row["id"],
            content=row["content"],
            book=row["book"],
            chapter=row["chapter"],
            section=row["section"],
            chunk_type=row["chunk_type"],
            score=float(row["score"]),
        )
        for row in rows
    ]
