from __future__ import annotations

import pytest

from domain.secret.exceptions import SecretKeyError
from domain.secret.value_objects import SecretKey


def test_secret_key_accepts_uppercase_digits_and_underscore() -> None:
    key = SecretKey("OPENAI_API_KEY_1")

    assert key.value == "OPENAI_API_KEY_1"


def test_secret_key_rejects_empty_value() -> None:
    with pytest.raises(SecretKeyError, match="required"):
        SecretKey("")


def test_secret_key_rejects_values_shorter_than_three_characters() -> None:
    with pytest.raises(SecretKeyError, match="at least 3"):
        SecretKey("AB")


def test_secret_key_rejects_values_longer_than_one_hundred_twenty_eight_characters() -> None:
    with pytest.raises(SecretKeyError, match="at most 128"):
        SecretKey("A" * 129)


def test_secret_key_rejects_lowercase_characters() -> None:
    with pytest.raises(SecretKeyError, match="A-Z"):
        SecretKey("openai_API_KEY")


def test_secret_key_rejects_hyphen_and_spaces() -> None:
    with pytest.raises(SecretKeyError, match="A-Z"):
        SecretKey("OPENAI-API-KEY")

    with pytest.raises(SecretKeyError, match="A-Z"):
        SecretKey(" OPENAI_API_KEY ")


def test_secret_key_accepts_boundary_lengths() -> None:
    assert SecretKey("ABC").value == "ABC"
    assert SecretKey("A" * 128).value == "A" * 128
