from __future__ import annotations


class CryptoProviderError(RuntimeError):
    """Raised when a cryptographic operation cannot be completed safely."""


class CryptoConfigurationError(CryptoProviderError):
    """Raised when cryptographic configuration is missing or invalid."""


class CryptoDecryptionError(CryptoProviderError):
    """Raised when encrypted data cannot be authenticated or decrypted."""
