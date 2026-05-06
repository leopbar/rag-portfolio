FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency manifest first (better layer caching)
COPY pyproject.toml .

# Install dependencies (no dev extras in production)
RUN uv pip install --system --no-cache .

# Copy application code
COPY app/ ./app/
COPY migrations/ ./migrations/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
