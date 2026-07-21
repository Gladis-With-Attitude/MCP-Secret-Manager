from __future__ import annotations

import pytest

from infrastructure.config import AppSettings, ConfigurationError


def test_local_configuration_can_start_without_sensitive_values() -> None:
    settings = AppSettings(environment="local")

    settings.validate_runtime()


def test_production_requires_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MCP_SECRET_MANAGER_DATABASE_URL", raising=False)
    settings = AppSettings(
        environment="production",
        master_key_base64="placeholder",
    )

    with pytest.raises(ConfigurationError, match="MCP_SECRET_MANAGER_DATABASE_URL"):
        settings.validate_runtime()


def test_production_requires_master_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MCP_SECRET_MANAGER_MASTER_KEY_BASE64", raising=False)
    settings = AppSettings(
        environment="production",
        database_url="postgresql+asyncpg://user:password@127.0.0.1:5432/app",
    )

    with pytest.raises(ConfigurationError, match="MCP_SECRET_MANAGER_MASTER_KEY_BASE64"):
        settings.validate_runtime()
