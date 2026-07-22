from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(RuntimeError):
    """Raised when runtime configuration is unsafe or incomplete."""


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="MCP_SECRET_MANAGER_",
        extra="ignore",
    )

    environment: Literal["local", "test", "production"] = "local"
    service_name: str = "mcp-secret-manager"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: str | None = None
    master_key_base64: str | None = None
    master_key_version: int = Field(default=1, ge=1)
    rest_host: str = "127.0.0.1"
    rest_port: int = Field(default=8000, ge=1, le=65535)
    openapi_enabled: bool = True
    audit_retention_days: int = Field(default=365, ge=1)
    bootstrap_enabled: bool = True
    bootstrap_admin_email: str | None = None
    bootstrap_admin_name: str | None = None
    bootstrap_admin_password: str | None = None
    bootstrap_admin_api_key: str | None = None
    bootstrap_service_account_enabled: bool = False
    bootstrap_service_account_project_id: str | None = None
    bootstrap_service_account_name: str | None = None
    bootstrap_service_account_api_key: str | None = None

    def validate_runtime(self) -> None:
        if self.environment != "production":
            return

        missing: list[str] = []
        if self.database_url is None:
            missing.append("MCP_SECRET_MANAGER_DATABASE_URL")
        if self.master_key_base64 is None:
            missing.append("MCP_SECRET_MANAGER_MASTER_KEY_BASE64")

        if missing:
            joined = ", ".join(missing)
            msg = f"Production configuration is incomplete: {joined}."
            raise ConfigurationError(msg)


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
