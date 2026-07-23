from __future__ import annotations

from secrets import token_hex


class SecureSessionTokenGenerator:
    _PREFIX_PREFIX = "mcp_sm_session"
    _PREFIX_BYTES = 8
    _SECRET_BYTES = 32

    def generate(self) -> str:
        token_prefix = token_hex(self._PREFIX_BYTES)
        secret = token_hex(self._SECRET_BYTES)
        return f"{self._PREFIX_PREFIX}_{token_prefix}_{secret}"

    def extract_prefix(self, session_token: str) -> str | None:
        parts = session_token.split("_", maxsplit=4)
        if len(parts) != 5:
            return None
        namespace, product, kind, token_prefix, secret = parts
        if namespace != "mcp" or product != "sm" or kind != "session":
            return None
        if len(token_prefix) != self._PREFIX_BYTES * 2:
            return None
        if len(secret) != self._SECRET_BYTES * 2:
            return None
        return f"{namespace}_{product}_{kind}_{token_prefix}"
