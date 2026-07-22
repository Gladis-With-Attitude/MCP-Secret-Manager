from __future__ import annotations

from application.health import get_liveness_status


def test_liveness_status_is_minimal() -> None:
    status = get_liveness_status("test-service")

    assert status.as_public_dict() == {
        "status": "ok",
        "service": "test-service",
        "api": "ok",
        "configuration": "ok",
        "database": "not_configured",
        "repositories": "not_configured",
        "use_cases": "not_configured",
    }


def test_liveness_status_does_not_expose_sensitive_fields() -> None:
    status = get_liveness_status("test-service")

    assert set(status.as_public_dict()) == {
        "api",
        "configuration",
        "database",
        "repositories",
        "service",
        "status",
        "use_cases",
    }
