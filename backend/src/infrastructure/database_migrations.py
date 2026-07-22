from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import time
from collections.abc import Sequence
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from infrastructure.config import AppSettings, get_settings
from infrastructure.persistence.database import create_database_engine

logger = logging.getLogger(__name__)

DEFAULT_WAIT_TIMEOUT_SECONDS = 60
DEFAULT_WAIT_INTERVAL_SECONDS = 1


def find_alembic_config(explicit_path: str | None = None) -> Path:
    candidates = []
    if explicit_path is not None:
        candidates.append(Path(explicit_path))

    env_path = os.environ.get("MCP_SECRET_MANAGER_ALEMBIC_CONFIG")
    if env_path is not None:
        candidates.append(Path(env_path))

    candidates.extend(
        [
            Path("/db/alembic.ini"),
            Path.cwd() / "db" / "alembic.ini",
            Path.cwd().parent / "db" / "alembic.ini",
        ]
    )

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    searched = ", ".join(str(candidate) for candidate in candidates)
    msg = f"Alembic configuration not found. Searched: {searched}."
    raise RuntimeError(msg)


def build_alembic_config(config_path: str | None = None) -> Config:
    path = find_alembic_config(config_path)
    config = Config(str(path))
    config.set_main_option("script_location", str(path.parent / "migrations"))
    return config


def migration_wait_timeout_seconds() -> int:
    raw_value = os.environ.get("MCP_SECRET_MANAGER_MIGRATION_WAIT_TIMEOUT_SECONDS")
    if raw_value is None:
        return DEFAULT_WAIT_TIMEOUT_SECONDS
    return int(raw_value)


async def wait_for_postgresql(
    settings: AppSettings,
    timeout_seconds: int = DEFAULT_WAIT_TIMEOUT_SECONDS,
    interval_seconds: int = DEFAULT_WAIT_INTERVAL_SECONDS,
) -> None:
    if settings.database_url is None:
        msg = "MCP_SECRET_MANAGER_DATABASE_URL is required to run migrations."
        raise RuntimeError(msg)

    engine = create_database_engine(settings.database_url)
    started_at = time.monotonic()
    last_error: BaseException | None = None

    try:
        while time.monotonic() - started_at <= timeout_seconds:
            try:
                async with engine.connect() as connection:
                    await connection.execute(text("SELECT 1"))
                logger.info("✓ PostgreSQL disponible")
                return
            except Exception as exc:
                last_error = exc
                logger.info("PostgreSQL not available yet. Retrying.")
                await asyncio.sleep(interval_seconds)

        msg = f"PostgreSQL did not become available within {timeout_seconds} seconds."
        raise RuntimeError(msg) from last_error
    finally:
        await engine.dispose()


async def reset_public_schema(settings: AppSettings) -> None:
    if settings.environment not in {"local", "test"}:
        msg = "Database reset is only allowed in local or test environments."
        raise RuntimeError(msg)
    if os.environ.get("MCP_SECRET_MANAGER_ALLOW_DB_RESET") != "true":
        msg = "Set MCP_SECRET_MANAGER_ALLOW_DB_RESET=true to reset the development database."
        raise RuntimeError(msg)
    if settings.database_url is None:
        msg = "MCP_SECRET_MANAGER_DATABASE_URL is required to reset the database."
        raise RuntimeError(msg)

    engine = create_database_engine(settings.database_url)
    try:
        async with engine.begin() as connection:
            logger.warning("Resetting PostgreSQL public schema for development.")
            await connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            await connection.execute(text("CREATE SCHEMA public"))
            await connection.execute(text("GRANT ALL ON SCHEMA public TO PUBLIC"))
    finally:
        await engine.dispose()


def upgrade(
    revision: str = "head",
    *,
    settings: AppSettings | None = None,
    config_path: str | None = None,
) -> None:
    resolved_settings = settings or get_settings()
    asyncio.run(wait_for_postgresql(resolved_settings, migration_wait_timeout_seconds()))

    logger.info("✓ Migration détectée")
    logger.info("✓ Upgrade vers %s", revision)
    command.upgrade(build_alembic_config(config_path), revision)
    configure_logging()
    logger.info("✓ Base synchronisée")


def downgrade(
    revision: str,
    *,
    settings: AppSettings | None = None,
    config_path: str | None = None,
) -> None:
    resolved_settings = settings or get_settings()
    asyncio.run(wait_for_postgresql(resolved_settings, migration_wait_timeout_seconds()))

    logger.info("Downgrade vers %s", revision)
    command.downgrade(build_alembic_config(config_path), revision)
    configure_logging()
    logger.info("✓ Base synchronisée")


def current(*, settings: AppSettings | None = None, config_path: str | None = None) -> None:
    resolved_settings = settings or get_settings()
    asyncio.run(wait_for_postgresql(resolved_settings, migration_wait_timeout_seconds()))

    command.current(build_alembic_config(config_path), verbose=True)


def history(*, config_path: str | None = None) -> None:
    command.history(build_alembic_config(config_path), verbose=True)


def revision(
    message: str,
    *,
    autogenerate: bool = False,
    settings: AppSettings | None = None,
    config_path: str | None = None,
) -> None:
    if autogenerate:
        resolved_settings = settings or get_settings()
        asyncio.run(wait_for_postgresql(resolved_settings, migration_wait_timeout_seconds()))

    command.revision(
        build_alembic_config(config_path),
        message=message,
        autogenerate=autogenerate,
    )


def reset(*, settings: AppSettings | None = None, config_path: str | None = None) -> None:
    resolved_settings = settings or get_settings()
    asyncio.run(wait_for_postgresql(resolved_settings, migration_wait_timeout_seconds()))
    asyncio.run(reset_public_schema(resolved_settings))

    logger.info("✓ Upgrade vers head")
    command.upgrade(build_alembic_config(config_path), "head")
    configure_logging()
    logger.info("✓ Base synchronisée")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage MCP Secret Manager database migrations.")
    parser.add_argument(
        "--config",
        help=(
            "Path to alembic.ini. Defaults to MCP_SECRET_MANAGER_ALEMBIC_CONFIG or /db/alembic.ini."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    upgrade_parser = subparsers.add_parser("upgrade")
    upgrade_parser.add_argument("revision", nargs="?", default="head")

    downgrade_parser = subparsers.add_parser("downgrade")
    downgrade_parser.add_argument("revision")

    subparsers.add_parser("current")
    subparsers.add_parser("history")
    subparsers.add_parser("reset")

    revision_parser = subparsers.add_parser("revision")
    revision_parser.add_argument("--message", "-m", required=True)
    revision_parser.add_argument("--autogenerate", action="store_true")

    return parser


def configure_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level)
    logging.basicConfig(
        level=level,
        format="%(levelname)s:%(name)s:%(message)s",
    )
    logging.getLogger().setLevel(level)


def main(argv: Sequence[str] | None = None) -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "upgrade":
            upgrade(args.revision, config_path=args.config)
        elif args.command == "downgrade":
            downgrade(args.revision, config_path=args.config)
        elif args.command == "current":
            current(config_path=args.config)
        elif args.command == "history":
            history(config_path=args.config)
        elif args.command == "revision":
            revision(
                args.message,
                autogenerate=args.autogenerate,
                config_path=args.config,
            )
        elif args.command == "reset":
            reset(config_path=args.config)
        else:
            parser.error(f"Unsupported command: {args.command}")
    except Exception:
        logger.exception("Database migration command failed.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
