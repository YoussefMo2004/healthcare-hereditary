# ADR-0001 — Tech Stack Selection

**Date:** 2026-04-18  
**Status:** Accepted  
**Deciders:** Engineering team

---

## Context

We are building a greenfield healthcare platform that must:
1. Model complex family relationship graphs for hereditary disease prediction.
2. Store FHIR-aligned clinical records with ACID guarantees.
3. Ingest real-time events (new diagnoses, prescriptions) at low latency.
4. Train and serve ML models (both tabular and graph-based).
5. Meet HIPAA/GDPR compliance requirements for PHI handling.

## Decision Drivers

- **Graph traversal performance**: family disease propagation requires multi-hop
  queries that are impractical in relational DBs.
- **FHIR alignment**: the relational store must map cleanly to HL7 FHIR R4.
- **ML pipeline maturity**: the ecosystem around training, tracking, and serving
  must be well-established and self-hostable.
- **Team expertise**: preference for Python-native tooling.
- **Compliance**: all data stores must support encryption at rest, audit logging,
  and field-level access control.

## Decision

| Concern              | Technology                              | Justification |
|----------------------|-----------------------------------------|---------------|
| Graph DB             | Neo4j 5.x + APOC + GDS                 | Native Cypher, GDS library for graph ML features, mature APOC procedures |
| Relational DB        | PostgreSQL 15+                          | Row-level security, logical replication, JSONB for FHIR resources |
| Object storage       | MinIO (local) / S3 (prod)               | S3-compatible API works with Delta Lake, MLflow, and all AWS tooling |
| Stream ingestion      | Apache Kafka (Confluent CP 7.6)         | De-facto standard, Schema Registry for Avro contracts |
| Batch/stream processing | Apache Spark 3.5 + PySpark + GraphFrames | Unified batch+stream, GraphFrames for graph feature extraction at scale |
| Orchestration        | Apache Airflow 2.9                      | Mature DAG-based scheduler, native Spark/Kafka operators |
| ML tracking          | MLflow 2.x                              | Model registry, artifact storage, supports all target frameworks |
| ML frameworks        | XGBoost, LightGBM, PyTorch Geometric    | Tabular baseline + GNN for graph-based risk scoring |
| Model serving        | FastAPI + BentoML                       | FastAPI for FHIR-compatible REST; BentoML for model packaging |
| Secrets              | `.env` (local) / HashiCorp Vault (prod) | 12-factor local dev; Vault for dynamic secrets in prod (Phase 7) |
| Auth                 | OAuth2/OIDC + mTLS                      | Industry standard; mTLS for service-to-service trust |
| IaC                  | Terraform 1.7+                          | Multi-cloud provider support, mature state management |
| Container platform   | Docker + Kubernetes                     | Docker Compose for local dev; K8s for staging/prod |
| Monitoring           | Prometheus + Grafana + Evidently AI     | Standard observability stack + ML-specific drift detection |
| Python version       | 3.11                                    | Stable PySpark support; 3.12 has rough edges with PySpark 3.5 |

## Consequences

### Positive

- Neo4j GDS eliminates bespoke graph feature code for Phase 4.
- Confluent Schema Registry enforces message contracts across all Kafka topics.
- MLflow's model registry gives Phase 5 a first-class promotion workflow.
- Terraform + K8s Helm charts make Phase 9 portable across cloud providers.

### Negative / Trade-offs

- Running all services locally requires ≥16 GB RAM (Neo4j + Spark are memory-hungry).
- Two separate databases (Neo4j + Postgres) means dual write paths must stay in sync.
- PyTorch Geometric dependency graph adds ~2 GB to training container images.

### Risks

- **Neo4j licence**: Community edition is used locally; production may require
  Enterprise for RBAC + cluster features. Revisit in Phase 7.
- **Spark ↔ Neo4j connector**: `neo4j-spark-connector` version compatibility must
  be pinned carefully — check against Neo4j 5.x and Spark 3.5 matrix.
- **PySpark 3.12 readiness**: monitor upstream for 3.12 support; upgrade path is
  straightforward once confirmed.

## Compliance Notes

- PostgreSQL row-level security will enforce patient-scoped data access (Phase 7).
- Neo4j Enterprise RBAC required for production PHI access controls.
- All S3/MinIO buckets must have server-side encryption enabled before storing PHI.
- Kafka topics containing PHI must use TLS + at-rest encryption (Phase 7).
