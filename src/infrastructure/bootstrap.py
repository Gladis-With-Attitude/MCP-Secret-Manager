from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from application.crypto.use_cases import DecryptSecretValueUseCase, EncryptSecretValueUseCase
from application.identity.use_cases import (
    AuthenticateApiKeyUseCase,
    CreateApiKeyUseCase,
    CreateServiceAccountUseCase,
    CreateUserUseCase,
)
from application.project.use_cases import CreateProjectUseCase
from application.secret.use_cases import CreateSecretUseCase
from application.secret_version.use_cases import (
    CreateSecretVersionUseCase,
    GetActiveSecretVersionUseCase,
    ListSecretVersionsUseCase,
)
from application.vault.use_cases import CreateVaultUseCase
from infrastructure.config import AppSettings, get_settings
from infrastructure.crypto import AesGcmCryptoProvider
from infrastructure.identity import Argon2idApiKeyHasher, SecureApiKeySecretGenerator
from infrastructure.persistence.database import create_database_engine, create_session_factory
from infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from presentation.rest.app import create_app
from presentation.rest.dependencies import (
    get_active_secret_version_use_case,
    get_create_api_key_use_case,
    get_create_project_use_case,
    get_create_secret_use_case,
    get_create_secret_version_use_case,
    get_create_service_account_use_case,
    get_create_user_use_case,
    get_create_vault_use_case,
    get_list_secret_versions_use_case,
)


def create_rest_app(settings: AppSettings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_settings.validate_runtime()

    engine = (
        create_database_engine(resolved_settings.database_url)
        if resolved_settings.database_url is not None
        else None
    )
    session_factory = create_session_factory(engine) if engine is not None else None
    api_key_generator = SecureApiKeySecretGenerator()
    api_key_hasher = Argon2idApiKeyHasher()
    authenticate_api_key_use_case = (
        AuthenticateApiKeyUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            api_key_generator,
            api_key_hasher,
        )
        if session_factory is not None
        else None
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            if engine is not None:
                await engine.dispose()

    app = create_app(
        service_name=resolved_settings.service_name,
        openapi_enabled=resolved_settings.openapi_enabled,
        lifespan=lifespan,
        authenticate_api_key_use_case=authenticate_api_key_use_case,
    )

    if session_factory is not None:
        crypto_provider = AesGcmCryptoProvider.from_base64_master_key(
            resolved_settings.master_key_base64,
            key_version=resolved_settings.master_key_version,
        )

        def create_vault_use_case() -> CreateVaultUseCase:
            return CreateVaultUseCase(SqlAlchemyUnitOfWork(session_factory))

        def create_user_use_case() -> CreateUserUseCase:
            return CreateUserUseCase(SqlAlchemyUnitOfWork(session_factory))

        def create_service_account_use_case() -> CreateServiceAccountUseCase:
            return CreateServiceAccountUseCase(SqlAlchemyUnitOfWork(session_factory))

        def create_api_key_use_case() -> CreateApiKeyUseCase:
            return CreateApiKeyUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                api_key_generator,
                api_key_hasher,
            )

        def create_project_use_case() -> CreateProjectUseCase:
            return CreateProjectUseCase(SqlAlchemyUnitOfWork(session_factory))

        def create_secret_use_case() -> CreateSecretUseCase:
            return CreateSecretUseCase(SqlAlchemyUnitOfWork(session_factory))

        def create_secret_version_use_case() -> CreateSecretVersionUseCase:
            return CreateSecretVersionUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                EncryptSecretValueUseCase(crypto_provider),
            )

        def list_secret_versions_use_case() -> ListSecretVersionsUseCase:
            return ListSecretVersionsUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                DecryptSecretValueUseCase(crypto_provider),
            )

        def build_active_secret_version_use_case() -> GetActiveSecretVersionUseCase:
            return GetActiveSecretVersionUseCase(
                SqlAlchemyUnitOfWork(session_factory),
                DecryptSecretValueUseCase(crypto_provider),
            )

        app.dependency_overrides[get_create_vault_use_case] = create_vault_use_case
        app.dependency_overrides[get_create_user_use_case] = create_user_use_case
        app.dependency_overrides[get_create_service_account_use_case] = (
            create_service_account_use_case
        )
        app.dependency_overrides[get_create_api_key_use_case] = create_api_key_use_case
        app.dependency_overrides[get_create_project_use_case] = create_project_use_case
        app.dependency_overrides[get_create_secret_use_case] = create_secret_use_case
        app.dependency_overrides[get_create_secret_version_use_case] = (
            create_secret_version_use_case
        )
        app.dependency_overrides[get_list_secret_versions_use_case] = list_secret_versions_use_case
        app.dependency_overrides[get_active_secret_version_use_case] = (
            build_active_secret_version_use_case
        )

    return app


app = create_rest_app()
