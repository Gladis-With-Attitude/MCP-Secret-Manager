from __future__ import annotations

import pytest

from domain.vault.exceptions import VaultNameError
from domain.vault.value_objects import VaultName


def test_vault_name_trims_surrounding_spaces() -> None:
    name = VaultName("  Production  ")

    assert name.value == "Production"


def test_vault_name_rejects_empty_value() -> None:
    with pytest.raises(VaultNameError, match="required"):
        VaultName("   ")


def test_vault_name_rejects_values_shorter_than_three_characters() -> None:
    with pytest.raises(VaultNameError, match="at least 3"):
        VaultName("ab")


def test_vault_name_rejects_values_longer_than_one_hundred_characters() -> None:
    with pytest.raises(VaultNameError, match="at most 100"):
        VaultName("a" * 101)


def test_vault_name_accepts_boundary_lengths() -> None:
    assert VaultName("abc").value == "abc"
    assert VaultName("a" * 100).value == "a" * 100
