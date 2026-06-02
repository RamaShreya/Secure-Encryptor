from __future__ import annotations

"""Secret-key generation and validation for direct AES-256 encryption."""

import secrets


KEY_SIZE = 32


def generate_secret_key() -> bytes:
    """Generate one cryptographically random AES-256 secret key."""
    return secrets.token_bytes(KEY_SIZE)


def validate_secret_key(key: bytes) -> bytes:
    if not isinstance(key, bytes):
        raise TypeError("Secret key must be bytes.")
    if len(key) != KEY_SIZE:
        raise ValueError("Invalid key file. AES-256 keys must be exactly 32 bytes.")
    return key
