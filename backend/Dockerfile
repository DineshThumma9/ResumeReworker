# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Copy docker CLI from official docker image for sibling container access
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker

# Install system dependencies needed by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libffi-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager) — used instead of pip for speed
RUN pip install --no-cache-dir uv

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies from lockfile (no dev deps)
RUN uv sync --frozen --no-dev

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Give appuser ownership of the app dir (including .venv) and
# pre-create a uv cache dir it can write to at runtime.
RUN chown -R appuser:appuser /app

USER appuser

# Add the virtual environment to the system PATH globally
ENV PATH="/app/.venv/bin:$PATH"

# Call gunicorn directly, which now resolves from the updated PATH
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--forwarded-allow-ips", "*"]
