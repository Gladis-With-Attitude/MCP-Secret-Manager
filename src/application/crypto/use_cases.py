from __future__ import annotations

from domain.crypto.entities import EncryptedSecretValue, SecretEncryptionContext
from domain.crypto.providers import CryptoProvider
from domain.secret_version.entities import SecretVersion
from domain.secret_version.value_objects import SecretValue


class EncryptSecretValueUseCase:
    def __init__(self, crypto_provider: CryptoProvider) -> None:
        self._crypto_provider = crypto_provider

    def execute(
        self,
        value: SecretValue,
        context: SecretEncryptionContext,
    ) -> EncryptedSecretValue:
        return self._crypto_provider.encrypt_secret_value(value, context)


class DecryptSecretValueUseCase:
    def __init__(self, crypto_provider: CryptoProvider) -> None:
        self._crypto_provider = crypto_provider

    def execute(self, secret_version: SecretVersion) -> SecretValue:
        return self._crypto_provider.decrypt_secret_value(
            secret_version.encrypted_payload(),
            SecretEncryptionContext(
                secret_id=str(secret_version.secret_id),
                version=secret_version.version.value,
            ),
        )
