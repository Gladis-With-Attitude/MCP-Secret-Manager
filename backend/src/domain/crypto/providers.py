from __future__ import annotations

from typing import Protocol

from domain.crypto.entities import EncryptedSecretValue, SecretEncryptionContext
from domain.secret_version.value_objects import SecretValue


class CryptoProvider(Protocol):
    def encrypt_secret_value(
        self,
        value: SecretValue,
        context: SecretEncryptionContext,
    ) -> EncryptedSecretValue:
        raise NotImplementedError

    def decrypt_secret_value(
        self,
        encrypted_value: EncryptedSecretValue,
        context: SecretEncryptionContext,
    ) -> SecretValue:
        raise NotImplementedError
