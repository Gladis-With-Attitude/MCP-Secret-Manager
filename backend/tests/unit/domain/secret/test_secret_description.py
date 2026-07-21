from __future__ import annotations

from domain.secret.value_objects import SecretDescription


def test_secret_description_accepts_none() -> None:
    description = SecretDescription(None)

    assert description.value is None


def test_secret_description_accepts_text() -> None:
    description = SecretDescription("Used by the API service.")

    assert description.value == "Used by the API service."
