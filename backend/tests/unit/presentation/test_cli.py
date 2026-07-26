from __future__ import annotations

from pathlib import Path

import pytest

from infrastructure.config import ConfigurationError
from presentation.cli.main import (
    load_env_file,
    run,
    validate_deployment_environment,
)

VALID_DATABASE_URL = "postgresql+asyncpg://user:password@db.example.com:5432/app"
VALID_MASTER_KEY = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
VALID_SECRET_KEY = "a-production-secret-key-with-enough-length"  # noqa: S105


def valid_deployment_values() -> dict[str, str]:
    return {
        "MCP_SECRET_MANAGER_ENVIRONMENT": "production",
        "MCP_SECRET_MANAGER_SERVICE_NAME": "mcp-secret-manager",
        "MCP_SECRET_MANAGER_DEBUG": "false",
        "MCP_SECRET_MANAGER_LOG_LEVEL": "INFO",
        "MCP_SECRET_MANAGER_DATABASE_URL": VALID_DATABASE_URL,
        "MCP_SECRET_MANAGER_MASTER_KEY_BASE64": VALID_MASTER_KEY,
        "MCP_SECRET_MANAGER_MASTER_KEY_VERSION": "1",
        "MCP_SECRET_MANAGER_SECRET_KEY": VALID_SECRET_KEY,
        "MCP_SECRET_MANAGER_TLS_REQUIRED": "true",
        "MCP_SECRET_MANAGER_SECURE_COOKIES": "true",
        "MCP_SECRET_MANAGER_OPENAPI_ENABLED": "false",
        "MCP_SECRET_MANAGER_SECURITY_HEADERS_ENABLED": "true",
        "MCP_SECRET_MANAGER_RATE_LIMIT_ENABLED": "true",
        "MCP_SECRET_MANAGER_ALLOW_INSECURE_DEV_DEFAULTS": "false",
        "MCP_SECRET_MANAGER_CORS_ALLOWED_ORIGINS": "https://app.example.com",
        "MCP_SECRET_MANAGER_CORS_ALLOWED_METHODS": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
        "MCP_SECRET_MANAGER_CORS_ALLOWED_HEADERS": "Authorization,Content-Type,X-CSRF-Token",
        "MCP_SECRET_MANAGER_CORS_ALLOW_CREDENTIALS": "true",
        "MCP_SECRET_MANAGER_BOOTSTRAP_ENABLED": "true",
        "MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL": "admin@example.com",
        "MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME": "Administrator",
        "NEXT_PUBLIC_APP_ENV": "production",
        "NEXT_PUBLIC_API_BASE_URL": "https://api.example.com",
    }


def write_env_file(path: Path, values: dict[str, str]) -> None:
    path.write_text(
        "\n".join(f"{key}={value}" for key, value in values.items()) + "\n",
        encoding="utf-8",
    )


def test_validate_deployment_environment_accepts_hardened_values() -> None:
    configuration = validate_deployment_environment(valid_deployment_values())

    assert configuration.application.environment == "production"
    assert configuration.rest_api.security_headers.hsts_enabled is True


def test_validate_deployment_environment_rejects_unsafe_values() -> None:
    values = valid_deployment_values()
    values.update(
        {
            "MCP_SECRET_MANAGER_OPENAPI_ENABLED": "true",
            "MCP_SECRET_MANAGER_ALLOW_DB_RESET": "true",
            "NEXT_PUBLIC_API_BASE_URL": "http://127.0.0.1:8000",
        }
    )

    with pytest.raises(ConfigurationError) as exc_info:
        validate_deployment_environment(values)

    message = str(exc_info.value)
    assert "MCP_SECRET_MANAGER_OPENAPI_ENABLED" in message
    assert "MCP_SECRET_MANAGER_ALLOW_DB_RESET" in message
    assert "NEXT_PUBLIC_API_BASE_URL must use HTTPS" in message


def test_validate_deployment_environment_ignores_ambient_backend_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MCP_SECRET_MANAGER_DATABASE_URL", VALID_DATABASE_URL)
    values = valid_deployment_values()
    del values["MCP_SECRET_MANAGER_DATABASE_URL"]

    with pytest.raises(ConfigurationError, match="MCP_SECRET_MANAGER_DATABASE_URL"):
        validate_deployment_environment(values)


def test_load_env_file_supports_comments_exports_and_quoted_values(tmp_path: Path) -> None:
    env_file = tmp_path / "deployment.env"
    env_file.write_text(
        "\n".join(
            [
                "# deployment env",
                "export MCP_SECRET_MANAGER_ENVIRONMENT=production",
                "MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME='Operations Admin'",
                "NEXT_PUBLIC_API_BASE_URL=https://api.example.com # public endpoint",
            ]
        ),
        encoding="utf-8",
    )

    values = load_env_file(env_file)

    assert values["MCP_SECRET_MANAGER_ENVIRONMENT"] == "production"  # noqa: S105
    assert values["MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME"] == "Operations Admin"  # noqa: S105
    assert values["NEXT_PUBLIC_API_BASE_URL"] == "https://api.example.com"


def test_validate_env_command_prints_only_safe_summary(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    env_file = tmp_path / "deployment.env"
    write_env_file(env_file, valid_deployment_values())

    exit_code = run(["validate-env", "--env-file", str(env_file)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Deployment environment validation passed." in captured.out
    assert "secret-key" not in captured.out
    assert VALID_MASTER_KEY not in captured.out
    assert "password" not in captured.out


def test_validate_env_command_returns_failure_for_missing_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = run(["validate-env", "--env-file", str(tmp_path / "missing.env")])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Environment file does not exist" in captured.err
