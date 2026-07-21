from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from domain.secret_version.value_objects import SecretVersionId


def test_secret_version_id_generates_uuid() -> None:
    secret_version_id = SecretVersionId.new()

    assert isinstance(secret_version_id.value, UUID)


def test_secret_version_id_can_be_created_from_string() -> None:
    value = "edbb44ee-7e6c-48cd-a3e5-60970c853a73"

    secret_version_id = SecretVersionId.from_string(value)

    assert str(secret_version_id) == value


def test_secret_version_id_is_immutable() -> None:
    secret_version_id = SecretVersionId.new()

    with pytest.raises(FrozenInstanceError):
        secret_version_id.__setattr__(
            "value",
            UUID("edbb44ee-7e6c-48cd-a3e5-60970c853a73"),
        )
