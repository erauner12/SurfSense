# syntax=docker/dockerfile:1.5
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN rm -f /var/cache/apt/archives/lock /var/lib/apt/lists/lock && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir uv && \
    uv pip install --system --no-cache-dir -e .

# Install Playwright browsers for web scraping if needed
ARG INSTALL_PLAYWRIGHT=false
RUN if [ "$INSTALL_PLAYWRIGHT" = "true" ]; then \
      pip install playwright && playwright install --with-deps chromium ; \
    fi

# --- Runtime Stage ---
FROM python:3.12-slim AS runtime

WORKDIR /app

# Prevent uvloop compatibility issues
ENV PYTHONPATH=/app
ENV UVICORN_LOOP=asyncio
ENV DISABLE_FFMPEG_CHECK=""

RUN useradd -u 1001 -r -s /sbin/nologin appuser

COPY --from=builder /usr/local /usr/local
# Copy source code
COPY . .

# Add permission changes before switching user
RUN chown -R 1001:0 /app && chmod -R g=u /app /tmp

USER appuser

# Run
EXPOSE 8000
CMD ["python", "main.py"] 