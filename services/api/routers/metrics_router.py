"""Prometheus scrape endpoint.

GET /metrics
    Returns current Prometheus metrics in the text exposition format.
    This endpoint is intentionally excluded from JWT authentication
    and audit logging — it exposes no PHI and must be scrapeable by
    Prometheus without credentials.

    The endpoint is hidden from the OpenAPI schema to avoid confusion.

Security note: in production the /metrics path should be firewalled
so only the Prometheus server can reach it (e.g., Kubernetes NetworkPolicy
or nginx ``allow`` directive).  The endpoint itself contains no PHI —
only aggregate counters and histograms.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["observability"])


@router.get(
    "/metrics",
    include_in_schema=False,
    response_class=PlainTextResponse,
    summary="Prometheus metrics scrape endpoint",
)
async def prometheus_metrics() -> PlainTextResponse:
    """Return all registered Prometheus metrics in text exposition format.

    Returns:
        Plain-text Prometheus metrics (``Content-Type: text/plain``).
        Returns an empty 200 response when ``prometheus_client`` is not
        installed, so the scrape job does not fail.
    """
    try:
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

        body = generate_latest()
        return PlainTextResponse(content=body.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        return PlainTextResponse(content="# prometheus_client not installed\n")
