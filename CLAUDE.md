# CLAUDE.md — AI Development Guide

> This file is loaded automatically by Claude Code in every session.
> Keep it current as the project evolves.

## Project Overview

Healthcare Hereditary Disease Prediction System: a production-grade platform
that stores patient + family-relationship graphs in Neo4j, clinical records in
PostgreSQL, and trains ML models (XGBoost + GNNs) to predict hereditary disease
risk. PHI compliance (HIPAA/GDPR) is non-negotiable at every layer.

## Tech Stack (pinned versions)

| Component          | Technology                        | Version  |
|--------------------|-----------------------------------|----------|
| Graph DB           | Neo4j                             | 5.x      |
| Relational DB      | PostgreSQL                        | 15+      |
| Data Lake          | MinIO + Delta Lake / Iceberg      | latest   |
| Streaming          | Apache Kafka (Confluent)          | 7.6      |
| Batch/Stream       | Apache Spark (PySpark)            | 3.5+     |
| Orchestration      | Apache Airflow                    | 2.9      |
| ML frameworks      | XGBoost, LightGBM, PyTorch Geo.   | latest   |
| Experiment track.  | MLflow                            | 2.x      |
| API                | FastAPI                           | 0.110+   |
| Python             | CPython                           | 3.11     |
| Container runtime  | Docker + Kubernetes               | —        |
| IaC                | Terraform                         | 1.7+     |

## Monorepo Layout

```
services/     Runtime microservices (FastAPI API, Kafka consumers)
pipelines/    Spark jobs (spark/) and Airflow DAGs (airflow/)
ml/           Feature definitions, training scripts, model configs
infra/        Dockerfiles (docker/), Compose files (compose/), Terraform (terraform/)
schemas/      Neo4j Cypher constraints, Postgres Alembic migrations, Avro schemas
libs/common/  Shared Python library: PHI redaction, structured logging, config
tests/        unit/ integration/ fixtures/
scripts/      Dev utilities: check-env.sh, seed, reset
docs/         decisions/ (ADRs), runbooks/
```

## Local Dev Quickstart

```bash
cp .env.example .env          # fill in secrets
make check-env                # validate required vars
make up                       # start Neo4j, Postgres, Kafka, Spark, MinIO, MLflow, Redis
make ps                       # verify all containers healthy
make test-unit                # run fast tests (no services needed)
```

## Coding Standards

- Python 3.11+, type hints on every function signature
- Pydantic v2 for all data contracts (request/response models, config)
- Ruff + Black for linting/formatting (line length 100)
- Mypy strict mode — no `Any` without justification
- Test coverage ≥ 85% on `libs/`, `services/`, `pipelines/`, `ml/`
- 12-factor app: all config via environment variables, never hardcoded
- Structured JSON logging via `libs/common/logging.py` — **never log PHI**
- Every public function/class needs a docstring (purpose, args, returns, raises)

See [CONTRIBUTING.md](CONTRIBUTING.md) for full PR checklist.

## Key Architectural Decisions

- [ADR-0001 — Tech Stack Selection](docs/decisions/0001-tech-stack.md)

## Domain Glossary

| Term                  | Definition |
|-----------------------|------------|
| PHI                   | Protected Health Information — any data that can identify a patient |
| FHIR                  | HL7 Fast Healthcare Interoperability Resources (R4) — data exchange standard |
| ICD-10                | International Classification of Diseases, 10th revision — diagnosis codes |
| SNOMED CT             | Systematized Nomenclature of Medicine — clinical terminology |
| RxNorm                | Normalized names for clinical drugs |
| LOINC                 | Logical Observation Identifiers Names and Codes — lab tests |
| Degree of relatedness | Genetic relatedness coefficient: 1st-degree=0.5, 2nd-degree=0.25, etc. |
| GNN                   | Graph Neural Network — model that operates on graph-structured data |
| GDS                   | Neo4j Graph Data Science library |
| GraphFrames           | Apache Spark library for graph processing |

## What NOT To Do

- **Never log PHI** — use `libs/common/phi.py:redact_phi()` before logging any patient data
- **Never hardcode secrets** — all credentials via `.env` (local) or Vault/KMS (prod)
- **Never commit `.env`** — it is gitignored; CI will fail on gitleaks detection
- **Never store PHI unencrypted at rest** — envelope encryption required (Phase 7)
- **Never use `SELECT *` or `MATCH (n)` without a LIMIT** in production queries
- **Never split train/test by row** — always split by patient ID to prevent leakage
- **Never mark a model as ready without calibration** — use Brier score + reliability diagrams

## Current Phase Status

- [x] Phase 1 — Foundation (monorepo, Docker Compose, CI skeleton)
- [x] Phase 2 — Data Model
- [x] Phase 3 — Ingestion
- [x] Phase 4 — Feature Engineering
- [x] Phase 5 — ML Models
- [x] Phase 6 — Serving
- [x] Phase 7 — Security & Compliance
- [x] Phase 8 — Observability & MLOps
- [x] Phase 9 — Deployment
