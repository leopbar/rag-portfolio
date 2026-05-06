import asyncio

from openai import AsyncOpenAI

from app.core.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)

BATCH_SIZE = 100  # OpenAI allows up to 2048 inputs per request; 100 is safe and fast


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts, processing in batches."""
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        response = await _client.embeddings.create(
            model=settings.embedding_model,
            input=batch,
        )
        # API returns embeddings sorted by index
        batch_embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
        all_embeddings.extend(batch_embeddings)

        # Avoid hitting rate limits on large ingestions
        if i + BATCH_SIZE < len(texts):
            await asyncio.sleep(0.5)

    return all_embeddings
