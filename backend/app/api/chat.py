import json
from collections.abc import AsyncGenerator

import structlog
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.observability.langfuse_client import observe_chat
from app.rag.generator import generate_stream
from app.rag.retriever import RetrievedChunk, retrieve

log = structlog.get_logger()
router = APIRouter()


class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[Message] = []


class SourceInfo(BaseModel):
    id: int
    book: str
    chapter: str
    section: str | None
    score: float


async def _event_stream(
    question: str,
    chunks: list[RetrievedChunk],
    history: list[dict[str, str]],
) -> AsyncGenerator[str, None]:
    """
    Server-Sent Events stream.

    Protocol used by the frontend (Vercel AI SDK compatible):
      - text tokens:  data: <token>\n\n
      - sources:      data: [SOURCES] <json>\n\n
      - end:          data: [DONE]\n\n
    """
    with observe_chat(question) as trace:
        sources = [
            SourceInfo(
                id=c.id,
                book=c.book,
                chapter=c.chapter,
                section=c.section,
                score=round(c.score, 4),
            ).model_dump()
            for c in chunks
        ]
        trace.log_retrieval(chunks)
        yield f"data: [SOURCES] {json.dumps(sources)}\n\n"

        answer_parts: list[str] = []
        async for token in generate_stream(question, chunks, history):
            answer_parts.append(token)
            yield f"data: {token}\n\n"

        trace.log_generation("".join(answer_parts), model=settings.llm_model)
        yield "data: [DONE]\n\n"


@router.post("/")
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    log.info("Chat request received", question=request.question[:80])

    chunks = await retrieve(request.question, session)
    history = [m.model_dump() for m in request.history]

    return StreamingResponse(
        _event_stream(request.question, chunks, history),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
