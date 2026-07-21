from __future__ import annotations

from base64 import b64decode
from binascii import Error as Base64DecodeError
from os import urandom

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from domain.crypto.entities import EncryptedSecretValue, SecretEncryptionContext
from domain.crypto.exceptions import CryptoConfigurationError, CryptoDecryptionError
from domain.secret_version.value_objects import SecretValue


class AesGcmCryptoProvider:
    _ALGORITHM = "AES-256-GCM"
    _KEY_SIZE_BYTES = 32
    _NONCE_SIZE_BYTES = 12
    _TAG_SIZE_BYTES = 16

    def __init__(self, master_key: bytes, key_version: int = 1) -> None:
        if len(master_key) != self._KEY_SIZE_BYTES:
            msg = "Master key must be exactly 32 bytes for AES-256-GCM."
            raise CryptoConfigurationError(msg)
        if key_version < 1:
            msg = "Master key version must be greater than or equal to 1."
            raise CryptoConfigurationError(msg)

        self._master_key = master_key
        self._key_version = key_version

    @classmethod
    def from_base64_master_key(
        cls,
        master_key_base64: str | None,
        key_version: int = 1,
    ) -> AesGcmCryptoProvider:
        if master_key_base64 is None:
            msg = "Master key is required for secret value encryption."
            raise CryptoConfigurationError(msg)

        try:
            master_key = b64decode(master_key_base64, validate=True)
        except (Base64DecodeError, ValueError) as exc:
            msg = "Master key must be valid base64."
            raise CryptoConfigurationError(msg) from exc

        return cls(master_key=master_key, key_version=key_version)

    def encrypt_secret_value(
        self,
        value: SecretValue,
        context: SecretEncryptionContext,
    ) -> EncryptedSecretValue:
        dek = urandom(self._KEY_SIZE_BYTES)
        value_nonce = urandom(self._NONCE_SIZE_BYTES)
        value_aad = self._build_value_aad(context)
        encrypted_value_with_tag = AESGCM(dek).encrypt(
            value_nonce,
            value.value.encode("utf-8"),
            value_aad,
        )
        encrypted_value = encrypted_value_with_tag[: -self._TAG_SIZE_BYTES]
        authentication_tag = encrypted_value_with_tag[-self._TAG_SIZE_BYTES :]

        encrypted_dek = self._wrap_dek(dek, context)

        return EncryptedSecretValue(
            encrypted_value=encrypted_value,
            encrypted_dek=encrypted_dek,
            nonce=value_nonce,
            authentication_tag=authentication_tag,
            encryption_algorithm=self._ALGORITHM,
            key_version=self._key_version,
        )

    def decrypt_secret_value(
        self,
        encrypted_value: EncryptedSecretValue,
        context: SecretEncryptionContext,
    ) -> SecretValue:
        self._validate_encrypted_value(encrypted_value)
        dek = self._unwrap_dek(encrypted_value.encrypted_dek, context)
        value_aad = self._build_value_aad(context)

        try:
            plaintext = AESGCM(dek).decrypt(
                encrypted_value.nonce,
                encrypted_value.encrypted_value + encrypted_value.authentication_tag,
                value_aad,
            )
        except InvalidTag as exc:
            msg = "Secret value authentication failed."
            raise CryptoDecryptionError(msg) from exc

        return SecretValue(plaintext.decode("utf-8"))

    def _wrap_dek(self, dek: bytes, context: SecretEncryptionContext) -> bytes:
        nonce = urandom(self._NONCE_SIZE_BYTES)
        aad = self._build_dek_aad(context)
        encrypted_dek_with_tag = AESGCM(self._master_key).encrypt(nonce, dek, aad)
        return nonce + encrypted_dek_with_tag

    def _unwrap_dek(self, encrypted_dek: bytes, context: SecretEncryptionContext) -> bytes:
        if len(encrypted_dek) <= self._NONCE_SIZE_BYTES + self._TAG_SIZE_BYTES:
            msg = "Encrypted data encryption key is malformed."
            raise CryptoDecryptionError(msg)

        nonce = encrypted_dek[: self._NONCE_SIZE_BYTES]
        wrapped_dek = encrypted_dek[self._NONCE_SIZE_BYTES :]

        try:
            dek = AESGCM(self._master_key).decrypt(nonce, wrapped_dek, self._build_dek_aad(context))
        except InvalidTag as exc:
            msg = "Data encryption key authentication failed."
            raise CryptoDecryptionError(msg) from exc

        if len(dek) != self._KEY_SIZE_BYTES:
            msg = "Data encryption key has an invalid size."
            raise CryptoDecryptionError(msg)

        return dek

    def _validate_encrypted_value(self, encrypted_value: EncryptedSecretValue) -> None:
        if encrypted_value.encryption_algorithm != self._ALGORITHM:
            msg = "Unsupported encryption algorithm."
            raise CryptoDecryptionError(msg)
        if encrypted_value.key_version != self._key_version:
            msg = "Unsupported key version."
            raise CryptoDecryptionError(msg)
        if len(encrypted_value.nonce) != self._NONCE_SIZE_BYTES:
            msg = "Secret value nonce has an invalid size."
            raise CryptoDecryptionError(msg)
        if len(encrypted_value.authentication_tag) != self._TAG_SIZE_BYTES:
            msg = "Secret value authentication tag has an invalid size."
            raise CryptoDecryptionError(msg)

    def _build_value_aad(self, context: SecretEncryptionContext) -> bytes:
        return self._build_aad(purpose="secret-value", context=context)

    def _build_dek_aad(self, context: SecretEncryptionContext) -> bytes:
        return self._build_aad(purpose="dek-wrap", context=context)

    def _build_aad(self, purpose: str, context: SecretEncryptionContext) -> bytes:
        return (
            f"purpose={purpose};"
            f"secret_id={context.secret_id};"
            f"version={context.version};"
            f"algorithm={self._ALGORITHM};"
            f"key_version={self._key_version}"
        ).encode()
