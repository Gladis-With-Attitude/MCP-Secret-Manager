from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from infrastructure import database_migrations
from infrastructure.config import AppSettings


def create_alembic_config(tmp_path: Path) -> Path:
    db_dir = tmp_path / "db"
    migrations_dir = db_dir / "migrations"
    migrations_dir.mkdir(parents=True)
    config_path = db_dir / "alembic.ini"
    config_path.write_text("[alembic]\nscript_location = %(here)s/migrations\n")
    return config_path


def test_build_alembic_config_resolves_absolute_script_location(tmp_path: Path) -> None:
    config_path = create_alembic_config(tmp_path)

    config = database_migrations.build_alembic_config(str(config_path))

    assert config.get_main_option("script_location") == str(config_path.parent / "migrations")


def test_upgrade_waits_for_postgresql_before_running_alembic(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_path = create_alembic_config(tmp_path)
    calls: list[str] = []

    async def wait_for_postgresql(
        _settings: AppSettings,
        _timeout_seconds: int,
    ) -> None:
        calls.append("wait")

    def run_upgrade(_config: Config, revision: str) -> None:
        calls.append(f"upgrade:{revision}")

    monkeypatch.setattr(database_migrations, "wait_for_postgresql", wait_for_postgresql)
    monkeypatch.setattr(database_migrations, "migration_wait_timeout_seconds", lambda: 10)
    monkeypatch.setattr(command, "upgrade", run_upgrade)

    database_migrations.upgrade(
        "head",
        settings=AppSettings(
            environment="local",
            database_url="postgresql+asyncpg://user:password@postgres:5432/app",
        ),
        config_path=str(config_path),
    )

    assert calls == ["wait", "upgrade:head"]


def test_reset_public_schema_requires_development_environment() -> None:
    settings = AppSettings(
        environment="production",
        database_url="postgresql+asyncpg://user:password@postgres:5432/app",
    )

    with pytest.raises(RuntimeError, match="only allowed in local or test"):
        asyncio.run(database_migrations.reset_public_schema(settings))


def test_reset_public_schema_requires_explicit_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MCP_SECRET_MANAGER_ALLOW_DB_RESET", raising=False)
    settings = AppSettings(
        environment="local",
        database_url="postgresql+asyncpg://user:password@postgres:5432/app",
    )

    with pytest.raises(RuntimeError, match="ALLOW_DB_RESET"):
        asyncio.run(database_migrations.reset_public_schema(settings))
