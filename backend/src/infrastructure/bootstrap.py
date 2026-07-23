from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from application.audit.use_cases import ListAuditEventsUseCase, PersistentAuditRecorder
from application.crypto.use_cases import DecryptSecretValueUseCase, EncryptSecretValueUseCase
from application.health import HealthStatus
from application.identity.use_cases import (
    AuthenticateApiKeyUseCase,
    AuthenticateSessionUseCase,
    CreateApiKeyUseCase,
    CreateServiceAccountUseCase,
    CreateSessionUseCase,
    CreateUserUseCase,
    GetCurrentSessionUseCase,
    RevokeCurrentSessionUseCase,
)
from application.project.use_cases import (
    ArchiveProjectUseCase,
    CreateProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    UpdateProjectUseCase,
)
from application.rbac.use_cases import AuthorizeUseCase, PermissionChecker
from application.secret.use_cases import (
    ArchiveSecretUseCase,
    CreateSecretUseCase,
    GetSecretUseCase,
    ListSecretsUseCase,
    SearchSecretsUseCase,
    UpdateSecretUseCase,
)
from application.secret_version.use_cases import (
    CreateSecretVersionUseCase,
    GetActiveSecretVersionUseCase,
    GetSecretVersionMetadataUseCase,
    ListSecretVersionsUseCase,
    RestoreSecretVersionUseCase,
)
from application.vault.use_cases import (
    ArchiveVaultUseCase,
    CreateVaultUseCase,
    GetVaultUseCase,
    ListVaultsUseCase,
    UpdateVaultUseCase,
)
from infrastructure.config import (
    AppSettings,
    ConfigurationError,
    get_settings,
    log_safe_runtime_configuration,
)
from infrastructure.crypto import AesGcmCryptoProvider
from infrastructure.identity import (
    Argon2idApiKeyHasher,
    SecureApiKeySecretGenerator,
    SecureSessionTokenGenerator,
)
from infrastructure.logging import configure_runtime_logging
from infrastructure.persistence.database import create_database_engine, create_session_factory
from infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from presentation.mcp.server import McpServer
from presentation.mcp.tools import SecretManagerMcpTools
from presentation.rest.app import create_app
from presentation.rest.dependencies import (
    get_active_secret_version_use_case,
    get_archive_project_use_case,
    get_archive_secret_use_case,
    get_archive_vault_use_case,
    get_authorize_use_case,
    get_create_api_key_use_case,
    get_create_project_use_case,
    get_create_secret_use_case,
    get_create_secret_version_use_case,
    get_create_service_account_use_case,
    get_create_session_use_case,
    get_create_user_use_case,
    get_create_vault_use_case,
    get_current_session_use_case,
    get_list_audit_events_use_case,
    get_list_projects_use_case,
    get_list_secret_versions_use_case,
    get_list_secrets_use_case,
    get_list_vaults_use_case,
    get_project_use_case,
    get_restore_secret_version_use_case,
    get_revoke_current_session_use_case,
    get_secret_use_case,
    get_secret_version_metadata_use_case,
    get_update_project_use_case,
    get_update_secret_use_case,
    get_update_vault_use_case,
    get_vault_use_case,
)

logger = logging.getLogger(__name__)


class RuntimeHealthCheck:
    def __init__(
        self,
        service_name: str,
        configuration_valid: bool,
        engine: AsyncEngine | None,
        session_factory: async_sessionmaker[AsyncSession] | None,
        use_cases_initialized: bool,
    ) -> None:
        self._service_name = service_name
        self._configuration_valid = configuration_valid
        self._engine = engine
        self._session_factory = session_factory
        self._use_cases_initialized = use_cases_initialized

    async def __call__(self) -> HealthStatus:
        database_status = await self._database_status()
        repositories_status: Literal["not_configured", "ok"] = (
            "ok" if self._session_factory is not None else "not_configured"
        )
        use_cases_status: Literal["not_configured", "ok"] = (
            "ok" if self._use_cases_initialized else "not_configured"
        )
        configuration_status: Literal["invalid", "ok"] = (
            "ok" if self._configuration_valid else "invalid"
        )
        status: Literal["degraded", "ok"] = (
            "ok"
            if database_status == "ok"
            and repositories_status == "ok"
            and use_cases_status == "ok"
            and configuration_status == "ok"
            else "degraded"
        )

        return HealthStatus(
            status=status,
            service=self._service_name,
            api="ok",
            configuration=configuration_status,
            database=database_status,
            repositories=repositories_status,
            use_cases=use_cases_status,
        )

    async def _database_status(self) -> Literal["not_configured", "ok", "unavailable"]:
        if self._engine is None:
            return "not_configured"

        try:
            async with self._engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
        except Exception:
            logger.exception("PostgreSQL health check failed.")
            return "unavailable"

        return "ok"


async def verify_database_connection(engine: AsyncEngine | None) -> None:
    if engine is None:
        logger.warning("PostgreSQL is not configured.")
        return

    logger.info("Connecting to PostgreSQL.")
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    logger.info("✓ Base PostgreSQL connectée")


def create_rest_app(settings: AppSettings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    configure_runtime_logging(
        resolved_settings.log_level,
        json_enabled=resolved_settings.log_json,
    )
    resolved_settings.validate_runtime()
    log_safe_runtime_configuration(resolved_settings)
    logger.info("✓ Configuration chargée")

    engine = (
        create_database_engine(resolved_settings.database_url)
        if resolved_settings.database_url is not None
        else None
    )
    session_factory = create_session_factory(engine) if engine is not None else None
    use_cases_initialized = session_factory is not None
    api_key_generator = SecureApiKeySecretGenerator()
    api_key_hasher = Argon2idApiKeyHasher()
    session_token_generator = SecureSessionTokenGenerator()
    session_token_hasher = Argon2idApiKeyHasher()
    audit_recorder = (
        PersistentAuditRecorder(SqlAlchemyUnitOfWork(session_factory))
        if session_factory is not None
        else None
    )
    authenticate_api_key_use_case = (
        AuthenticateApiKeyUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            api_key_generator,
            api_key_hasher,
            audit_recorder=audit_recorder,
        )
        if session_factory is not None
        else None
    )
    authenticate_session_use_case = (
        AuthenticateSessionUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            session_token_generator,
            session_token_hasher,
        )
        if session_factory is not None
        else None
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            await verify_database_connection(engine)
            if session_factory is not None:
                logger.info("✓ Repositories initialisés")
            if use_cases_initialized:
                logger.info("✓ Use Cases initialisés")
            logger.info("✓ REST API prête")
            logger.info("✓ MCP prêt (factory disponible)")
            yield
        except Exception:
            logger.exception("Backend startup failed.")
            raise
        finally:
            if engine is not None:
                logger.info("Closing PostgreSQL engine.")
                await engine.dispose()

    health_check = RuntimeHealthCheck(
        service_name=resolved_settings.service_name,
        configuration_valid=True,
        engine=engine,
        session_factory=session_factory,
        use_cases_initialized=use_cases_initialized,
    )
    app = create_app(
        service_name=resolved_settings.service_name,
        openapi_enabled=resolved_settings.openapi_enabled,
        lifespan=lifespan,
        authenticate_api_key_use_case=authenticate_api_key_use_case,
        authenticate_session_use_case=authenticate_session_use_case,
        health_check=health_check,
    )

    if session_factory is not None:
        crypto_provider = AesGcmCryptoProvider.from_base64_master_key(
            resolved_settings.master_key_base64,
            key_version=resolved_settings.master_key_version,
        )

        def create_vault_use_case() -> CreateVaultUseCase:
            return CreateVaultUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def list_vaults_use_case() -> ListVaultsUseCase:
            return ListVaultsUseCase(SqlAlchemyUnitOfWork(session_factory))

        def build_get_vault_use_case() -> GetVaultUseCase:
            return GetVaultUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def update_vault_use_case() -> UpdateVaultUseCase:
            return UpdateVaultUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def archive_vault_use_case() -> ArchiveVaultUseCase:
            return ArchiveVaultUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def create_user_use_case() -> CreateUserUseCase:
            return CreateUserUseCase(SqlAlchemyUnitOfWork(session_factory))

        def create_service_account_use_case() -> CreateServiceAccountUseCase:
            return CreateServiceAccountUseCase(SqlAlchemyUnitOfWork(session_factory))

        def create_api_key_use_case() -> CreateApiKeyUseCase:
            return CreateApiKeyUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                api_key_generator,
                api_key_hasher,
                audit_recorder=audit_recorder,
            )

        def create_session_use_case() -> CreateSessionUseCase:
            return CreateSessionUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                api_key_generator,
                api_key_hasher,
                session_token_generator,
                session_token_hasher,
                audit_recorder=audit_recorder,
            )

        def current_session_use_case() -> GetCurrentSessionUseCase:
            return GetCurrentSessionUseCase(SqlAlchemyUnitOfWork(session_factory))

        def revoke_current_session_use_case() -> RevokeCurrentSessionUseCase:
            return RevokeCurrentSessionUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def authorize_use_case() -> AuthorizeUseCase:
            return AuthorizeUseCase(
                PermissionChecker(SqlAlchemyUnitOfWork(session_factory)),
                audit_recorder=audit_recorder,
            )

        def list_audit_events_use_case() -> ListAuditEventsUseCase:
            return ListAuditEventsUseCase(SqlAlchemyUnitOfWork(session_factory))

        def create_project_use_case() -> CreateProjectUseCase:
            return CreateProjectUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def list_projects_use_case() -> ListProjectsUseCase:
            return ListProjectsUseCase(SqlAlchemyUnitOfWork(session_factory))

        def build_get_project_use_case() -> GetProjectUseCase:
            return GetProjectUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def update_project_use_case() -> UpdateProjectUseCase:
            return UpdateProjectUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def archive_project_use_case() -> ArchiveProjectUseCase:
            return ArchiveProjectUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def create_secret_use_case() -> CreateSecretUseCase:
            return CreateSecretUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def list_secrets_use_case() -> ListSecretsUseCase:
            return ListSecretsUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def build_get_secret_use_case() -> GetSecretUseCase:
            return GetSecretUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def update_secret_use_case() -> UpdateSecretUseCase:
            return UpdateSecretUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def archive_secret_use_case() -> ArchiveSecretUseCase:
            return ArchiveSecretUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def create_secret_version_use_case() -> CreateSecretVersionUseCase:
            return CreateSecretVersionUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                EncryptSecretValueUseCase(crypto_provider),
                audit_recorder=audit_recorder,
            )

        def list_secret_versions_use_case() -> ListSecretVersionsUseCase:
            return ListSecretVersionsUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def build_get_secret_version_metadata_use_case() -> GetSecretVersionMetadataUseCase:
            return GetSecretVersionMetadataUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        def build_active_secret_version_use_case() -> GetActiveSecretVersionUseCase:
            return GetActiveSecretVersionUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                DecryptSecretValueUseCase(crypto_provider),
                audit_recorder=audit_recorder,
            )

        def restore_secret_version_use_case() -> RestoreSecretVersionUseCase:
            return RestoreSecretVersionUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                audit_recorder=audit_recorder,
            )

        app.dependency_overrides[get_create_vault_use_case] = create_vault_use_case
        app.dependency_overrides[get_list_vaults_use_case] = list_vaults_use_case
        app.dependency_overrides[get_vault_use_case] = build_get_vault_use_case
        app.dependency_overrides[get_update_vault_use_case] = update_vault_use_case
        app.dependency_overrides[get_archive_vault_use_case] = archive_vault_use_case
        app.dependency_overrides[get_create_user_use_case] = create_user_use_case
        app.dependency_overrides[get_create_service_account_use_case] = (
            create_service_account_use_case
        )
        app.dependency_overrides[get_create_api_key_use_case] = create_api_key_use_case
        app.dependency_overrides[get_create_session_use_case] = create_session_use_case
        app.dependency_overrides[get_current_session_use_case] = current_session_use_case
        app.dependency_overrides[get_revoke_current_session_use_case] = (
            revoke_current_session_use_case
        )
        app.dependency_overrides[get_authorize_use_case] = authorize_use_case
        app.dependency_overrides[get_list_audit_events_use_case] = list_audit_events_use_case
        app.dependency_overrides[get_create_project_use_case] = create_project_use_case
        app.dependency_overrides[get_list_projects_use_case] = list_projects_use_case
        app.dependency_overrides[get_project_use_case] = build_get_project_use_case
        app.dependency_overrides[get_update_project_use_case] = update_project_use_case
        app.dependency_overrides[get_archive_project_use_case] = archive_project_use_case
        app.dependency_overrides[get_create_secret_use_case] = create_secret_use_case
        app.dependency_overrides[get_list_secrets_use_case] = list_secrets_use_case
        app.dependency_overrides[get_secret_use_case] = build_get_secret_use_case
        app.dependency_overrides[get_update_secret_use_case] = update_secret_use_case
        app.dependency_overrides[get_archive_secret_use_case] = archive_secret_use_case
        app.dependency_overrides[get_create_secret_version_use_case] = (
            create_secret_version_use_case
        )
        app.dependency_overrides[get_list_secret_versions_use_case] = list_secret_versions_use_case
        app.dependency_overrides[get_secret_version_metadata_use_case] = (
            build_get_secret_version_metadata_use_case
        )
        app.dependency_overrides[get_active_secret_version_use_case] = (
            build_active_secret_version_use_case
        )
        app.dependency_overrides[get_restore_secret_version_use_case] = (
            restore_secret_version_use_case
        )

    return app


app = create_rest_app()


def create_mcp_server(settings: AppSettings | None = None) -> McpServer:
    resolved_settings = settings or get_settings()
    if resolved_settings.database_url is None:
        raise ConfigurationError("MCP server requires MCP_SECRET_MANAGER_DATABASE_URL.")
    if resolved_settings.master_key_base64 is None:
        raise ConfigurationError("MCP server requires MCP_SECRET_MANAGER_MASTER_KEY_BASE64.")

    engine = create_database_engine(resolved_settings.database_url)
    session_factory = create_session_factory(engine)
    unit_of_work = SqlAlchemyUnitOfWork
    api_key_generator = SecureApiKeySecretGenerator()
    api_key_hasher = Argon2idApiKeyHasher()
    audit_recorder = PersistentAuditRecorder(unit_of_work(session_factory))
    crypto_provider = AesGcmCryptoProvider.from_base64_master_key(
        resolved_settings.master_key_base64,
        key_version=resolved_settings.master_key_version,
    )

    authenticate_api_key_use_case = AuthenticateApiKeyUseCase(
        unit_of_work(session_factory),
        api_key_generator,
        api_key_hasher,
        audit_recorder=audit_recorder,
    )
    authorize_use_case = AuthorizeUseCase(
        PermissionChecker(unit_of_work(session_factory)),
        audit_recorder=audit_recorder,
    )

    server = McpServer(name=resolved_settings.service_name)
    tools = SecretManagerMcpTools(
        service_name=resolved_settings.service_name,
        authenticate_api_key_use_case=authenticate_api_key_use_case,
        authorize_use_case=authorize_use_case,
        list_vaults_use_case=ListVaultsUseCase(unit_of_work(session_factory)),
        create_vault_use_case=CreateVaultUseCase(
            unit_of_work(session_factory),
            audit_recorder=audit_recorder,
        ),
        list_projects_use_case=ListProjectsUseCase(unit_of_work(session_factory)),
        create_project_use_case=CreateProjectUseCase(
            unit_of_work(session_factory),
            audit_recorder=audit_recorder,
        ),
        list_secrets_use_case=ListSecretsUseCase(
            unit_of_work(session_factory),
            audit_recorder=audit_recorder,
        ),
        create_secret_use_case=CreateSecretUseCase(
            unit_of_work(session_factory),
            audit_recorder=audit_recorder,
        ),
        get_secret_use_case=GetSecretUseCase(
            unit_of_work(session_factory),
            audit_recorder=audit_recorder,
        ),
        create_secret_version_use_case=CreateSecretVersionUseCase(
            unit_of_work(session_factory),
            EncryptSecretValueUseCase(crypto_provider),
            audit_recorder=audit_recorder,
        ),
        list_secret_versions_use_case=ListSecretVersionsUseCase(
            unit_of_work(session_factory),
            audit_recorder=audit_recorder,
        ),
        get_active_secret_version_use_case=GetActiveSecretVersionUseCase(
            unit_of_work(session_factory),
            DecryptSecretValueUseCase(crypto_provider),
            audit_recorder=audit_recorder,
        ),
        search_secrets_use_case=SearchSecretsUseCase(
            unit_of_work(session_factory),
            audit_recorder=audit_recorder,
        ),
    )
    tools.register(server)
    return server
