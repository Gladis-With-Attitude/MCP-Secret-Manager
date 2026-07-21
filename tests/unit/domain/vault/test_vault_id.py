from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from domain.vault.value_objects import VaultId


def test_vault_id_generates_uuid() -> None:
    vault_id = VaultId.new()

    assert isinstance(vault_id.value, UUID)


def test_vault_id_can_be_created_from_string() -> None:
    value = "2fd4fa1e-bf71-4dd7-bba2-b8c41c4e9138"

    vault_id = VaultId.from_string(value)

    assert str(vault_id) == value


def test_vault_id_is_immutable() -> None:
    vault_id = VaultId.new()

    with pytest.raises(FrozenInstanceError):
        vault_id.__setattr__("value", UUID("2fd4fa1e-bf71-4dd7-bba2-b8c41c4e9138"))
