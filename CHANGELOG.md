# Changelog

All notable changes to this project will be documented in this file.  
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [Unreleased]

## [0.1.0] — 2026-04-18

### Added
- Phase 1: monorepo directory structure
- Docker Compose for local dev (Neo4j, Postgres, Kafka, Spark, MinIO, MLflow, Redis)
- CI/CD skeleton (GitHub Actions: lint, test, build, security scan)
- Pre-commit hooks (ruff, black, mypy, gitleaks, hadolint)
- `libs/common`: PHI redaction, structured logging, environment config
- `scripts/check-env.sh`: required-variable validation
- `CLAUDE.md`, `CONTRIBUTING.md`, `DECISIONS.md`, ADR-0001
