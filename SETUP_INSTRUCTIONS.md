# Development Setup Guide

This guide provides step-by-step instructions for setting up the Healthcare Hereditary Disease Prediction System for local development.

## Prerequisites

Before starting, ensure you have:
- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Docker Desktop** — [Download](https://www.docker.com/products/docker-desktop)
- **Docker Compose** (usually included with Docker Desktop)
- **Git** — [Download](https://git-scm.com/downloads)
- **~8 GB RAM** (minimum for running all services)
- **~20 GB disk space** (for Docker images and data volumes)

Verify installations:
```bash
python --version           # Should show 3.11+
docker --version           # Should show 20.10+
docker compose version     # Should show 2.0+
git --version              # Should show 2.0+
```

## Step 1: Clone the Repository

```bash
# Clone repository
git clone https://github.com/your-org/healthcare-hereditary.git
cd healthcare-hereditary

# Verify structure
ls -la    # Should show Makefile, README.md, docker-compose.yml, etc.
```

## Step 2: Set Up Python Environment

### Option A: Using venv (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Windows CMD:
.venv\Scripts\activate.bat

# Verify activation (prompt should show (.venv))
python --version
```

### Option B: Using conda
```bash
# Create conda environment
conda create -n healthcare python=3.11
conda activate healthcare

# Verify activation (prompt should show (healthcare))
python --version
```

## Step 3: Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install development dependencies (for testing, linting, etc.)
pip install -r requirements-dev.txt

# Or install as editable package
pip install -e ".[dev]"

# Verify installation
pip list | grep -E "fastapi|streamlit|xgboost|pandas"
```

## Step 4: Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env and update these values:
# POSTGRES_PASSWORD=your_secure_password
# NEO4J_PASSWORD=your_secure_password
# MINIO_SECRET_KEY=your_secure_password
# REDIS_PASSWORD=your_secure_password

# For development, you can use simple values:
cat > .env << 'EOF'
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=healthcare
POSTGRES_USER=healthcare_app
NEO4J_HOST=neo4j
NEO4J_BOLT_PORT=7687
NEO4J_HTTP_PORT=7474
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j123
NEO4J_URI=bolt://neo4j:7687
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_SCHEMA_REGISTRY_URL=http://schema-registry:8081
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET_RAW=healthcare-raw
MINIO_BUCKET_DELTA=healthcare-delta
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_EXPERIMENT_NAME=hereditary-disease-prediction
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin123
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis123
SPARK_MASTER_URL=spark://spark-master:7077
API_PORT=8000
API_ENV=development
API_LOG_LEVEL=INFO
APP_SECRET_KEY=development-secret-key-at-least-32-characters-long
STREAMLIT_PORT=8501
AIRFLOW_PORT=8082
AIRFLOW_FERNET_KEY=development-fernet-key-for-airflow-32-chars
AIRFLOW_SECRET_KEY=development-airflow-secret-key-32-chars
AIRFLOW_ADMIN_USER=admin
AIRFLOW_ADMIN_PASSWORD=airflow123
GRAFANA_PORT=3000
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=grafana123
PROMETHEUS_PORT=9090
APP_ENV=development
APP_LOG_LEVEL=INFO
ENCRYPTION_KEY=development-encryption-key-32-chars-long
ENABLE_GNN_MODEL=false
ENABLE_SYMPTOM_MODEL=false
MODEL_NAME=hereditary-risk-xgboost
MODEL_STAGE=Staging
XGB_N_ESTIMATORS=500
XGB_MAX_DEPTH=6
XGB_LEARNING_RATE=0.05
EOF
```

## Step 5: Start Docker Services

```bash
# Start all services in background
docker compose -f infra/compose/docker-compose.yml up -d

# Wait for services to be healthy (~30 seconds)
sleep 30

# Verify all services are running
docker compose ps

# You should see services like: postgres, neo4j, kafka, mlflow, redis, spark, streamlit, etc.
```

## Step 6: Verify Services Are Healthy

```bash
# Check PostgreSQL
docker compose exec postgres pg_isready -U healthcare_app

# Check Neo4j
curl http://localhost:7474

# Check MLflow
curl http://localhost:5000/health

# Check Streamlit
curl http://localhost:8501/_stcore/health

# View logs if any service fails
docker compose logs [service_name]
```

## Step 7: Initialize Databases (Optional)

```bash
# Apply PostgreSQL migrations
python -m alembic -c schemas/postgres/alembic.ini upgrade head

# View migration history
python -m alembic -c schemas/postgres/alembic.ini history

# Rollback last migration (if needed)
python -m alembic -c schemas/postgres/alembic.ini downgrade -1
```

## Step 8: Access Services

Once everything is running, access these URLs:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Streamlit Web UI** | http://localhost:8501 | N/A |
| **FastAPI Docs** | http://localhost:8000/docs | N/A |
| **Neo4j Browser** | http://localhost:7474 | neo4j / neo4j123 |
| **MLflow Dashboard** | http://localhost:5000 | N/A |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin123 |
| **Spark Master** | http://localhost:8080 | N/A |
| **PostgreSQL** | localhost:5432 | healthcare_app / postgres123 |

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest -m unit

# Run with coverage report
pytest --cov=libs --cov=services --cov=ml

# Run specific test file
pytest tests/unit/test_phi.py

# Run specific test function
pytest tests/unit/test_phi.py::test_redact_phi
```

### Code Quality

```bash
# Format code
black services/ ml/ pipelines/ libs/

# Lint code
ruff check services/ ml/ pipelines/ libs/
ruff check --fix services/ ml/ pipelines/ libs/

# Type checking
mypy services/ ml/ libs/

# All in one
make lint    # or: ruff check && black --check && mypy
make fmt     # or: black && ruff check --fix
make typecheck
```

### Running Services

```bash
# Follow logs for specific service
docker compose logs -f streamlit
docker compose logs -f api
docker compose logs -f postgres

# Restart a service
docker compose restart streamlit

# Stop all services
docker compose down

# Stop and remove all volumes (clean slate)
docker compose down -v

# Rebuild images
docker compose build streamlit
docker compose build api

# Rebuild and restart
docker compose up -d --build streamlit
```

### Database Operations

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U healthcare_app -d healthcare

# Common PostgreSQL commands inside psql:
\dt                          # List tables
SELECT * FROM patients;      # Query patients
\d patients                  # Describe patients table

# Connect to Neo4j
docker compose exec neo4j cypher-shell -u neo4j -p neo4j123

# Query example:
MATCH (p:Patient) RETURN p LIMIT 10;
```

## Troubleshooting

### Problem: Python version mismatch
```bash
# Verify Python 3.11+
python --version

# If not 3.11+, install it or use pyenv
pyenv install 3.11.8
pyenv shell 3.11.8
```

### Problem: Docker services won't start
```bash
# Check Docker is running
docker ps

# Verify Docker has enough resources
docker system info | grep -E "Memory|CPUs"

# Clean up old containers/images
docker system prune -a

# Restart Docker daemon
# macOS: Docker menu > Restart
# Windows: Restart Docker Desktop
# Linux: sudo systemctl restart docker
```

### Problem: Port already in use
```bash
# Find process using port
# macOS/Linux:
lsof -i :8501

# Windows PowerShell:
Get-Process -Id (Get-NetTCPConnection -LocalPort 8501).OwningProcess

# Kill process or change port in .env
STREAMLIT_PORT=8502
```

### Problem: Module not found
```bash
# Verify virtual environment is activated (should show (.venv) in prompt)
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt -r requirements-dev.txt --force-reinstall
```

### Problem: Database connection errors
```bash
# Check databases are healthy
docker compose ps | grep -E "postgres|neo4j"

# Check logs
docker compose logs postgres
docker compose logs neo4j

# Restart databases
docker compose restart postgres neo4j
```

## Making Your First Change

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes** (see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines)

3. **Run tests and linting:**
   ```bash
   pytest
   ruff check --fix
   black .
   mypy
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/my-new-feature
   ```

6. **Create a Pull Request** on GitHub

## Next Steps

- Read [QUICKSTART.md](QUICKSTART.md) for system overview
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Check [PROJECT_AUDIT.md](PROJECT_AUDIT.md) for architecture details
- Explore [CLAUDE.md](CLAUDE.md) for AI development guide

## Getting Help

- **Issues:** Open an issue on GitHub
- **Discussions:** Join GitHub Discussions
- **Email:** team@healthcare.local

## Summary

Your development environment is now ready! Start coding and contributing. Good luck! 🚀
