from __future__ import annotations

import hashlib
import os
import stat
import subprocess
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


def require_repository_root() -> Path:
    repository_root = find_repository_root()
    if repository_root is None:
        pytest.skip("repository-level deployment files are not mounted in this test environment")
    return repository_root


def create_fake_compose(tmp_path: Path) -> Path:
    fake_compose = tmp_path / "fake-compose.sh"
    fake_compose.write_text(
        """#!/usr/bin/env sh
set -eu
{
    printf 'args:'
    for arg in "$@"; do
        printf ' [%s]' "$arg"
    done
    printf '\\n'
} >> "$FAKE_COMPOSE_LOG"

case "$*" in
    *pg_dump*)
        printf 'fake custom postgres dump\\n'
        ;;
    *pg_restore*)
        cat > "$FAKE_RESTORE_CAPTURE"
        ;;
    *)
        echo "unexpected fake compose invocation: $*" >&2
        exit 64
        ;;
esac
""",
        encoding="utf-8",
    )
    fake_compose.chmod(0o700)
    return fake_compose


def script_environment(tmp_path: Path, fake_compose: Path) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "COMPOSE": str(fake_compose),
            "ENV_FILE": "fake.env",
            "FAKE_COMPOSE_LOG": str(tmp_path / "compose.log"),
            "FAKE_RESTORE_CAPTURE": str(tmp_path / "restore.capture"),
        }
    )
    return environment


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


def test_postgres_backup_script_writes_dump_checksum_and_restricted_permissions(
    tmp_path: Path,
) -> None:
    repository_root = require_repository_root()
    fake_compose = create_fake_compose(tmp_path)
    backup_file = tmp_path / "recovery-test.dump"

    result = subprocess.run(  # noqa: S603
        [
            str(repository_root / "scripts/postgres-backup.sh"),
            "--output",
            str(backup_file),
        ],
        cwd=repository_root,
        env=script_environment(tmp_path, fake_compose),
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert backup_file.read_bytes() == b"fake custom postgres dump\n"
    assert stat.S_IMODE(backup_file.stat().st_mode) == 0o600

    checksum_file = backup_file.with_suffix(".dump.sha256")
    expected_digest = hashlib.sha256(backup_file.read_bytes()).hexdigest()
    assert checksum_file.read_text(encoding="utf-8") == f"{expected_digest}  {backup_file}\n"
    assert stat.S_IMODE(checksum_file.stat().st_mode) == 0o600

    compose_log = (tmp_path / "compose.log").read_text(encoding="utf-8")
    assert "args: [--env-file] [fake.env] [exec] [-T] [postgres]" in compose_log
    assert "pg_dump" in compose_log


def test_postgres_backup_script_removes_temporary_dump_after_failure(tmp_path: Path) -> None:
    repository_root = require_repository_root()
    failing_compose = tmp_path / "failing-compose.sh"
    failing_compose.write_text(
        """#!/usr/bin/env sh
set -eu
printf 'failing compose invoked\\n' >> "$FAKE_COMPOSE_LOG"
exit 42
""",
        encoding="utf-8",
    )
    failing_compose.chmod(0o700)
    backup_file = tmp_path / "failed-recovery-test.dump"

    result = subprocess.run(  # noqa: S603
        [
            str(repository_root / "scripts/postgres-backup.sh"),
            "--output",
            str(backup_file),
        ],
        cwd=repository_root,
        env=script_environment(tmp_path, failing_compose),
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 42
    assert not backup_file.exists()
    assert not backup_file.with_suffix(".dump.tmp").exists()
    assert not backup_file.with_suffix(".dump.sha256").exists()


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


def test_postgres_restore_script_streams_selected_dump_to_pg_restore(tmp_path: Path) -> None:
    repository_root = require_repository_root()
    fake_compose = create_fake_compose(tmp_path)
    backup_file = tmp_path / "selected-recovery-test.dump"
    backup_file.write_bytes(b"custom dump selected for recovery\n")
    environment = script_environment(tmp_path, fake_compose)
    environment["RESTORE_CONFIRM"] = "replace"

    result = subprocess.run(  # noqa: S603
        [
            str(repository_root / "scripts/postgres-restore.sh"),
            str(backup_file),
        ],
        cwd=repository_root,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "restore.capture").read_bytes() == b"custom dump selected for recovery\n"

    compose_log = (tmp_path / "compose.log").read_text(encoding="utf-8")
    assert "args: [--env-file] [fake.env] [exec] [-T] [postgres]" in compose_log
    assert "pg_restore" in compose_log
    assert "--single-transaction" in compose_log
    assert "--exit-on-error" in compose_log


def test_postgres_restore_script_refuses_unconfirmed_recovery_before_compose(
    tmp_path: Path,
) -> None:
    repository_root = require_repository_root()
    fake_compose = create_fake_compose(tmp_path)
    backup_file = tmp_path / "unconfirmed-recovery-test.dump"
    backup_file.write_bytes(b"custom dump\n")

    result = subprocess.run(  # noqa: S603
        [
            str(repository_root / "scripts/postgres-restore.sh"),
            str(backup_file),
        ],
        cwd=repository_root,
        env=script_environment(tmp_path, fake_compose),
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 1
    assert "RESTORE_CONFIRM=replace" in result.stderr
    assert not (tmp_path / "compose.log").exists()


def test_database_docs_include_operator_backup_and_restore_flow() -> None:
    docs = read_repository_file("db/README.md")

    assert "make db-backup" in docs
    assert "make db-restore" in docs
    assert "RESTORE_CONFIRM=replace" in docs
    assert "sha256" in docs
    assert "application master" in docs
    assert "key is not stored in PostgreSQL" in docs
