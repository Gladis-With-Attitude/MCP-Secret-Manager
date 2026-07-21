from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from domain.secret.value_objects import SecretId


def test_secret_id_generates_uuid() -> None:
    secret_id = SecretId.new()

    assert isinstance(secret_id.value, UUID)


def test_secret_id_can_be_created_from_string() -> None:
    value = "7eb17f4c-2256-4095-bac1-507c82f0a52a"

    secret_id = SecretId.from_string(value)

    assert str(secret_id) == value


def test_secret_id_is_immutable() -> None:
    secret_id = SecretId.new()

    with pytest.raises(FrozenInstanceError):
        secret_id.__setattr__("value", UUID("7eb17f4c-2256-4095-bac1-507c82f0a52a"))
