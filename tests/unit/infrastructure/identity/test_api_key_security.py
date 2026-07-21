from __future__ import annotations

from infrastructure.identity import Argon2idApiKeyHasher, SecureApiKeySecretGenerator


def test_secure_api_key_generator_creates_server_sized_key_and_extractable_prefix() -> None:
    generator = SecureApiKeySecretGenerator()

    api_key = generator.generate()
    key_prefix = generator.extract_prefix(api_key)

    assert api_key.startswith("mcp_sm_")
    assert len(api_key) == 88
    assert key_prefix is not None
    assert len(key_prefix) == 23
    assert api_key.startswith(f"{key_prefix}_")


def test_argon2id_api_key_hasher_hashes_and_verifies_without_storing_plain_key() -> None:
    hasher = Argon2idApiKeyHasher()
    api_key = SecureApiKeySecretGenerator().generate()

    hashed_key = hasher.hash(api_key)

    assert hashed_key.startswith("$argon2id$")
    assert api_key not in hashed_key
    assert hasher.verify(api_key, hashed_key) is True
    assert hasher.verify(f"{api_key}wrong", hashed_key) is False
