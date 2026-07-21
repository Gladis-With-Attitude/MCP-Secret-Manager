from __future__ import annotations

from secrets import token_hex


class SecureApiKeySecretGenerator:
    _PREFIX_PREFIX = "mcp_sm"
    _PREFIX_BYTES = 8
    _SECRET_BYTES = 32

    def generate(self) -> str:
        key_prefix = token_hex(self._PREFIX_BYTES)
        secret = token_hex(self._SECRET_BYTES)
        return f"{self._PREFIX_PREFIX}_{key_prefix}_{secret}"

    def extract_prefix(self, api_key: str) -> str | None:
        parts = api_key.split("_", maxsplit=3)
        if len(parts) != 4:
            return None
        namespace, kind, key_prefix, secret = parts
        if namespace != "mcp" or kind != "sm":
            return None
        if len(key_prefix) != self._PREFIX_BYTES * 2:
            return None
        if len(secret) != self._SECRET_BYTES * 2:
            return None
        return f"{namespace}_{kind}_{key_prefix}"
