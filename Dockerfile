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
COPY pyproject.toml uv.lock ./

# Install Python deps via uv
# --no-install-project: Install dependencies but not the project itself (allows caching)
RUN uv sync --frozen --no-install-project --no-dev

# Copy project files
COPY . .

# Install the project itself now that source is available
RUN uv sync --frozen --no-dev

# Expose port (Render provides $PORT at runtime, defaults to 10000)
EXPOSE 10000

# Start server using sh to expand $PORT variable
# 'uv run' ensures we run within the environment set up by 'uv sync'
CMD ["sh", "-c", "uv run uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
