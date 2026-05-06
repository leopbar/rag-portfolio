"""
Langfuse tracing helpers.

Usage in endpoints:
    with observe_chat(question) as trace:
        chunks = await retrieve(...)
        trace.log_retrieval(chunks)
        async for token in generate_stream(...):
            ...
        trace.log_generation(answer, tokens_used)
"""

from contextlib import contextmanager
from typing import Any, Generator

import structlog

from app.core.config import settings

log = structlog.get_logger()

_langfuse: Any = None


def get_langfuse() -> Any:
    global _langfuse
    if _langfuse is None and settings.langfuse_public_key:
        try:
            from langfuse import Langfuse

            _langfuse = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
            )
            log.info("Langfuse initialized", host=settings.langfuse_host)
        except Exception as exc:
            log.warning("Langfuse init failed — tracing disabled", error=str(exc))
    return _langfuse


class ChatTrace:
    """Thin wrapper that records a single chat interaction in Langfuse."""

    def __init__(self, question: str) -> None:
        self._question = question
        self._trace: Any = None
        self._span: Any = None

        lf = get_langfuse()
        if lf:
            self._trace = lf.trace(name="chat", input=question)

    def log_retrieval(self, chunks: list[Any]) -> None:
        if self._trace:
            self._trace.span(
                name="retrieval",
                output=[
                    {"id": c.id, "book": c.book, "chapter": c.chapter, "score": c.score}
                    for c in chunks
                ],
            )

    def log_generation(self, answer: str, model: str) -> None:
        if self._trace:
            self._trace.generation(
                name="llm",
                model=model,
                output=answer,
            )

    def finish(self) -> None:
        lf = get_langfuse()
        if lf:
            lf.flush()


@contextmanager
def observe_chat(question: str) -> Generator[ChatTrace, None, None]:
    trace = ChatTrace(question)
    try:
        yield trace
    finally:
        trace.finish()
