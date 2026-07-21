from __future__ import annotations

import pytest

from domain.secret_version.exceptions import SecretVersionNumberError
from domain.secret_version.value_objects import SecretVersionNumber


def test_secret_version_number_accepts_one_or_greater() -> None:
    assert int(SecretVersionNumber(1)) == 1
    assert int(SecretVersionNumber(2)) == 2


def test_secret_version_number_rejects_zero() -> None:
    with pytest.raises(SecretVersionNumberError, match="greater than or equal to 1"):
        SecretVersionNumber(0)


def test_secret_version_number_rejects_negative_value() -> None:
    with pytest.raises(SecretVersionNumberError, match="greater than or equal to 1"):
        SecretVersionNumber(-1)
