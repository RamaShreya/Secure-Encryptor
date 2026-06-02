from __future__ import annotations

"""AES-256-GCM encryption using per-file direct secret keys.

Each encryption generates a new random 32-byte key, saves it separately as a
.key file, and stores only non-secret metadata with the encrypted container.
"""

import base64
import json
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from crypto.key_manager import generate_secret_key
from crypto.keyfile_manager import save_key_file
from crypto.security_utils import file_sha256, unique_output_path, validate_file
from database.database import EncryptionDatabase


MAGIC = b"AESFT2"
ENC_VERSION = 2
NONCE_SIZE = 12


@dataclass(frozen=True)
class EncryptionResult:
    encrypted_path: Path
    key_path: Path


def _progress(callback: Callable[[int], None] | None, value: int) -> None:
    if callback:
        callback(value)


def encrypt_file(
    file_path: str | Path,
    output_dir: str | Path,
    key_dir: str | Path,
    database: EncryptionDatabase | None = None,
    progress_callback: Callable[[int], None] | None = None,
) -> EncryptionResult:
    source = validate_file(file_path)
    output_directory = Path(output_dir).expanduser().resolve()
    _progress(progress_callback, 6)

    secret_key = generate_secret_key()
    key_path = save_key_file(secret_key, key_dir, source)
    nonce = secrets.token_bytes(NONCE_SIZE)
    aesgcm = AESGCM(secret_key)
    _progress(progress_callback, 25)

    plaintext = source.read_bytes()
    digest = file_sha256(source)
    _progress(progress_callback, 52)

    metadata = {
        "version": ENC_VERSION,
        "original_name": source.name,
        "original_size": source.stat().st_size,
        "sha256": digest,
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "key_mode": "direct-key-file",
        "cipher": "AES-256-GCM",
    }
    metadata_bytes = json.dumps(metadata, separators=(",", ":")).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, plaintext, metadata_bytes)
    _progress(progress_callback, 78)

    output_path = unique_output_path(output_directory, f"{source.name}.enc")
    with output_path.open("wb") as encrypted:
        encrypted.write(MAGIC)
        encrypted.write(len(metadata_bytes).to_bytes(4, "big"))
        encrypted.write(metadata_bytes)
        encrypted.write(ciphertext)

    if database:
        database.record_encryption(
            filename=source.name,
            filetype=source.suffix.lower() or "binary",
            status="success",
            source_path=source,
            output_path=output_path,
            key_file_path=key_path,
            file_size=source.stat().st_size,
            sha256=digest,
            nonce_b64=base64.b64encode(nonce).decode("ascii"),
            encryption_version=ENC_VERSION,
        )

    _progress(progress_callback, 100)
    return EncryptionResult(encrypted_path=output_path, key_path=key_path)
