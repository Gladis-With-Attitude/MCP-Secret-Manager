from __future__ import annotations

from dataclasses import dataclass

from domain.crypto.exceptions import CryptoProviderError


@dataclass(frozen=True, slots=True)
class SecretEncryptionContext:
    secret_id: str
    version: int

    def __post_init__(self) -> None:
        if self.secret_id == "":
            msg = "Secret encryption context requires a secret id."
            raise CryptoProviderError(msg)
        if self.version < 1:
            msg = "Secret encryption context version must be greater than or equal to 1."
            raise CryptoProviderError(msg)


@dataclass(frozen=True, slots=True)
class EncryptedSecretValue:
    encrypted_value: bytes
    encrypted_dek: bytes
    nonce: bytes
    authentication_tag: bytes
    encryption_algorithm: str
    key_version: int

    def __post_init__(self) -> None:
        if self.encrypted_value == b"":
            msg = "Encrypted secret value is required."
            raise CryptoProviderError(msg)
        if self.encrypted_dek == b"":
            msg = "Encrypted data encryption key is required."
            raise CryptoProviderError(msg)
        if self.nonce == b"":
            msg = "Secret value nonce is required."
            raise CryptoProviderError(msg)
        if self.authentication_tag == b"":
            msg = "Secret value authentication tag is required."
            raise CryptoProviderError(msg)
        if self.encryption_algorithm == "":
            msg = "Encryption algorithm is required."
            raise CryptoProviderError(msg)
        if self.key_version < 1:
            msg = "Key version must be greater than or equal to 1."
            raise CryptoProviderError(msg)
