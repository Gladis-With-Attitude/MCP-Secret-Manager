from __future__ import annotations

from datetime import UTC

from domain.secret.value_objects import SecretId
from domain.secret_version.entities import SecretVersion
from domain.secret_version.value_objects import (
    SecretValue,
    SecretVersionId,
    SecretVersionNumber,
)


def test_secret_version_create_assigns_id_active_state_and_created_at() -> None:
    secret_id = SecretId.new()

    secret_version = SecretVersion.create(
        secret_id=secret_id,
        value=SecretValue("plain-value"),
        version=SecretVersionNumber(1),
    )

    assert isinstance(secret_version.id, SecretVersionId)
    assert secret_version.secret_id == secret_id
    assert secret_version.value == SecretValue("plain-value")
    assert secret_version.version == SecretVersionNumber(1)
    assert secret_version.active is True
    assert secret_version.created_at.tzinfo == UTC


def test_secret_version_deactivate_returns_inactive_copy() -> None:
    secret_version = SecretVersion.create(
        secret_id=SecretId.new(),
        value=SecretValue("plain-value"),
        version=SecretVersionNumber(1),
    )

    inactive = secret_version.deactivate()

    assert secret_version.active is True
    assert inactive.active is False
    assert inactive.id == secret_version.id


def test_secret_versions_are_equal_when_their_ids_are_equal() -> None:
    secret_version_id = SecretVersionId.new()
    first = SecretVersion(
        id=secret_version_id,
        secret_id=SecretId.new(),
        value=SecretValue("first"),
        version=SecretVersionNumber(1),
        active=True,
        created_at=SecretVersion.create(
            secret_id=SecretId.new(),
            value=SecretValue("created"),
            version=SecretVersionNumber(1),
        ).created_at,
    )
    second = SecretVersion(
        id=secret_version_id,
        secret_id=SecretId.new(),
        value=SecretValue("second"),
        version=SecretVersionNumber(2),
        active=False,
        created_at=first.created_at,
    )

    assert first == second
    assert hash(first) == hash(second)
