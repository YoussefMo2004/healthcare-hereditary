# Healthcare Hereditary Disease Prediction System

A production-grade platform for predicting hereditary disease risk using patient
records, family relationship graphs, and machine learning.

## Quick Start (local dev)

```bash
# 1. Copy and fill in secrets
cp .env.example .env

# 2. Validate environment
make check-env

# 3. Start all base services
make up

# 4. Verify everything is healthy
make ps
```

### Service URLs

| Service      | URL                        | Credentials          |
|--------------|----------------------------|----------------------|
| Neo4j Browser| http://localhost:7474       | neo4j / see .env     |
| MinIO Console| http://localhost:9001       | see .env             |
| MLflow UI    | http://localhost:5000       | —                    |
| Spark UI     | http://localhost:8080       | —                    |
| API Docs     | http://localhost:8000/docs  | Phase 6              |

## Architecture Phases

| Phase | Focus                        | Status     |
|-------|------------------------------|------------|
| 1     | Foundation & local dev       | ✅ Current |
| 2     | Data model (Neo4j + Postgres)| Pending    |
| 3     | Ingestion (Kafka + Spark)    | Pending    |
| 4     | Feature engineering          | Pending    |
| 5     | ML models                    | Pending    |
| 6     | Serving (FastAPI)            | Pending    |
| 7     | Security & compliance        | Pending    |
| 8     | Observability & MLOps        | Pending    |
| 9     | Kubernetes + Terraform       | Pending    |

## Development

```bash
make lint        # ruff linter
make fmt         # black + ruff --fix
make typecheck   # mypy
make test-unit   # fast tests, no services required
make test        # full suite (services must be up)
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch strategy and PR checklist.  
See [CLAUDE.md](CLAUDE.md) for AI-assisted development guidance.
