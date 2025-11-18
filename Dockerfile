# Multi-stage build for Lawdit
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy dependency files
COPY pyproject.toml setup.py README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e .

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 lawdit && \
    mkdir -p /app /app/data_room_processing /app/outputs && \
    chown -R lawdit:lawdit /app

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=lawdit:lawdit src/ ./src/
COPY --chown=lawdit:lawdit pyproject.toml setup.py README.md ./

# Install the package
RUN pip install --no-cache-dir -e .

# Switch to non-root user
USER lawdit

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WORKING_DIR=/app/data_room_processing \
    OUTPUT_DIR=/app/outputs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import lawdit; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "lawdit.indexer.cli", "--help"]
