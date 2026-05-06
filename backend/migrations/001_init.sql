-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Main chunks table: stores text passages + their vector embeddings
CREATE TABLE IF NOT EXISTS chunks (
    id          BIGSERIAL PRIMARY KEY,
    content     TEXT NOT NULL,
    embedding   VECTOR(1536) NOT NULL,          -- text-embedding-3-small dimensions
    book        TEXT NOT NULL,                   -- e.g. "I", "II", "III", "IV", "V"
    chapter     TEXT NOT NULL,                   -- e.g. "Chapter 1"
    section     TEXT,                            -- optional sub-section title
    chunk_type  TEXT NOT NULL DEFAULT 'passage', -- 'passage' | 'summary'
    token_count INT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast approximate nearest-neighbor search (cosine distance)
-- HNSW outperforms IVFFlat for our volume (~5-10k chunks) with no training step needed
CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);

-- Composite index for metadata filtering (e.g. search within a specific book)
CREATE INDEX IF NOT EXISTS chunks_book_chapter_idx
    ON chunks (book, chapter);
