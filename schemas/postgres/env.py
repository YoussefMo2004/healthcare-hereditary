"""Alembic migration environment.

Uses synchronous SQLAlchemy engine so migrations can run from the CLI without
an async event loop.  Application code uses async SQLAlchemy separately.

The DSN is read from the ``POSTGRES_*`` environment variables (or .env file)
via the project's ``libs.common.config`` module — the same config used by
every other service.  This ensures migrations always target the same database
as the running application.
"""

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# ── Ensure project root is on sys.path ────────────────────────────────────────
# Allows `from libs.common...` imports to resolve when running:
#   alembic -c schemas/postgres/alembic.ini upgrade head
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ── Import metadata from all models ──────────────────────────────────────────
# All models must be imported before target_metadata is set so that
# autogenerate can detect new/modified tables.
from libs.common.models import Base  # noqa: E402 — must be after sys.path fix

# ── Alembic config object ─────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_dsn() -> str:
    """Build the synchronous DSN from environment variables.

    Returns:
        PostgreSQL DSN string suitable for ``engine_from_config``.

    Raises:
        RuntimeError: If ``POSTGRES_PASSWORD`` is not set.
    """
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "healthcare")
    user = os.environ.get("POSTGRES_USER", "healthcare_app")
    password = os.environ.get("POSTGRES_PASSWORD", "")

    if not password:
        raise RuntimeError(
            "POSTGRES_PASSWORD environment variable is required for Alembic migrations. "
            "Run `make check-env` to diagnose."
        )

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — generate SQL without a live connection.

    Useful for generating migration scripts to review before applying.
    Run: alembic -c schemas/postgres/alembic.ini upgrade head --sql
    """
    url = _get_dsn()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode — apply directly to the database."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _get_dsn()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # no connection pooling for migrations
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Include schema-level objects (e.g., enum types) in autogenerate.
            include_schemas=False,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
