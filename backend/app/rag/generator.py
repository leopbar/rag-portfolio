from collections.abc import AsyncGenerator

from openai import AsyncOpenAI

from app.core.config import settings
from app.rag.prompts import SYSTEM_PROMPT, build_context_block
from app.rag.retriever import RetrievedChunk

_client = AsyncOpenAI(api_key=settings.openai_api_key)


async def generate(
    question: str,
    chunks: list[RetrievedChunk],
    history: list[dict[str, str]] | None = None,
) -> str:
    """Generate a complete (non-streaming) answer grounded in retrieved chunks."""
    messages = _build_messages(question, chunks, history)
    response = await _client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,  # type: ignore[arg-type]
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


async def generate_stream(
    question: str,
    chunks: list[RetrievedChunk],
    history: list[dict[str, str]] | None = None,
) -> AsyncGenerator[str, None]:
    """Stream the LLM answer token-by-token (used by the SSE endpoint)."""
    messages = _build_messages(question, chunks, history)
    stream = await _client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,  # type: ignore[arg-type]
        temperature=0.2,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def _build_messages(
    question: str,
    chunks: list[RetrievedChunk],
    history: list[dict[str, str]] | None,
) -> list[dict[str, str]]:
    context_block = build_context_block(chunks)
    user_content = f"Context:\n---\n{context_block}\n---\n\nQuestion: {question}"

    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": user_content})
    return messages
