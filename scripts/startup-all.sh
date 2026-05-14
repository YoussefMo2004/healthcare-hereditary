#!/usr/bin/env bash
# Healthcare system startup script — initializes and runs all services

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Healthcare Hereditary Disease Prediction System              ║${NC}"
echo -e "${BLUE}║  Startup Script — All Services                               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Validate environment
echo -e "${YELLOW}[1/5] Validating environment variables...${NC}"
if ! bash scripts/check-env.sh; then
    echo -e "${RED}❌ Environment validation failed. Please check .env file.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Environment variables validated${NC}"
echo ""

# Step 2: Install dependencies
echo -e "${YELLOW}[2/5] Installing Python dependencies...${NC}"
if command -v pip &> /dev/null; then
    pip install --upgrade pip setuptools wheel
    pip install -e .
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ pip not found, skipping dependency installation${NC}"
fi
echo ""

# Step 3: Start Docker services
echo -e "${YELLOW}[3/5] Starting Docker Compose services...${NC}"
if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose -f infra/compose/docker-compose.yml -f infra/compose/docker-compose.override.yml up -d
    elif command -v docker-compose &> /dev/null; then
        docker-compose -f infra/compose/docker-compose.yml -f infra/compose/docker-compose.override.yml up -d
    fi
    echo -e "${GREEN}✅ Docker services started${NC}"
    echo ""
    
    # Wait for services to be healthy
    echo -e "${YELLOW}[4/5] Waiting for services to become healthy...${NC}"
    MAX_RETRIES=60
    RETRY=0
    
    while [ $RETRY -lt $MAX_RETRIES ]; do
        if docker compose -f infra/compose/docker-compose.yml exec -T postgres pg_isready -U healthcare_app &> /dev/null && \
           docker compose -f infra/compose/docker-compose.yml exec -T neo4j curl -s http://localhost:7474 &> /dev/null && \
           docker compose -f infra/compose/docker-compose.yml exec -T mlflow curl -s http://localhost:5000/health &> /dev/null; then
            echo -e "${GREEN}✅ All services healthy${NC}"
            break
        fi
        RETRY=$((RETRY + 1))
        echo -n "."
        sleep 1
    done
    
    if [ $RETRY -eq $MAX_RETRIES ]; then
        echo -e "${YELLOW}⚠ Services slow to start, proceeding anyway${NC}"
    fi
else
    echo -e "${RED}❌ Docker not found. Please install Docker Desktop or Docker Engine.${NC}"
    exit 1
fi
echo ""

# Step 5: Display service URLs
echo -e "${YELLOW}[5/5] Services ready!${NC}"
echo ""
echo -e "${GREEN}✅ System fully initialized${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Service URLs:${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${GREEN}🏥 Streamlit UI${NC}           http://localhost:8501"
echo -e "  ${GREEN}📊 Neo4j Browser${NC}          http://localhost:7474       (neo4j / see .env)"
echo -e "  ${GREEN}⚙️  API Documentation${NC}     http://localhost:8000/docs"
echo -e "  ${GREEN}📈 MLflow Dashboard${NC}       http://localhost:5000"
echo -e "  ${GREEN}🪣 MinIO Console${NC}          http://localhost:9001       (minioadmin / see .env)"
echo -e "  ${GREEN}⚡ Spark Master${NC}           http://localhost:8080"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Open ${GREEN}http://localhost:8501${NC} in your browser for the Streamlit interface"
echo "  2. Navigate to 'Risk Prediction' tab to predict hereditary disease risk"
echo "  3. Visit 'Model Training' to train new models"
echo "  4. Check 'Dashboard' for system overview"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  - View logs:              docker compose logs -f [service]"
echo "  - Stop services:          docker compose down"
echo "  - Reset data:             docker compose down -v && docker volume prune"
echo "  - Check service status:   make ps"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
