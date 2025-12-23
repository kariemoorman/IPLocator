# -----------------------------
# Stage 1: Builder
# -----------------------------
FROM python:3.12-alpine3.22 AS builder

# Install build dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-virtualenv \
    build-base \
    libffi-dev \
    openssl-dev \
    cargo

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt \
    && /venv/bin/pip install --no-cache-dir gunicorn

# Copy application code and GeoLite2 database
COPY IPLocator-App/ ./IPLocator-App/
COPY IPLocator-App/src/GeoLite2-City.mmdb ./IPLocator-App/src/

# -----------------------------
# Stage 2: Runtime
# -----------------------------
FROM python:3.12-alpine3.22

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /venv /venv

# Copy application code
COPY --from=builder /app/IPLocator-App ./IPLocator-App

# Set environment variables
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH=/app/IPLocator-App/src

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:8000/health || exit 1

# Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "IPLocator-App.src.app:app"]
