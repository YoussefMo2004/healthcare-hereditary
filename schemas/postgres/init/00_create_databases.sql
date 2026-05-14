-- Runs once when the Postgres container first initialises.
-- Creates the separate MLflow tracking database so the app DB and MLflow
-- metadata do not share the same schema namespace.
-- The healthcare app DB itself is created by POSTGRES_DB env var automatically.

SELECT 'CREATE DATABASE mlflow'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'mlflow'
)\gexec

SELECT 'CREATE DATABASE airflow'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'airflow'
)\gexec

-- Grant the app user access to all databases.
GRANT ALL PRIVILEGES ON DATABASE mlflow TO :POSTGRES_USER;
GRANT ALL PRIVILEGES ON DATABASE airflow TO :POSTGRES_USER;
