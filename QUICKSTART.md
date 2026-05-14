# 🚀 Quick Start Guide — Complete System Setup

This guide walks you through setting up and running the complete Healthcare Hereditary Disease Prediction System with the Streamlit web interface.

**Estimated time: 15-20 minutes**

---

## Prerequisites

- **Docker Desktop** or **Docker Engine** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Python 3.11+** (for local development)
- **Git**
- **~8 GB free RAM** (recommended for running all services)
- **~20 GB free disk space** (for Docker images and volumes)

### Installation Check

```bash
# Verify Docker
docker --version
docker compose version

# Verify Python
python --version
```

---

## Step 1: Clone Repository & Setup Environment

```bash
# Navigate to project directory (replace with your path)
cd ~/projects/healthcare-hereditary

# Copy environment template
cp .env.example .env

# Edit .env and set required passwords (open with your editor)
# At minimum, change these values:
#   POSTGRES_PASSWORD=secure_password_here
#   NEO4J_PASSWORD=secure_password_here
#   MINIO_SECRET_KEY=secure_password_here
#   REDIS_PASSWORD=secure_password_here
#   APP_SECRET_KEY=your-secret-key-at-least-32-chars-long

# For development/testing, you can use simple values:
# ===== Quick Setup (Development Only) =====
cat > .env << 'EOF'
POSTGRES_PASSWORD=postgres
NEO4J_PASSWORD=neo4j
MINIO_SECRET_KEY=minioadmin
REDIS_PASSWORD=redis
APP_SECRET_KEY=development-secret-key-at-least-32-characters
STREAMLIT_PORT=8501
EOF
```

---

## Step 2: Validate Configuration

```bash
# Check that all required environment variables are set
make check-env
```

You should see a list of environment variables marked as `OK` (green) or `MISSING` (red).

---

## Step 3: Start All Services

```bash
# Option A: One-command startup with model training (RECOMMENDED)
make run-all

# This will:
# 1. Validate environment ✓
# 2. Start all Docker services ✓
# 3. Train an XGBoost model ✓
# 4. Launch Streamlit interface ✓
# 5. Display service URLs ✓
```

Or, if you prefer manual steps:

```bash
# Option B: Manual steps
make check-env        # Validate environment
make up               # Start Docker services
make sleep            # Wait for services to be healthy
make train-models     # Train XGBoost model
make streamlit-logs   # Follow Streamlit logs
```

---

## Step 4: Access the Web Interface

Once services are running, open your browser:

### 🎯 Main Interface
- **Streamlit Web App**: [http://localhost:8501](http://localhost:8501)
  - 📊 Dashboard: System overview & KPIs
  - 🔮 Risk Prediction: Patient-level hereditary disease risk scoring
  - 👨‍👩‍👧 Family Tree: Pedigree analysis & relationships
  - 🤖 Model Training: Train & evaluate ML models
  - 📈 Analytics: System monitoring & data quality

### 🔧 Admin Interfaces
- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474)
  - Login: `neo4j` / password in .env
  - Query family relationships and patient data with Cypher
  
- **MinIO Console**: [http://localhost:9001](http://localhost:9001)
  - Login: `minioadmin` / password in .env
  - Browse object storage buckets
  
- **MLflow Dashboard**: [http://localhost:5000](http://localhost:5000)
  - View model runs, experiments, and artifacts
  
- **Spark Master UI**: [http://localhost:8080](http://localhost:8080)
  - Monitor Spark jobs and resources
  
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Swagger UI for REST API endpoints

---

## Step 5: Try the System

### 🔮 Make Your First Risk Prediction

1. Navigate to **🔮 Risk Prediction** tab
2. Fill in patient information:
   - Age: 55
   - Gender: Male
   - Comorbidities: 3
   - Hereditary Conditions: 1
   - Closest Affected Relative: 1st degree
   - Family Risk Prevalence: 50%
3. Click **🔮 Predict Risk**
4. View risk score, category, and recommendations

### 🤖 Train a Model

1. Navigate to **🤖 Model Training** tab
2. Adjust XGBoost parameters (or use defaults)
3. Click **🚀 Train Model**
4. Monitor training progress
5. View performance metrics and ROC curve

### 👨‍👩‍👧 Explore Family Relationships

1. Navigate to **👨‍👩‍👧 Family Tree** tab
2. View sample family structure with disease annotations
3. Observe how genetic relationships influence risk

### 📊 View System Dashboard

1. Navigate to **📊 Dashboard** tab
2. See real-time KPIs:
   - Total patients
   - At-risk patients
   - Model accuracy
   - Prediction volume

---

## Useful Commands

```bash
# ── View Service Status ──
make ps                    # Show all running Docker containers

# ── View Logs ──
docker compose logs -f [service]    # Follow logs for a service
docker compose logs -f streamlit    # Streamlit logs
docker compose logs -f api          # API logs
docker compose logs -f postgres     # Database logs

# ── Stop Services ──
make down                  # Stop all services (keep volumes)
docker compose down -v     # Stop and remove volumes (clean slate)

# ── Development ──
make lint                  # Run linter (Ruff)
make fmt                   # Format code (Black + Ruff)
make typecheck             # Run type checker (Mypy)
make test-unit             # Run unit tests
make test-integration      # Run integration tests

# ── Database Management ──
make migrate               # Apply Postgres migrations
make migrate-down          # Rollback last migration
make migrate-history       # Show migration history

# ── Shell Access ──
make streamlit-shell       # Open shell in Streamlit container
docker compose exec api /bin/bash      # Access API container
docker compose exec postgres psql -U healthcare_app -d healthcare  # Connect to Postgres

# ── Rebuild Services ──
docker compose build streamlit         # Rebuild Streamlit image
docker compose build api               # Rebuild API image
docker compose up -d --build           # Rebuild and restart all

# ── Clean Up ──
make clean                 # Remove Python cache/artifacts
docker system prune -a     # Remove unused Docker images/containers
```

---

## Troubleshooting

### Problem: "Docker not found" or services won't start

**Solution:**
1. Install Docker Desktop: https://www.docker.com/products/docker-desktop
2. Or install Docker Engine: https://docs.docker.com/engine/install/
3. Verify installation: `docker --version && docker compose version`
4. Restart Docker daemon if needed

### Problem: Port conflicts (e.g., "Port 8501 already in use")

**Solution:**
```bash
# Option 1: Change port in .env
STREAMLIT_PORT=8502

# Option 2: Kill process using the port
lsof -ti:8501 | xargs kill -9  # macOS/Linux
Get-Process -Id (Get-NetTCPConnection -LocalPort 8501).OwningProcess | Stop-Process  # Windows
```

### Problem: Services are slow to start or timeout

**Solution:**
```bash
# Increase Docker resource allocation:
# 1. Open Docker Desktop
# 2. Go to Settings > Resources
# 3. Increase CPUs and Memory
# 4. Restart Docker

# Or manually wait longer:
sleep 30 && make streamlit-logs
```

### Problem: "POSTGRES_PASSWORD is required" error

**Solution:**
```bash
# .env file is missing or environment variable not set
cp .env.example .env
# Edit .env and set: POSTGRES_PASSWORD=your_password
make check-env  # Verify all variables
```

### Problem: Streamlit page won't load or shows errors

**Solution:**
```bash
# Check Streamlit logs
make streamlit-logs

# Restart Streamlit container
docker compose restart streamlit

# Or rebuild from scratch
docker compose down
docker compose up -d streamlit
```

### Problem: Neo4j/Postgres connection errors in API

**Solution:**
```bash
# Verify databases are healthy
docker compose exec postgres pg_isready
docker compose exec neo4j curl http://localhost:7474

# Check API logs
docker compose logs api

# Restart dependent services
docker compose restart postgres neo4j api
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Browser (Port 8501)                          │
│                  ┌──────────────────────┐                        │
│                  │   Streamlit Web UI   │                        │
│                  │  • Dashboard         │                        │
│                  │  • Predictions       │                        │
│                  │  • Model Training    │                        │
│                  └──────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI Service (Port 8000)                    │
│  • REST endpoints for predictions                               │
│  • FHIR-aligned data contracts                                  │
│  • Rate limiting & audit logging                                │
└─────────────────────────────────────────────────────────────────┘
                      ↙          ↓          ↘
         ┌────────────┴─────────┴─────────┬─────┐
         ↓            ↓          ↓         ↓     ↓
    ┌────────┐   ┌────────┐   ┌──────┐ ┌─────┐ ┌────┐
    │ Neo4j  │   │Postgres│   │MinIO │ │Redis│ │MLflow
    │ (Graph)│   │ (SQL)  │   │(S3)  │ │Cache│ │Model
    │        │   │        │   │      │ │     │ │Registry
    └────────┘   └────────┘   └──────┘ └─────┘ └────┘

Kafka (Event Stream) ← Patient Events ← Spark (Feature Engineering)
```

---

## Data Flow Example

```
1. Patient Information
   ↓
2. Ingestion (Kafka Topic: patient.created)
   ↓
3. Storage (PostgreSQL + Neo4j)
   ↓
4. Feature Engineering (Spark Job)
   ↓
5. Feature Materialization (Delta Lake / MinIO)
   ↓
6. ML Training (XGBoost + GNN via MLflow)
   ↓
7. Model Serving (FastAPI + Redis Cache)
   ↓
8. User Interface (Streamlit)
   ↓
9. Prediction Result with Explainability
```

---

## Next Steps

After the system is running:

1. **Explore Sample Predictions**
   - Try the 🔮 Risk Prediction tab with different patient profiles
   - Observe how family history affects risk scoring

2. **Train Custom Models**
   - Adjust XGBoost hyperparameters in 🤖 Model Training
   - Train models and compare metrics

3. **Inspect Raw Data**
   - Open Neo4j Browser: http://localhost:7474
   - Run Cypher queries to explore family relationships
   - Example: `MATCH (p:Patient)-[:HAS_DIAGNOSIS]->(d:Diagnosis) RETURN p, d LIMIT 10`

4. **View Model Artifacts**
   - Open MLflow Dashboard: http://localhost:5000
   - Inspect trained model runs and parameters
   - Download model artifacts

5. **Read the Code**
   - `services/streamlit/app.py` — Streamlit interface
   - `services/api/main.py` — API service
   - `ml/training/train_xgboost.py` — Model training
   - `libs/common/` — Shared utilities (logging, config, PHI redaction)

---

## Development Workflow

```bash
# 1. Make code changes
edit services/streamlit/app.py

# 2. Rebuild Docker image
docker compose build streamlit

# 3. Restart service
docker compose restart streamlit

# 4. View changes
# Navigate to http://localhost:8501 and refresh
```

---

## Support & Documentation

- **Project Overview**: See [README.md](README.md)
- **Architecture Decisions**: See [docs/decisions/0001-tech-stack.md](docs/decisions/0001-tech-stack.md)
- **Contributing Guide**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Full Audit Report**: See [PROJECT_AUDIT.md](PROJECT_AUDIT.md)
- **AI Development Guide**: See [CLAUDE.md](CLAUDE.md)

---

## Summary

You now have a **complete, production-grade healthcare data platform** with:

✅ Docker Compose for local development
✅ Neo4j + PostgreSQL for data storage
✅ Kafka for event ingestion
✅ Spark for batch processing
✅ XGBoost + GNN for ML models
✅ MLflow for model management
✅ **Streamlit web interface for risk predictions**
✅ FastAPI REST service
✅ Redis caching
✅ Comprehensive logging & monitoring

**Phase 1 is complete. Phases 2-9 roadmap in PROJECT_AUDIT.md.**

Happy predicting! 🎯
