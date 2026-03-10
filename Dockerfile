# Use official Python image as base
# Using 3.14 as required by pyproject.toml
FROM python:3.14-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (astral)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy dependency manifest (first for layer cache)
COPY pyproject.toml ./

# Install Python deps via uv
RUN uv sync

# Copy project files
COPY . .

# Expose port (Render provides $PORT at runtime)
EXPOSE 8000

# Start server using exec form (fixed port 8000). Note: exec form does not expand shell variables.
CMD ln -sf /etc/secrets/.env /app/.env && uv run uvicorn src.server.main:app --host 0.0.0.0 --port 8000
