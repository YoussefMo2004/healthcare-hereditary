#!/usr/bin/env bash
# Validates that all required environment variables are set before starting
# services. Called by `make check-env` and `make up`.
# Exits 1 if any required variable is missing or empty.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Colour

MISSING=0

check_var() {
    local var_name="$1"
    local value="${!var_name:-}"
    if [[ -z "$value" ]]; then
        echo -e "${RED}  MISSING${NC}  ${var_name}"
        MISSING=$((MISSING + 1))
    else
        # Never print the value — it may be a secret
        echo -e "${GREEN}  OK     ${NC}  ${var_name}"
    fi
}

warn_default() {
    local var_name="$1"
    local unsafe_value="$2"
    local current="${!var_name:-}"
    if [[ "$current" == "$unsafe_value" ]]; then
        echo -e "${YELLOW}  WARN   ${NC}  ${var_name} is set to the default placeholder '${unsafe_value}' — change before production use"
    fi
}

echo ""
echo "Checking required environment variables..."
echo "────────────────────────────────────────────"

# Load .env if it exists and hasn't been sourced yet
if [[ -f ".env" ]]; then
    # Export vars from .env without executing arbitrary code
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
elif [[ -f "$(dirname "$0")/../.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$(dirname "$0")/../.env"
    set +a
fi

# ── PostgreSQL ────────────────────────────────────────────────────────────────
check_var "POSTGRES_PASSWORD"
check_var "POSTGRES_DB"
check_var "POSTGRES_USER"

# ── Neo4j ─────────────────────────────────────────────────────────────────────
check_var "NEO4J_PASSWORD"

# ── MinIO ─────────────────────────────────────────────────────────────────────
check_var "MINIO_SECRET_KEY"

# ── Redis ─────────────────────────────────────────────────────────────────────
check_var "REDIS_PASSWORD"

# ── Application ───────────────────────────────────────────────────────────────
check_var "APP_SECRET_KEY"

# ── Airflow (only checked when orchestration profile is active) ───────────────
if [[ "${COMPOSE_PROFILES:-}" == *"orchestration"* ]]; then
  check_var "AIRFLOW_FERNET_KEY"
  check_var "AIRFLOW_ADMIN_PASSWORD"
  check_var "AIRFLOW_SECRET_KEY"
fi

# ── Warn about unsafe placeholder values ─────────────────────────────────────
echo ""
echo "Checking for unsafe placeholder values..."
echo "────────────────────────────────────────────"
warn_default "POSTGRES_PASSWORD" "change_me_postgres"
warn_default "NEO4J_PASSWORD"    "change_me_neo4j"
warn_default "MINIO_SECRET_KEY"  "change_me_minio"
warn_default "REDIS_PASSWORD"    "change_me_redis"
warn_default "APP_SECRET_KEY"    "change_me_app_secret_32chars_min"

echo ""
echo "────────────────────────────────────────────"
if [[ $MISSING -gt 0 ]]; then
    echo -e "${RED}ERROR: ${MISSING} required variable(s) are missing.${NC}"
    echo "Copy .env.example to .env and fill in all required values."
    exit 1
else
    echo -e "${GREEN}All required environment variables are set.${NC}"
fi
echo ""
