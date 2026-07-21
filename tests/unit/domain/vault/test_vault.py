from __future__ import annotations

from domain.vault.entities import Vault
from domain.vault.value_objects import VaultId, VaultName


def test_vault_create_assigns_an_id_and_name() -> None:
    name = VaultName("Production")

    vault = Vault.create(name)

    assert isinstance(vault.id, VaultId)
    assert vault.name == name


def test_vaults_are_equal_when_their_ids_are_equal() -> None:
    vault_id = VaultId.new()
    first = Vault(id=vault_id, name=VaultName("Production"))
    second = Vault(id=vault_id, name=VaultName("Development"))

    assert first == second
    assert hash(first) == hash(second)


def test_vaults_are_different_when_their_ids_are_different() -> None:
    first = Vault.create(VaultName("Production"))
    second = Vault.create(VaultName("Production"))

    assert first != second
