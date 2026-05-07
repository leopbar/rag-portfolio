"""
Hierarchical chunker for The Wealth of Nations (Project Gutenberg plain text).

Parsing strategy:
  1. Detect BOOK and CHAPTER boundaries using regex.
  2. Split each chapter's text into token-bounded chunks (512 tokens, 64 overlap).
  3. Attach metadata {book, chapter, section} to every chunk.
"""

import re
from dataclasses import dataclass

import tiktoken

BOOK_RE = re.compile(r"^BOOK\s+(I{1,3}V?|VI{0,3}|IV|IX|XI{0,3})\.?\s*$", re.MULTILINE)
CHAPTER_RE = re.compile(r"^CHAPTER\s+(I{1,3}V?|VI{0,3}|IV|IX|XI{0,3})\.?\s*$", re.MULTILINE)


@dataclass
class ChunkData:
    content: str
    book: str
    chapter: str
    section: str | None
    chunk_type: str
    token_count: int


def _split_by_pattern(text: str, pattern: re.Pattern[str]) -> list[tuple[str, str]]:
    """Return list of (label, body) pairs split by a regex pattern."""
    matches = list(pattern.finditer(text))
    if not matches:
        return [("UNKNOWN", text)]

    sections: list[tuple[str, str]] = []
    for i, match in enumerate(matches):
        label = match.group().strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections.append((label, body))
    return sections


def _token_chunks(
    text: str,
    enc: tiktoken.Encoding,
    chunk_size: int,
    overlap: int,
) -> list[tuple[str, int]]:
    """Split text into (chunk_text, token_count) pairs respecting token limits."""
    tokens = enc.encode(text)
    results: list[tuple[str, int]] = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens).strip()
        if chunk_text:
            results.append((chunk_text, len(chunk_tokens)))
        start += chunk_size - overlap
    return results


def chunk_book(
    text: str,
    chunk_size: int = 512,
    overlap: int = 64,
) -> list[ChunkData]:
    """
    Parse the full book text and return all ChunkData objects with metadata.
    """
    enc = tiktoken.get_encoding("cl100k_base")
    chunks: list[ChunkData] = []

    # Handle content before the first BOOK marker as an introduction
    first_book = BOOK_RE.search(text)
    preamble = text[: first_book.start()].strip() if first_book else text

    if preamble:
        for chunk_text, token_count in _token_chunks(preamble, enc, chunk_size, overlap):
            chunks.append(
                ChunkData(
                    content=chunk_text,
                    book="INTRODUCTION",
                    chapter="Introduction",
                    section=None,
                    chunk_type="passage",
                    token_count=token_count,
                )
            )

    for book_label, book_body in _split_by_pattern(text, BOOK_RE):
        for chapter_label, chapter_body in _split_by_pattern(book_body, CHAPTER_RE):
            # Extract optional section title (first non-empty line after CHAPTER header)
            lines = chapter_body.splitlines()
            section_title: str | None = None
            body_start = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith("CHAPTER"):
                    section_title = stripped[:120]
                    body_start = i + 1
                    break

            body = "\n".join(lines[body_start:]).strip()
            if not body:
                continue

            for chunk_text, token_count in _token_chunks(body, enc, chunk_size, overlap):
                chunks.append(
                    ChunkData(
                        content=chunk_text,
                        book=book_label,
                        chapter=chapter_label,
                        section=section_title,
                        chunk_type="passage",
                        token_count=token_count,
                    )
                )

    return chunks
