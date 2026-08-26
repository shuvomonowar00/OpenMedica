FROM python:3.11-slim

# Copy the official uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy lockfiles and install exactly what is locked
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy source code
COPY . .

# Install the project itself (if needed)
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Start FastAPI server via uv run
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
