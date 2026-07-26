from __future__ import annotations

from pathlib import Path

import pytest


def find_repository_root() -> Path | None:
    for parent in Path(__file__).resolve().parents:
        if (parent / "docker-compose.yml").is_file():
            return parent
    return None


def read_repository_file(relative_path: str) -> str:
    repository_root = find_repository_root()
    if repository_root is None:
        pytest.skip("repository-level deployment files are not mounted in this test environment")
    return (repository_root / relative_path).read_text(encoding="utf-8")


def test_makefile_exposes_postgres_backup_and_restore_targets() -> None:
    makefile = read_repository_file("Makefile")

    assert "BACKUP_DIR ?= dist/backups/postgres" in makefile
    assert "db-backup:" in makefile
    assert "scripts/postgres-backup.sh" in makefile
    assert "db-restore:" in makefile
    assert "BACKUP_FILE is required." in makefile
    assert "scripts/postgres-restore.sh" in makefile


def test_postgres_backup_script_creates_restricted_custom_format_dumps() -> None:
    script = read_repository_file("scripts/postgres-backup.sh")

    assert "pg_dump" in script
    assert "--format=custom" in script
    assert "--no-owner" in script
    assert "--no-privileges" in script
    assert "umask 077" in script
    assert 'chmod 600 "$BACKUP_FILE"' in script
    assert 'sha256sum "$BACKUP_FILE"' in script
    assert 'exec -T "$POSTGRES_SERVICE"' in script
    assert "MCP_SECRET_MANAGER_MASTER_KEY" not in script


def test_postgres_restore_script_is_explicitly_guarded() -> None:
    script = read_repository_file("scripts/postgres-restore.sh")

    assert "pg_restore" in script
    assert "--clean" in script
    assert "--if-exists" in script
    assert "--single-transaction" in script
    assert "--exit-on-error" in script
    assert "--no-owner" in script
    assert "--no-privileges" in script
    assert 'RESTORE_CONFIRM:-}" != "replace"' in script
    assert 'exec -T "$POSTGRES_SERVICE"' in script
    assert "MCP_SECRET_MANAGER_MASTER_KEY" not in script


def test_database_docs_include_operator_backup_and_restore_flow() -> None:
    docs = read_repository_file("db/README.md")

    assert "make db-backup" in docs
    assert "make db-restore" in docs
    assert "RESTORE_CONFIRM=replace" in docs
    assert "sha256" in docs
    assert "application master" in docs
    assert "key is not stored in PostgreSQL" in docs
