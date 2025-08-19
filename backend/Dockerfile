# Multi-stage Dockerfile optimized for Alibaba Cloud Container Registry
# Stage 1: Build dependencies
FROM python:3.9-slim AS builder

# Set build arguments
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Install system dependencies for building with Alibaba Cloud mirrors
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y \
    build-essential \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com && \
    pip config set global.timeout 60 && \
    pip install --upgrade pip setuptools wheel --no-cache-dir && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime image
FROM python:3.9-slim AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_ENV=production \
    LOG_LEVEL=INFO

# Install only runtime system dependencies with Alibaba Cloud mirrors
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create app directory and set permissions
WORKDIR /app
RUN chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check for Kubernetes readiness/liveness probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health/ready || exit 1

# Expose port
EXPOSE 8000

# Use exec form for better signal handling in containers
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--access-log"]