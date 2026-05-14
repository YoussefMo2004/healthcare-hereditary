"""Shared fixtures for live integration tests.

These tests exercise the stack through its network endpoints, so they are
intended to run only after Docker Compose has started the services.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import pytest
import requests


@dataclass(frozen=True)
class LiveServiceEndpoints:
    """Resolved base URLs for locally running services."""

    api_base_url: str = os.environ.get("API_BASE_URL", "http://localhost:8000")
    mlflow_base_url: str = os.environ.get("MLFLOW_BASE_URL", "http://localhost:5000")
    neo4j_browser_url: str = os.environ.get("NEO4J_BROWSER_URL", "http://localhost:7474")
    redis_host: str = os.environ.get("REDIS_HOST", "localhost")
    redis_port: int = int(os.environ.get("REDIS_PORT", "6379"))


@pytest.fixture(scope="session")
def live_endpoints() -> LiveServiceEndpoints:
    """Return the configured local service endpoints."""
    return LiveServiceEndpoints()


def _http_get(url: str, timeout: float = 10.0) -> requests.Response:
    """Perform an HTTP GET with a deterministic timeout."""
    return requests.get(url, timeout=timeout)


def pytest_configure(config: pytest.Config) -> None:
    """Register the integration marker for pytest."""
    config.addinivalue_line(
        "markers",
        "integration: live-service integration tests that require Docker Compose",
    )
