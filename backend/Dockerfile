FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e .

COPY app ./app

EXPOSE 8000

# Bind to Railway's injected $PORT (falls back to 8000 for local runs).
# Shell form is required so the variable is expanded at runtime.
CMD gunicorn app.main:app -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 300
