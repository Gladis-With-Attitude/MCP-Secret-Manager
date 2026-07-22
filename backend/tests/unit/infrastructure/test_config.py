from __future__ import annotations

import pytest

from infrastructure.config import AppSettings, ConfigurationError

VALID_DATABASE_URL = "postgresql+asyncpg://user:password@127.0.0.1:5432/app"
VALID_MASTER_KEY = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
VALID_SECRET_KEY = "a-production-secret-key-with-enough-length"  # noqa: S105


def test_development_configuration_is_valid_with_runtime_values() -> None:
    settings = AppSettings(
        environment="development",
        database_url=VALID_DATABASE_URL,
        master_key_base64=VALID_MASTER_KEY,
        bootstrap_admin_email="admin@example.local",
        bootstrap_admin_name="Administrator",
    )

    settings.validate_runtime()


def test_development_requires_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MCP_SECRET_MANAGER_DATABASE_URL", raising=False)
    settings = AppSettings(
        environment="development",
        master_key_base64=VALID_MASTER_KEY,
        bootstrap_admin_email="admin@example.local",
        bootstrap_admin_name="Administrator",
    )

    with pytest.raises(ConfigurationError, match="MCP_SECRET_MANAGER_DATABASE_URL"):
        settings.validate_runtime()


def test_development_requires_master_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MCP_SECRET_MANAGER_MASTER_KEY_BASE64", raising=False)
    settings = AppSettings(
        environment="development",
        database_url=VALID_DATABASE_URL,
        bootstrap_admin_email="admin@example.local",
        bootstrap_admin_name="Administrator",
    )

    with pytest.raises(ConfigurationError, match="MCP_SECRET_MANAGER_MASTER_KEY_BASE64"):
        settings.validate_runtime()


def test_test_environment_allows_missing_runtime_secrets() -> None:
    settings = AppSettings(
        environment="test",
        bootstrap_enabled=False,
    )

    settings.validate_runtime()


def test_invalid_database_driver_is_rejected() -> None:
    settings = AppSettings(
        environment="development",
        database_url="postgresql://user:password@127.0.0.1:5432/app",
        master_key_base64=VALID_MASTER_KEY,
        bootstrap_admin_email="admin@example.local",
        bootstrap_admin_name="Administrator",
    )

    with pytest.raises(ConfigurationError, match="postgresql\\+asyncpg"):
        settings.validate_runtime()


def test_invalid_master_key_length_is_rejected() -> None:
    settings = AppSettings(
        environment="development",
        database_url=VALID_DATABASE_URL,
        master_key_base64="c2hvcnQ=",
        bootstrap_admin_email="admin@example.local",
        bootstrap_admin_name="Administrator",
    )

    with pytest.raises(ConfigurationError, match="32 bytes"):
        settings.validate_runtime()


def test_production_requires_security_configuration() -> None:
    settings = AppSettings(
        environment="production",
        database_url=VALID_DATABASE_URL,
        master_key_base64=VALID_MASTER_KEY,
        secret_key="",
        bootstrap_admin_email="admin@example.local",
        bootstrap_admin_name="Administrator",
        cors_allowed_origins="https://app.example.com",
    )

    with pytest.raises(ConfigurationError) as exc_info:
        settings.validate_runtime()

    message = str(exc_info.value)
    assert "MCP_SECRET_MANAGER_SECRET_KEY" in message
    assert "MCP_SECRET_MANAGER_OPENAPI_ENABLED" in message
    assert "MCP_SECRET_MANAGER_TLS_REQUIRED" in message
    assert "MCP_SECRET_MANAGER_SECURE_COOKIES" in message


def test_production_configuration_is_valid_when_hardened() -> None:
    settings = AppSettings(
        environment="production",
        database_url=VALID_DATABASE_URL,
        master_key_base64=VALID_MASTER_KEY,
        secret_key=VALID_SECRET_KEY,
        tls_required=True,
        secure_cookies=True,
        allow_insecure_dev_defaults=False,
        openapi_enabled=False,
        cors_allowed_origins="https://app.example.com",
        bootstrap_admin_email="admin@example.local",
        bootstrap_admin_name="Administrator",
    )

    settings.validate_runtime()


def test_production_rejects_insecure_cors() -> None:
    settings = AppSettings(
        environment="production",
        database_url=VALID_DATABASE_URL,
        master_key_base64=VALID_MASTER_KEY,
        secret_key=VALID_SECRET_KEY,
        tls_required=True,
        secure_cookies=True,
        allow_insecure_dev_defaults=False,
        openapi_enabled=False,
        cors_allowed_origins="http://localhost:3000",
        bootstrap_admin_email="admin@example.local",
        bootstrap_admin_name="Administrator",
    )

    with pytest.raises(ConfigurationError, match="HTTPS origins"):
        settings.validate_runtime()


def test_bootstrap_requires_admin_identity_when_enabled() -> None:
    settings = AppSettings(
        environment="development",
        database_url=VALID_DATABASE_URL,
        master_key_base64=VALID_MASTER_KEY,
        bootstrap_admin_email="",
        bootstrap_admin_name="",
    )

    with pytest.raises(ConfigurationError, match="BOOTSTRAP_ADMIN_EMAIL"):
        settings.validate_runtime()


def test_safe_summary_does_not_expose_sensitive_values() -> None:
    settings = AppSettings(
        environment="production",
        database_url="postgresql+asyncpg://user:secret-password@db:5432/app",
        master_key_base64=VALID_MASTER_KEY,
        secret_key=VALID_SECRET_KEY,
        tls_required=True,
        secure_cookies=True,
        allow_insecure_dev_defaults=False,
        openapi_enabled=False,
        cors_allowed_origins="https://app.example.com",
        bootstrap_admin_email="admin@example.local",
        bootstrap_admin_name="Administrator",
        bootstrap_admin_api_key="mcp_sm_0123456789abcdef_" + ("a" * 64),
    )

    summary = str(settings.runtime_configuration().safe_summary())

    assert "secret-password" not in summary
    assert VALID_MASTER_KEY not in summary
    assert VALID_SECRET_KEY not in summary
    assert "mcp_sm_0123456789abcdef_" not in summary
