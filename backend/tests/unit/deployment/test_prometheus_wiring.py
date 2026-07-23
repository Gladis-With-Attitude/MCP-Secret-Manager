from __future__ import annotations

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


def test_makefile_exposes_an_observability_profile_target() -> None:
    makefile = read_repository_file("Makefile")

    assert "up-observability:" in makefile
    assert "--profile observability up -d prometheus" in makefile
