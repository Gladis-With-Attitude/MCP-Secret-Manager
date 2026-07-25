from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RuntimeEnvironment = Literal["development", "test", "staging", "production"]


@dataclass(frozen=True, slots=True)
class ApplicationConfig:
    environment: RuntimeEnvironment
    service_name: str
    debug: bool


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    url: str | None
    alembic_config: str | None
    migration_wait_timeout_seconds: int
    migration_lock_timeout_seconds: int


@dataclass(frozen=True, slots=True)
class SecurityConfig:
    secret_key_configured: bool
    secret_key_min_length: int
    tls_required: bool
    secure_cookies: bool
    allow_insecure_dev_defaults: bool


@dataclass(frozen=True, slots=True)
class AuthenticationConfig:
    bootstrap_admin_email: str | None
    bootstrap_admin_password_configured: bool
    bootstrap_admin_api_key_configured: bool


@dataclass(frozen=True, slots=True)
class CryptographyConfig:
    master_key_configured: bool
    master_key_version: int
    master_key_bytes: int | None


@dataclass(frozen=True, slots=True)
class CorsConfig:
    allowed_origins: tuple[str, ...]
    allowed_methods: tuple[str, ...]
    allowed_headers: tuple[str, ...]
    allow_credentials: bool


@dataclass(frozen=True, slots=True)
class RestApiConfig:
    host: str
    port: int
    openapi_enabled: bool
    cors: CorsConfig


@dataclass(frozen=True, slots=True)
class McpConfig:
    enabled: bool


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    level: str
    json_enabled: bool


@dataclass(frozen=True, slots=True)
class OpenTelemetryConfig:
    traces_enabled: bool
    exporter_otlp_endpoint: str | None


@dataclass(frozen=True, slots=True)
class DockerConfig:
    enabled: bool


@dataclass(frozen=True, slots=True)
class DevelopmentConfig:
    reset_enabled: bool
    test_database_url_configured: bool


@dataclass(frozen=True, slots=True)
class BootstrapConfig:
    enabled: bool
    admin_email: str | None
    admin_name: str | None
    admin_password_configured: bool
    admin_api_key_configured: bool
    service_account_enabled: bool
    service_account_project_id_configured: bool
    service_account_name_configured: bool
    service_account_api_key_configured: bool


@dataclass(frozen=True, slots=True)
class RuntimeConfiguration:
    application: ApplicationConfig
    database: DatabaseConfig
    security: SecurityConfig
    authentication: AuthenticationConfig
    cryptography: CryptographyConfig
    rest_api: RestApiConfig
    mcp: McpConfig
    logging: LoggingConfig
    opentelemetry: OpenTelemetryConfig
    docker: DockerConfig
    development: DevelopmentConfig
    bootstrap: BootstrapConfig

    def safe_summary(self) -> dict[str, object]:
        return {
            "application": {
                "environment": self.application.environment,
                "service_name": self.application.service_name,
                "debug": self.application.debug,
            },
            "database": {
                "configured": self.database.url is not None,
                "alembic_config": self.database.alembic_config,
                "migration_wait_timeout_seconds": self.database.migration_wait_timeout_seconds,
                "migration_lock_timeout_seconds": self.database.migration_lock_timeout_seconds,
            },
            "security": {
                "secret_key_configured": self.security.secret_key_configured,
                "tls_required": self.security.tls_required,
                "secure_cookies": self.security.secure_cookies,
            },
            "cryptography": {
                "master_key_configured": self.cryptography.master_key_configured,
                "master_key_version": self.cryptography.master_key_version,
                "master_key_bytes": self.cryptography.master_key_bytes,
            },
            "rest_api": {
                "host": self.rest_api.host,
                "port": self.rest_api.port,
                "openapi_enabled": self.rest_api.openapi_enabled,
                "cors_origins_count": len(self.rest_api.cors.allowed_origins),
                "cors_allow_credentials": self.rest_api.cors.allow_credentials,
            },
            "mcp": {"enabled": self.mcp.enabled},
            "logging": {
                "level": self.logging.level,
                "json_enabled": self.logging.json_enabled,
            },
            "opentelemetry": {
                "traces_enabled": self.opentelemetry.traces_enabled,
                "exporter_otlp_endpoint_configured": (
                    self.opentelemetry.exporter_otlp_endpoint is not None
                ),
            },
            "docker": {"enabled": self.docker.enabled},
            "development": {
                "reset_enabled": self.development.reset_enabled,
                "test_database_url_configured": self.development.test_database_url_configured,
            },
            "bootstrap": {
                "enabled": self.bootstrap.enabled,
                "admin_email": self.bootstrap.admin_email,
                "admin_name": self.bootstrap.admin_name,
                "admin_password_configured": self.bootstrap.admin_password_configured,
                "admin_api_key_configured": self.bootstrap.admin_api_key_configured,
                "service_account_enabled": self.bootstrap.service_account_enabled,
            },
        }
