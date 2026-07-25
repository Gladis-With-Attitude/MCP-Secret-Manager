from __future__ import annotations

import base64
import binascii
import logging
import os
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

from infrastructure.configuration.models import (
    ApplicationConfig,
    AuthenticationConfig,
    BootstrapConfig,
    CorsConfig,
    CryptographyConfig,
    DatabaseConfig,
    DevelopmentConfig,
    DockerConfig,
    LoggingConfig,
    McpConfig,
    OpenTelemetryConfig,
    RestApiConfig,
    RuntimeConfiguration,
    RuntimeEnvironment,
    SecurityConfig,
    SecurityHeadersConfig,
)
from infrastructure.logging import safe_log_extra

logger = logging.getLogger(__name__)

SECRET_KEY_MIN_LENGTH = 32
MASTER_KEY_BYTES = 32
DEFAULT_CONTENT_SECURITY_POLICY = "frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
DEFAULT_PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=()"
DEFAULT_STRICT_TRANSPORT_SECURITY = "max-age=31536000; includeSubDomains"


class ConfigurationError(RuntimeError):
    """Raised when runtime configuration is unsafe or incomplete."""


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="MCP_SECRET_MANAGER_",
        extra="ignore",
    )

    environment: RuntimeEnvironment = "development"
    service_name: str = Field(default="mcp-secret-manager", min_length=1)
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_json: bool = False
    otel_traces_enabled: bool = False
    otel_exporter_otlp_endpoint: str | None = None

    database_url: str | None = None
    alembic_config: str | None = None
    migration_wait_timeout_seconds: int = Field(default=60, ge=1)
    migration_lock_timeout_seconds: int = Field(default=300, ge=1)

    secret_key: str | None = None
    tls_required: bool = False
    secure_cookies: bool = False
    security_headers_enabled: bool = True
    allow_insecure_dev_defaults: bool = True

    master_key_base64: str | None = None
    master_key_version: int = Field(default=1, ge=1)

    rest_host: str = "127.0.0.1"
    rest_port: int = Field(default=8000, ge=1, le=65535)
    openapi_enabled: bool = True

    cors_allowed_origins: str = "http://127.0.0.1:3000,http://localhost:3000"
    cors_allowed_methods: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
    cors_allowed_headers: str = "Authorization,Content-Type"
    cors_allow_credentials: bool = True

    mcp_enabled: bool = True
    docker_enabled: bool = False

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

    def runtime_configuration(self) -> RuntimeConfiguration:
        master_key_bytes = _decode_master_key_length(self.master_key_base64)
        return RuntimeConfiguration(
            application=ApplicationConfig(
                environment=self.environment,
                service_name=self.service_name,
                debug=self.debug,
            ),
            database=DatabaseConfig(
                url=_optional_value(self.database_url),
                alembic_config=_optional_value(self.alembic_config),
                migration_wait_timeout_seconds=self.migration_wait_timeout_seconds,
                migration_lock_timeout_seconds=self.migration_lock_timeout_seconds,
            ),
            security=SecurityConfig(
                secret_key_configured=_optional_value(self.secret_key) is not None,
                secret_key_min_length=SECRET_KEY_MIN_LENGTH,
                tls_required=self.tls_required,
                secure_cookies=self.secure_cookies,
                security_headers_enabled=self.security_headers_enabled,
                allow_insecure_dev_defaults=self.allow_insecure_dev_defaults,
            ),
            authentication=AuthenticationConfig(
                bootstrap_admin_email=_optional_value(self.bootstrap_admin_email),
                bootstrap_admin_password_configured=(
                    _optional_value(self.bootstrap_admin_password) is not None
                ),
                bootstrap_admin_api_key_configured=(
                    _optional_value(self.bootstrap_admin_api_key) is not None
                ),
            ),
            cryptography=CryptographyConfig(
                master_key_configured=_optional_value(self.master_key_base64) is not None,
                master_key_version=self.master_key_version,
                master_key_bytes=master_key_bytes,
            ),
            rest_api=RestApiConfig(
                host=self.rest_host,
                port=self.rest_port,
                openapi_enabled=self.openapi_enabled,
                cors=CorsConfig(
                    allowed_origins=_split_csv(self.cors_allowed_origins),
                    allowed_methods=_split_csv(self.cors_allowed_methods),
                    allowed_headers=_split_csv(self.cors_allowed_headers),
                    allow_credentials=self.cors_allow_credentials,
                ),
                security_headers=SecurityHeadersConfig(
                    enabled=self.security_headers_enabled,
                    hsts_enabled=self.tls_required,
                    content_security_policy=DEFAULT_CONTENT_SECURITY_POLICY,
                    frame_options="DENY",
                    content_type_options="nosniff",
                    referrer_policy="no-referrer",
                    permissions_policy=DEFAULT_PERMISSIONS_POLICY,
                    strict_transport_security=DEFAULT_STRICT_TRANSPORT_SECURITY,
                ),
            ),
            mcp=McpConfig(enabled=self.mcp_enabled),
            logging=LoggingConfig(level=self.log_level, json_enabled=self.log_json),
            opentelemetry=OpenTelemetryConfig(
                traces_enabled=self.otel_traces_enabled,
                exporter_otlp_endpoint=_optional_value(self.otel_exporter_otlp_endpoint),
            ),
            docker=DockerConfig(enabled=self.docker_enabled),
            development=DevelopmentConfig(
                reset_enabled=os.environ.get("MCP_SECRET_MANAGER_ALLOW_DB_RESET") == "true",
                test_database_url_configured=(
                    _optional_value(os.environ.get("MCP_SECRET_MANAGER_TEST_DATABASE_URL"))
                    is not None
                ),
            ),
            bootstrap=BootstrapConfig(
                enabled=self.bootstrap_enabled,
                admin_email=_optional_value(self.bootstrap_admin_email),
                admin_name=_optional_value(self.bootstrap_admin_name),
                admin_password_configured=(
                    _optional_value(self.bootstrap_admin_password) is not None
                ),
                admin_api_key_configured=(
                    _optional_value(self.bootstrap_admin_api_key) is not None
                ),
                service_account_enabled=self.bootstrap_service_account_enabled,
                service_account_project_id_configured=(
                    _optional_value(self.bootstrap_service_account_project_id) is not None
                ),
                service_account_name_configured=(
                    _optional_value(self.bootstrap_service_account_name) is not None
                ),
                service_account_api_key_configured=(
                    _optional_value(self.bootstrap_service_account_api_key) is not None
                ),
            ),
        )

    def validate_runtime(self) -> None:
        errors = self.validation_errors()
        if errors:
            joined = "\n".join(f"- {error}" for error in errors)
            msg = f"Runtime configuration is invalid:\n{joined}"
            raise ConfigurationError(msg)

    def validation_errors(self) -> list[str]:
        errors: list[str] = []

        database_url = _optional_value(self.database_url)
        if self.environment != "test" and database_url is None:
            errors.append(
                "MCP_SECRET_MANAGER_DATABASE_URL is required to create repositories, "
                "transactions and runtime health checks."
            )
        if database_url is not None:
            errors.extend(_validate_database_url(database_url))

        master_key = _optional_value(self.master_key_base64)
        if self.environment != "test" and master_key is None:
            errors.append(
                "MCP_SECRET_MANAGER_MASTER_KEY_BASE64 is required to initialize the "
                "cryptography provider used by secret version use cases."
            )
        if master_key is not None:
            errors.extend(_validate_master_key(master_key, self.environment))

        secret_key = _optional_value(self.secret_key)
        if self.environment in {"staging", "production"} and secret_key is None:
            errors.append(
                "MCP_SECRET_MANAGER_SECRET_KEY is required in staging and production "
                "for signed runtime security material."
            )
        if secret_key is not None and len(secret_key) < SECRET_KEY_MIN_LENGTH:
            errors.append(
                "MCP_SECRET_MANAGER_SECRET_KEY must contain at least "
                f"{SECRET_KEY_MIN_LENGTH} characters."
            )

        if self.environment == "production" and self.debug:
            errors.append("MCP_SECRET_MANAGER_DEBUG must be false in production.")
        if self.environment == "production" and self.openapi_enabled:
            errors.append("MCP_SECRET_MANAGER_OPENAPI_ENABLED must be false in production.")
        if self.environment == "production" and not self.tls_required:
            errors.append("MCP_SECRET_MANAGER_TLS_REQUIRED must be true in production.")
        if self.environment == "production" and not self.secure_cookies:
            errors.append("MCP_SECRET_MANAGER_SECURE_COOKIES must be true in production.")
        if self.environment == "production" and not self.security_headers_enabled:
            errors.append("MCP_SECRET_MANAGER_SECURITY_HEADERS_ENABLED must be true in production.")
        if self.environment == "production" and self.allow_insecure_dev_defaults:
            errors.append(
                "MCP_SECRET_MANAGER_ALLOW_INSECURE_DEV_DEFAULTS must be false in production."
            )

        errors.extend(self._validate_cors())
        errors.extend(self._validate_bootstrap())
        return errors

    def runtime_warnings(self) -> list[str]:
        warnings: list[str] = []
        if self.environment == "development" and _master_key_is_all_zero(self.master_key_base64):
            warnings.append(
                "MCP_SECRET_MANAGER_MASTER_KEY_BASE64 uses the development placeholder key."
            )
        if self.environment == "staging" and self.openapi_enabled:
            warnings.append("OpenAPI is enabled in staging.")
        if self.environment in {"staging", "production"} and self.log_level == "DEBUG":
            warnings.append("DEBUG logging is enabled outside development.")
        return warnings

    def _validate_cors(self) -> list[str]:
        errors: list[str] = []
        origins = _split_csv(self.cors_allowed_origins)
        methods = _split_csv(self.cors_allowed_methods)
        headers = _split_csv(self.cors_allowed_headers)

        if not origins:
            errors.append(
                "MCP_SECRET_MANAGER_CORS_ALLOWED_ORIGINS must contain at least one origin."
            )
        if not methods:
            errors.append(
                "MCP_SECRET_MANAGER_CORS_ALLOWED_METHODS must contain at least one method."
            )
        if not headers:
            errors.append(
                "MCP_SECRET_MANAGER_CORS_ALLOWED_HEADERS must contain at least one header."
            )
        if "*" in origins and self.cors_allow_credentials:
            errors.append(
                "MCP_SECRET_MANAGER_CORS_ALLOWED_ORIGINS cannot contain '*' when "
                "MCP_SECRET_MANAGER_CORS_ALLOW_CREDENTIALS is true."
            )
        if self.environment == "production":
            for origin in origins:
                if origin == "*":
                    errors.append(
                        "MCP_SECRET_MANAGER_CORS_ALLOWED_ORIGINS cannot use wildcard "
                        "origins in production."
                    )
                    break
                if not origin.startswith("https://"):
                    errors.append(
                        "MCP_SECRET_MANAGER_CORS_ALLOWED_ORIGINS must use HTTPS origins "
                        "in production."
                    )
                    break
                if "localhost" in origin or "127.0.0.1" in origin:
                    errors.append(
                        "MCP_SECRET_MANAGER_CORS_ALLOWED_ORIGINS cannot use localhost "
                        "origins in production."
                    )
                    break
        return errors

    def _validate_bootstrap(self) -> list[str]:
        errors: list[str] = []
        if not self.bootstrap_enabled:
            return errors

        if _optional_value(self.bootstrap_admin_email) is None:
            errors.append(
                "MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL is required when bootstrap is enabled."
            )
        if _optional_value(self.bootstrap_admin_name) is None:
            errors.append(
                "MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME is required when bootstrap is enabled."
            )
        password = _optional_value(self.bootstrap_admin_password)
        if password is not None and len(password) < 12:
            errors.append(
                "MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_PASSWORD must contain at least 12 "
                "characters when configured."
            )
        if self.bootstrap_service_account_enabled:
            if _optional_value(self.bootstrap_service_account_project_id) is None:
                errors.append(
                    "MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_PROJECT_ID is required "
                    "when bootstrap service account is enabled."
                )
            if _optional_value(self.bootstrap_service_account_name) is None:
                errors.append(
                    "MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_NAME is required when "
                    "bootstrap service account is enabled."
                )
        return errors


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


def log_safe_runtime_configuration(settings: AppSettings) -> None:
    configuration = settings.runtime_configuration()
    logger.info(
        "Runtime configuration loaded.",
        extra=safe_log_extra(runtime_configuration=configuration.safe_summary()),
    )
    for warning in settings.runtime_warnings():
        logger.warning(
            "Configuration warning.",
            extra=safe_log_extra(configuration_warning=warning),
        )


def _split_csv(raw_value: str) -> tuple[str, ...]:
    return tuple(value.strip() for value in raw_value.split(",") if value.strip())


def _optional_value(raw_value: str | None) -> str | None:
    if raw_value is None:
        return None
    value = raw_value.strip()
    return value or None


def _validate_database_url(database_url: str) -> list[str]:
    try:
        parsed = make_url(database_url)
    except ArgumentError as exc:
        return [f"MCP_SECRET_MANAGER_DATABASE_URL is invalid: {exc}."]

    if parsed.drivername != "postgresql+asyncpg":
        return [
            "MCP_SECRET_MANAGER_DATABASE_URL must use the postgresql+asyncpg SQLAlchemy driver."
        ]
    if parsed.database is None:
        return ["MCP_SECRET_MANAGER_DATABASE_URL must include a database name."]
    return []


def _validate_master_key(master_key_base64: str, environment: RuntimeEnvironment) -> list[str]:
    try:
        decoded = base64.b64decode(master_key_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        return [f"MCP_SECRET_MANAGER_MASTER_KEY_BASE64 must be valid base64: {exc}."]

    if len(decoded) != MASTER_KEY_BYTES:
        return [
            f"MCP_SECRET_MANAGER_MASTER_KEY_BASE64 must decode to exactly {MASTER_KEY_BYTES} bytes."
        ]
    if environment in {"staging", "production"} and decoded == bytes(MASTER_KEY_BYTES):
        return [
            "MCP_SECRET_MANAGER_MASTER_KEY_BASE64 cannot use the development placeholder "
            "key in staging or production."
        ]
    return []


def _decode_master_key_length(master_key_base64: str | None) -> int | None:
    value = _optional_value(master_key_base64)
    if value is None:
        return None
    try:
        return len(base64.b64decode(value, validate=True))
    except (binascii.Error, ValueError):
        return None


def _master_key_is_all_zero(master_key_base64: str | None) -> bool:
    value = _optional_value(master_key_base64)
    if value is None:
        return False
    try:
        return base64.b64decode(value, validate=True) == bytes(MASTER_KEY_BYTES)
    except (binascii.Error, ValueError):
        return False
