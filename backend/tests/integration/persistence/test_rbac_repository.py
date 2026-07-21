from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from domain.identity.value_objects import ApiKeyOwnerType, UserId
from domain.rbac.entities import Permission, Role, RoleAssignment
from domain.rbac.repositories import (
    PermissionRepositoryConflictError,
    RoleAssignmentRepositoryConflictError,
    RoleRepositoryConflictError,
)
from domain.rbac.value_objects import PermissionName, RoleName, ScopeType
from infrastructure.persistence import Base
from infrastructure.persistence.rbac_repositories import (
    SqlAlchemyPermissionRepository,
    SqlAlchemyRoleAssignmentRepository,
    SqlAlchemyRoleRepository,
)

TEST_SCHEMA = "mcp_secret_manager_rbac_repository_test"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def database_url() -> str:
    value = os.environ.get("MCP_SECRET_MANAGER_TEST_DATABASE_URL")
    if value is None:
        pytest.skip("MCP_SECRET_MANAGER_TEST_DATABASE_URL is required for PostgreSQL tests.")
    return value


@pytest.fixture
async def session_factory(
    database_url: str,
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    admin_engine = create_async_engine(database_url, isolation_level="AUTOCOMMIT")
    async with admin_engine.begin() as connection:
        await connection.execute(text(f'DROP SCHEMA IF EXISTS "{TEST_SCHEMA}" CASCADE'))
        await connection.execute(text(f'CREATE SCHEMA "{TEST_SCHEMA}"'))
    await admin_engine.dispose()

    engine = create_async_engine(
        database_url,
        connect_args={"server_settings": {"search_path": TEST_SCHEMA}},
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    try:
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        await engine.dispose()
        cleanup_engine = create_async_engine(database_url, isolation_level="AUTOCOMMIT")
        async with cleanup_engine.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA IF EXISTS "{TEST_SCHEMA}" CASCADE'))
        await cleanup_engine.dispose()


async def create_role_with_permission(
    session: AsyncSession,
    permission_name: str = "secret.read",
) -> tuple[Permission, Role]:
    permission_repository = SqlAlchemyPermissionRepository(session)
    role_repository = SqlAlchemyRoleRepository(session)
    permission = await permission_repository.create(
        Permission.create(PermissionName(permission_name), "Read secrets.")
    )
    role = await role_repository.create(Role.create(RoleName("reader"), "Read-only role."))
    await role_repository.add_permission(role.id, permission.id)
    return permission, role


@pytest.mark.integration
@pytest.mark.anyio
async def test_rbac_repositories_create_and_read_role_graph(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    user_id = UserId.new()
    async with session_factory() as session:
        permission, role = await create_role_with_permission(session)
        role_assignment_repository = SqlAlchemyRoleAssignmentRepository(session)
        role_assignment = await role_assignment_repository.create(
            RoleAssignment.create(user_id, ApiKeyOwnerType.USER, ScopeType.GLOBAL, None, role.id)
        )
        await session.commit()

    async with session_factory() as session:
        permission_repository = SqlAlchemyPermissionRepository(session)
        role_repository = SqlAlchemyRoleRepository(session)
        role_assignment_repository = SqlAlchemyRoleAssignmentRepository(session)

        fetched_permission = await permission_repository.get_by_name(PermissionName("secret.read"))
        fetched_role = await role_repository.get_by_name(RoleName("reader"))
        has_permission = await role_repository.has_permission(role.id, permission.id)
        assignments = await role_assignment_repository.list_for_identity(
            user_id,
            ApiKeyOwnerType.USER,
        )

    assert fetched_permission == permission
    assert fetched_role == role
    assert has_permission is True
    assert assignments == (role_assignment,)


@pytest.mark.integration
@pytest.mark.anyio
async def test_rbac_repositories_enforce_unique_permission_and_role_names(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        permission_repository = SqlAlchemyPermissionRepository(session)
        role_repository = SqlAlchemyRoleRepository(session)

        await permission_repository.create(Permission.create(PermissionName("secret.read"), None))
        await role_repository.create(Role.create(RoleName("reader"), None))
        await session.commit()

        with pytest.raises(PermissionRepositoryConflictError):
            await permission_repository.create(
                Permission.create(PermissionName("secret.read"), None)
            )
        await session.rollback()

        with pytest.raises(RoleRepositoryConflictError):
            await role_repository.create(Role.create(RoleName("reader"), None))


@pytest.mark.integration
@pytest.mark.anyio
async def test_rbac_repository_enforces_unique_global_assignments(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    user_id = UserId.new()
    async with session_factory() as session:
        _, role = await create_role_with_permission(session)
        role_assignment_repository = SqlAlchemyRoleAssignmentRepository(session)
        await role_assignment_repository.create(
            RoleAssignment.create(user_id, ApiKeyOwnerType.USER, ScopeType.GLOBAL, None, role.id)
        )

        with pytest.raises(RoleAssignmentRepositoryConflictError):
            await role_assignment_repository.create(
                RoleAssignment.create(
                    user_id,
                    ApiKeyOwnerType.USER,
                    ScopeType.GLOBAL,
                    None,
                    role.id,
                )
            )
