from __future__ import annotations

from os import urandom

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


class Argon2idApiKeyHasher:
    _SALT_SIZE_BYTES = 16
    _HASH_SIZE_BYTES = 32
    _ITERATIONS = 3
    _LANES = 4
    _MEMORY_COST_KIB = 64 * 1024

    def hash(self, api_key: str) -> str:
        kdf = Argon2id(
            salt=urandom(self._SALT_SIZE_BYTES),
            length=self._HASH_SIZE_BYTES,
            iterations=self._ITERATIONS,
            lanes=self._LANES,
            memory_cost=self._MEMORY_COST_KIB,
        )
        return kdf.derive_phc_encoded(api_key.encode())

    def verify(self, api_key: str, hashed_key: str) -> bool:
        try:
            Argon2id.verify_phc_encoded(api_key.encode(), hashed_key)
        except (InvalidKey, ValueError):
            return False
        return True
