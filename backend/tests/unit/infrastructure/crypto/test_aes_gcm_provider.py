from __future__ import annotations

from base64 import b64encode
from os import urandom

import pytest

from domain.crypto.entities import EncryptedSecretValue, SecretEncryptionContext
from domain.crypto.exceptions import CryptoConfigurationError, CryptoDecryptionError
from domain.secret.value_objects import SecretId
from domain.secret_version.value_objects import SecretValue
from infrastructure.crypto import AesGcmCryptoProvider


def random_master_key_base64() -> str:
    return b64encode(urandom(32)).decode("ascii")


def build_provider() -> AesGcmCryptoProvider:
    return AesGcmCryptoProvider.from_base64_master_key(random_master_key_base64())


def build_context(version: int = 1) -> SecretEncryptionContext:
    return SecretEncryptionContext(str(SecretId.new()), version)


def test_aes_gcm_provider_encrypts_and_decrypts_secret_value() -> None:
    provider = build_provider()
    context = build_context()

    encrypted = provider.encrypt_secret_value(SecretValue("plain-value"), context)
    decrypted = provider.decrypt_secret_value(encrypted, context)

    assert decrypted == SecretValue("plain-value")
    assert encrypted.encrypted_value != b"plain-value"
    assert encrypted.encrypted_dek != b""
    assert len(encrypted.nonce) == 12
    assert len(encrypted.authentication_tag) == 16
    assert encrypted.encryption_algorithm == "AES-256-GCM"
    assert encrypted.key_version == 1


def test_aes_gcm_provider_rejects_invalid_authentication_tag() -> None:
    provider = build_provider()
    context = build_context()
    encrypted = provider.encrypt_secret_value(SecretValue("plain-value"), context)
    tampered = EncryptedSecretValue(
        encrypted_value=encrypted.encrypted_value,
        encrypted_dek=encrypted.encrypted_dek,
        nonce=encrypted.nonce,
        authentication_tag=b"1" * 16,
        encryption_algorithm=encrypted.encryption_algorithm,
        key_version=encrypted.key_version,
    )

    with pytest.raises(CryptoDecryptionError, match="authentication failed"):
        provider.decrypt_secret_value(tampered, context)


def test_aes_gcm_provider_generates_random_nonces() -> None:
    provider = build_provider()
    context = build_context()

    first = provider.encrypt_secret_value(SecretValue("same-value"), context)
    second = provider.encrypt_secret_value(SecretValue("same-value"), context)

    assert first.nonce != second.nonce


def test_aes_gcm_provider_encrypts_identical_values_to_different_ciphertexts() -> None:
    provider = build_provider()
    context = build_context()

    first = provider.encrypt_secret_value(SecretValue("same-value"), context)
    second = provider.encrypt_secret_value(SecretValue("same-value"), context)

    assert first.encrypted_value != second.encrypted_value
    assert first.encrypted_dek != second.encrypted_dek


def test_aes_gcm_provider_rejects_wrong_master_key() -> None:
    encrypting_provider = build_provider()
    decrypting_provider = build_provider()
    context = build_context()
    encrypted = encrypting_provider.encrypt_secret_value(SecretValue("plain-value"), context)

    with pytest.raises(CryptoDecryptionError, match="authentication failed"):
        decrypting_provider.decrypt_secret_value(encrypted, context)


def test_aes_gcm_provider_rejects_malformed_base64_master_key() -> None:
    with pytest.raises(CryptoConfigurationError, match="valid base64"):
        AesGcmCryptoProvider.from_base64_master_key("not valid base64")


def test_aes_gcm_provider_rejects_invalid_master_key_size() -> None:
    short_key_base64 = b64encode(urandom(16)).decode("ascii")

    with pytest.raises(CryptoConfigurationError, match="32 bytes"):
        AesGcmCryptoProvider.from_base64_master_key(short_key_base64)
