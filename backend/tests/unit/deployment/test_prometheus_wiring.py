from __future__ import annotations

import json
from pathlib import Path

import pytest


def find_repository_root() -> Path | None:
    for parent in Path(__file__).resolve().parents:
        if (parent / "docker-compose.yml").is_file():
            return parent
    return None


def read_repository_file(relative_path: str) -> str:
    repository_root = find_repository_root()
    if repository_root is None:
        pytest.skip("repository-level deployment files are not mounted in this test environment")
    return (repository_root / relative_path).read_text(encoding="utf-8")


def test_prometheus_scrapes_the_rest_metrics_endpoint() -> None:
    config = read_repository_file("monitoring/prometheus/prometheus.yml")

    assert "job_name: mcp-secret-manager-rest" in config
    assert "metrics_path: /v1/metrics" in config
    assert "scheme: http" in config
    assert "backend:8000" in config
    assert "service: mcp-secret-manager" in config


def test_compose_prometheus_service_is_opt_in_and_local_only() -> None:
    compose = read_repository_file("docker-compose.yml")

    assert "prometheus:" in compose
    assert "- observability" in compose
    assert "./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro" in compose
    assert '"127.0.0.1:${PROMETHEUS_PORT:-9090}:9090"' in compose


def test_grafana_provisions_prometheus_datasource() -> None:
    datasource = read_repository_file("monitoring/grafana/provisioning/datasources/prometheus.yml")

    assert "name: Prometheus" in datasource
    assert "uid: prometheus" in datasource
    assert "type: prometheus" in datasource
    assert "url: http://prometheus:9090" in datasource
    assert "isDefault: true" in datasource
    assert "editable: false" in datasource


def test_grafana_provisions_dashboard_files() -> None:
    provider = read_repository_file("monitoring/grafana/provisioning/dashboards/dashboards.yml")

    assert "name: mcp-secret-manager" in provider
    assert "folder: Secret Manager" in provider
    assert "editable: false" in provider
    assert "path: /etc/grafana/dashboards" in provider


def test_grafana_dashboard_uses_safe_aggregate_metrics() -> None:
    dashboard = json.loads(
        read_repository_file("monitoring/grafana/dashboards/secret-manager-overview.json")
    )

    assert dashboard["title"] == "MCP Secret Manager Overview"
    assert dashboard["uid"] == "mcp-secret-manager-overview"
    assert dashboard["editable"] is False

    panels = dashboard["panels"]
    assert len(panels) >= 6

    expressions = [
        target["expr"]
        for panel in panels
        for target in panel.get("targets", [])
        if "expr" in target
    ]
    assert expressions
    assert all("mcp_secret_manager_http_" in expression for expression in expressions)
    assert any("mcp_secret_manager_http_requests_total" in expression for expression in expressions)
    assert any(
        "mcp_secret_manager_http_request_duration_seconds" in expression
        for expression in expressions
    )

    serialized_dashboard = json.dumps(dashboard).lower()
    forbidden_terms = (
        "authorization",
        "api_key",
        "password",
        "secret_value",
        "token",
    )
    assert all(term not in serialized_dashboard for term in forbidden_terms)


def test_compose_grafana_service_is_opt_in_local_only_and_provisioned() -> None:
    compose = read_repository_file("docker-compose.yml")

    assert "grafana:" in compose
    assert "${GRAFANA_IMAGE:-grafana/grafana-oss:latest}" in compose
    assert '"127.0.0.1:${GRAFANA_PORT:-3001}:3000"' in compose
    assert "./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro" in compose
    assert "./monitoring/grafana/dashboards:/etc/grafana/dashboards:ro" in compose
    assert "GF_AUTH_ANONYMOUS_ORG_ROLE: Viewer" in compose
    assert "GF_SECURITY_DISABLE_INITIAL_ADMIN_CREATION" in compose


def test_makefile_exposes_an_observability_profile_target() -> None:
    makefile = read_repository_file("Makefile")

    assert "up-observability:" in makefile
    assert "--profile observability up -d prometheus grafana" in makefile
