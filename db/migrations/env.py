from __future__ import annotations

import os
import time
from asyncio import run
from logging import getLogger
from logging.config import fileConfig

from alembic import context
import sqlalchemy as sa
from sqlalchemy import Connection, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from infrastructure.config import get_settings
from infrastructure.persistence import Base

config = context.config
target_metadata = Base.metadata
logger = getLogger("alembic.runtime.migration")
MIGRATION_LOCK_ID = 426531991
DEFAULT_LOCK_TIMEOUT_SECONDS = 300

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)


def get_database_url() -> str:
    configured_url = config.get_main_option("sqlalchemy.url")
    if configured_url is not None and configured_url.strip() != "":
        return configured_url

    settings = get_settings()
    if settings.database_url is None:
        msg = "MCP_SECRET_MANAGER_DATABASE_URL is required to run migrations."
        raise RuntimeError(msg)
    return settings.database_url


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def migration_lock_timeout_seconds() -> int:
    raw_value = os.environ.get("MCP_SECRET_MANAGER_MIGRATION_LOCK_TIMEOUT_SECONDS")
    if raw_value is None:
        return DEFAULT_LOCK_TIMEOUT_SECONDS
    return int(raw_value)


def acquire_migration_lock(connection: Connection) -> None:
    timeout_seconds = migration_lock_timeout_seconds()
    started_at = time.monotonic()

    while time.monotonic() - started_at <= timeout_seconds:
        locked = connection.execute(
            sa.text("SELECT pg_try_advisory_lock(:lock_id)"),
            {"lock_id": MIGRATION_LOCK_ID},
        ).scalar_one()
        if locked:
            logger.info("✓ Migration lock acquired")
            return

        logger.info("Another migration is already running. Waiting.")
        time.sleep(1)

    msg = f"Timed out waiting for migration lock after {timeout_seconds} seconds."
    raise RuntimeError(msg)


def release_migration_lock(connection: Connection) -> None:
    connection.execute(
        sa.text("SELECT pg_advisory_unlock(:lock_id)"),
        {"lock_id": MIGRATION_LOCK_ID},
    )
    logger.info("✓ Migration lock released")


def do_run_migrations(connection: Connection) -> None:
    acquire_migration_lock(connection)
    connection.commit()
    try:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()
    finally:
        release_migration_lock(connection)
        connection.commit()


async def run_async_migrations() -> None:
    config.set_main_option("sqlalchemy.url", get_database_url())
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
