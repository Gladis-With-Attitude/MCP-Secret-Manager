from __future__ import annotations

import logging

import anyio
import pytest
from httpx import ASGITransport, AsyncClient, Response

from infrastructure.configuration.models import (
    CorsConfig,
    OpenTelemetryConfig,
    SecurityHeadersConfig,
)
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


async def fetch_unknown_path_then_metrics() -> tuple[Response, Response]:
    app = create_app(service_name="test-service")
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        unknown_response = await client.get("/v1/unknown/prod-db-password")
        metrics_response = await client.get("/v1/metrics")
        return unknown_response, metrics_response


async def fetch_health_with_opentelemetry_enabled() -> Response:
    transport = ASGITransport(
        app=create_app(
            service_name="test-service",
            opentelemetry=OpenTelemetryConfig(
                traces_enabled=True,
                exporter_otlp_endpoint=None,
            ),
        )
    )

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get("/v1/health", headers={"X-Request-ID": "req-otel"})


async def fetch_health_with_hsts_enabled() -> Response:
    security_headers = SecurityHeadersConfig(
        enabled=True,
        hsts_enabled=True,
        content_security_policy="frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
        frame_options="DENY",
        content_type_options="nosniff",
        referrer_policy="no-referrer",
        permissions_policy="camera=(), microphone=(), geolocation=()",
        strict_transport_security="max-age=31536000; includeSubDomains",
    )
    transport = ASGITransport(
        app=create_app(service_name="test-service", security_headers=security_headers)
    )

    async with AsyncClient(transport=transport, base_url="https://testserver") as client:
        return await client.get("/v1/health")


async def fetch_configured_cors_responses() -> tuple[Response, Response]:
    cors = CorsConfig(
        allowed_origins=("https://app.example.com",),
        allowed_methods=("GET", "OPTIONS"),
        allowed_headers=("Authorization", "Content-Type"),
        allow_credentials=True,
    )
    transport = ASGITransport(app=create_app(service_name="test-service", cors=cors))

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        allowed_response = await client.options(
            "/v1/health",
            headers={
                "Origin": "https://app.example.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization",
            },
        )
        rejected_response = await client.options(
            "/v1/health",
            headers={
                "Origin": "https://evil.example.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization",
            },
        )
        return allowed_response, rejected_response


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


def test_rest_responses_include_baseline_security_headers() -> None:
    response = anyio.run(fetch_health_response)

    assert response.status_code == 200
    assert response.headers["Content-Security-Policy"] == (
        "frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
    )
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"
    assert "Strict-Transport-Security" not in response.headers


def test_strict_transport_security_is_enabled_for_tls_runtime() -> None:
    response = anyio.run(fetch_health_with_hsts_enabled)

    assert response.status_code == 200
    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"


def test_cors_uses_configured_origin_allow_list() -> None:
    allowed_response, rejected_response = anyio.run(fetch_configured_cors_responses)

    assert allowed_response.status_code == 200
    assert allowed_response.headers["Access-Control-Allow-Origin"] == "https://app.example.com"
    assert allowed_response.headers["Access-Control-Allow-Credentials"] == "true"
    assert rejected_response.status_code == 400
    assert "Access-Control-Allow-Origin" not in rejected_response.headers


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


def test_unknown_routes_use_safe_observability_path(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="presentation.rest.observability")

    unknown_response, metrics_response = anyio.run(fetch_unknown_path_then_metrics)

    assert unknown_response.status_code == 404
    assert (
        'mcp_secret_manager_http_requests_total{method="GET",path="unmatched_route",status="404"}'
        in metrics_response.text
    )
    observability_records = [
        record for record in caplog.records if record.name == "presentation.rest.observability"
    ]
    assert observability_records
    assert all("prod-db-password" not in record.getMessage() for record in observability_records)
    assert all(
        "prod-db-password" not in str(getattr(record, "event_fields", {}))
        for record in observability_records
    )
    assert "prod-db-password" not in metrics_response.text


def test_opentelemetry_can_be_enabled_without_changing_request_id_behavior() -> None:
    response = anyio.run(fetch_health_with_opentelemetry_enabled)

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-otel"


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
