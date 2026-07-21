from __future__ import annotations

from application.crypto.use_cases import DecryptSecretValueUseCase, EncryptSecretValueUseCase
from domain.crypto.entities import EncryptedSecretValue, SecretEncryptionContext
from domain.secret.value_objects import SecretId
from domain.secret_version.entities import SecretVersion
from domain.secret_version.value_objects import SecretValue, SecretVersionNumber


class FakeCryptoProvider:
    def encrypt_secret_value(
        self,
        value: SecretValue,
        _context: SecretEncryptionContext,
    ) -> EncryptedSecretValue:
        return EncryptedSecretValue(
            encrypted_value=f"encrypted:{value.value}".encode(),
            encrypted_dek=b"encrypted-dek",
            nonce=b"0" * 12,
            authentication_tag=b"1" * 16,
            encryption_algorithm="AES-256-GCM",
            key_version=1,
        )

    def decrypt_secret_value(
        self,
        encrypted_value: EncryptedSecretValue,
        _context: SecretEncryptionContext,
    ) -> SecretValue:
        return SecretValue(
            encrypted_value.encrypted_value.decode("utf-8").removeprefix("encrypted:")
        )


def test_encrypt_secret_value_use_case_delegates_to_crypto_provider() -> None:
    use_case = EncryptSecretValueUseCase(FakeCryptoProvider())
    raw_id = str(SecretId.new())

    encrypted = use_case.execute(
        SecretValue("plain-value"),
        SecretEncryptionContext(raw_id, 1),
    )

    assert encrypted.encrypted_value == b"encrypted:plain-value"


def test_decrypt_secret_value_use_case_delegates_to_crypto_provider() -> None:
    provider = FakeCryptoProvider()
    secret_id = SecretId.new()
    encrypted = provider.encrypt_secret_value(
        SecretValue("plain-value"),
        SecretEncryptionContext(str(secret_id), 1),
    )
    secret_version = SecretVersion.create(
        secret_id=secret_id,
        encrypted_payload=encrypted,
        version=SecretVersionNumber(1),
    )

    decrypted = DecryptSecretValueUseCase(provider).execute(secret_version)

    assert decrypted == SecretValue("plain-value")
