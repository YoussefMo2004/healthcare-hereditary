# Healthcare Prediction API — production image
#
# Multi-stage build:
#   builder — installs all Python deps into a virtual-env
#   runtime — copies only the venv + application code (no build tools)
#
# Build:
#   docker build -f infra/docker/api.Dockerfile -t healthcare-api:latest .
#
# The build context must be the monorepo root so that libs/, services/,
# and ml/ are all available.

# ── Stage 1: dependency builder ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies for psycopg2, lxml, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment so it can be cleanly copied to the runtime stage
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (pin to avoid non-deterministic builds)
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# API runtime dependencies
RUN pip install --no-cache-dir \
    fastapi==0.110.3 \
    uvicorn[standard]==0.29.0 \
    pydantic==2.7.1 \
    pydantic-settings==2.2.1 \
    redis==5.0.4 \
    psycopg2-binary==2.9.9 \
    neo4j==5.19.0 \
    mlflow==2.13.0 \
    prometheus-client==0.15.0 \
    xgboost==2.0.3 \
    numpy==1.26.4 \
    shap==0.45.1


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="healthcare-api"
LABEL org.opencontainers.image.description="Healthcare Hereditary Disease Prediction API"

# Runtime system deps (libpq for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for least-privilege execution
RUN useradd --no-create-home --shell /bin/false appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy application source (only what the API needs)
COPY libs/ ./libs/
COPY services/api/ ./services/api/
COPY ml/features/ ./ml/features/
COPY ml/serving/bentoml_service.py ./ml/serving/bentoml_service.py
COPY ml/serving/__init__.py ./ml/serving/__init__.py

# Ensure the monorepo root is on PYTHONPATH
ENV PYTHONPATH="/app"

USER appuser

EXPOSE 8000

# Healthcheck mirrors the /health liveness probe
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "services.api.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--workers", "2", \
    "--log-level", "info"]
