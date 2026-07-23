from __future__ import annotations

import logging

import anyio
import pytest
from httpx import ASGITransport, AsyncClient, Response

from presentation.rest.app import create_app


async def fetch_health_response() -> Response:
    transport = ASGITransport(app=create_app(service_name="test-service"))

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get("/v1/health")


async def fetch_health_response_with_request_id(request_id: str) -> Response:
    transport = ASGITransport(app=create_app(service_name="test-service"))

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get("/v1/health", headers={"X-Request-ID": request_id})


async def fetch_metrics_after_health() -> Response:
    app = create_app(service_name="test-service")
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.get("/v1/health")
        return await client.get("/v1/metrics")


def test_health_endpoint_returns_minimal_liveness_payload() -> None:
    response = anyio.run(fetch_health_response)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "test-service",
        "api": "ok",
        "configuration": "ok",
        "database": "not_configured",
        "repositories": "not_configured",
        "use_cases": "not_configured",
    }
    assert response.headers["X-Request-ID"]


def test_rest_requests_echo_valid_request_id() -> None:
    response = anyio.run(fetch_health_response_with_request_id, "req-123")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"


def test_rest_requests_replace_invalid_request_id() -> None:
    response = anyio.run(fetch_health_response_with_request_id, "bad request id")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "bad request id"
    assert response.headers["X-Request-ID"]


def test_metrics_endpoint_exposes_request_counts() -> None:
    response = anyio.run(fetch_metrics_after_health)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert (
        'mcp_secret_manager_http_requests_total{method="GET",path="/v1/health",status="200"} 1'
        in response.text
    )
    assert "mcp_secret_manager_http_request_duration_seconds_count" in response.text


def test_request_logging_omits_sensitive_inputs(caplog: pytest.LogCaptureFixture) -> None:
    async def run() -> Response:
        transport = ASGITransport(app=create_app(service_name="test-service"))

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get(
                "/v1/health",
                headers={
                    "Authorization": "Bearer credential-material",
                    "X-Request-ID": "req-456",
                },
            )

    caplog.set_level(logging.INFO, logger="presentation.rest.observability")

    response = anyio.run(run)

    assert response.status_code == 503
    assert "credential-material" not in caplog.text
    assert any(
        getattr(record, "event_fields", {}).get("request_id") == "req-456"
        for record in caplog.records
    )
