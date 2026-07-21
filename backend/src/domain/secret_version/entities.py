from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime

from domain.crypto.entities import EncryptedSecretValue
from domain.secret.value_objects import SecretId
from domain.secret_version.value_objects import (
    SecretVersionId,
    SecretVersionNumber,
)


@dataclass(frozen=True, slots=True, eq=False)
class SecretVersion:
    id: SecretVersionId
    secret_id: SecretId
    encrypted_value: bytes
    encrypted_dek: bytes
    nonce: bytes
    authentication_tag: bytes
    encryption_algorithm: str
    key_version: int
    version: SecretVersionNumber
    active: bool
    created_at: datetime

    @classmethod
    def create(
        cls,
        secret_id: SecretId,
        encrypted_payload: EncryptedSecretValue,
        version: SecretVersionNumber,
    ) -> SecretVersion:
        return cls(
            id=SecretVersionId.new(),
            secret_id=secret_id,
            encrypted_value=encrypted_payload.encrypted_value,
            encrypted_dek=encrypted_payload.encrypted_dek,
            nonce=encrypted_payload.nonce,
            authentication_tag=encrypted_payload.authentication_tag,
            encryption_algorithm=encrypted_payload.encryption_algorithm,
            key_version=encrypted_payload.key_version,
            version=version,
            active=True,
            created_at=datetime.now(UTC),
        )

    def encrypted_payload(self) -> EncryptedSecretValue:
        return EncryptedSecretValue(
            encrypted_value=self.encrypted_value,
            encrypted_dek=self.encrypted_dek,
            nonce=self.nonce,
            authentication_tag=self.authentication_tag,
            encryption_algorithm=self.encryption_algorithm,
            key_version=self.key_version,
        )

    def deactivate(self) -> SecretVersion:
        return replace(self, active=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SecretVersion):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
