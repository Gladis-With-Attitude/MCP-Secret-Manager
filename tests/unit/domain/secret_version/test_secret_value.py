from __future__ import annotations

import pytest

from domain.secret_version.exceptions import SecretValueError
from domain.secret_version.value_objects import SecretValue


def test_secret_value_accepts_non_empty_value() -> None:
    value = SecretValue("sk-test")

    assert value.value == "sk-test"


def test_secret_value_preserves_surrounding_spaces() -> None:
    value = SecretValue("  value  ")

    assert value.value == "  value  "


def test_secret_value_rejects_empty_value() -> None:
    with pytest.raises(SecretValueError, match="required"):
        SecretValue("")
