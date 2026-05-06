from app.rag.chunker import chunk_book

SAMPLE_TEXT = """
INTRODUCTION AND PLAN OF THE WORK

The greatest improvement in the productive powers of labour seems to have been the effects
of the division of labour. This is a short introduction paragraph.

BOOK I

OF THE CAUSES OF IMPROVEMENT IN THE PRODUCTIVE POWERS OF LABOUR

CHAPTER I

OF THE DIVISION OF LABOUR

To take an example from a very trifling manufacture, the trade of the pin-maker.
A person who has never exercised this trade could scarce make one pin in a day.
But in the way in which this business is now carried on, it is divided into a number
of branches. One man draws out the wire, another straights it, a third cuts it.
"""


def test_chunk_book_returns_chunks() -> None:
    chunks = chunk_book(SAMPLE_TEXT, chunk_size=128, overlap=16)
    assert len(chunks) > 0


def test_chunk_book_metadata_attached() -> None:
    chunks = chunk_book(SAMPLE_TEXT, chunk_size=128, overlap=16)
    book_one_chunks = [c for c in chunks if c.book == "BOOK I"]
    assert len(book_one_chunks) > 0
    for chunk in book_one_chunks:
        assert chunk.chapter == "CHAPTER I"
        assert chunk.chunk_type == "passage"
        assert chunk.token_count > 0


def test_chunk_book_no_empty_content() -> None:
    chunks = chunk_book(SAMPLE_TEXT, chunk_size=128, overlap=16)
    for chunk in chunks:
        assert chunk.content.strip() != ""


def test_chunk_book_token_count_within_limit() -> None:
    chunk_size = 64
    chunks = chunk_book(SAMPLE_TEXT, chunk_size=chunk_size, overlap=8)
    for chunk in chunks:
        assert chunk.token_count <= chunk_size
