from __future__ import annotations

"""AES-256-GCM decryption for version 2 key-file encrypted containers."""

import base64
import json
from pathlib import Path
from typing import Callable

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from crypto.encrypt import ENC_VERSION, MAGIC
from crypto.keyfile_manager import KeyFileError, load_key_file
from crypto.security_utils import file_sha256, remove_enc_suffix, unique_output_path, validate_file
from database.database import EncryptionDatabase


class DecryptionError(Exception):
    pass


def _progress(callback: Callable[[int], None] | None, value: int) -> None:
    if callback:
        callback(value)


def _read_encrypted_container(path: Path) -> tuple[dict[str, object], bytes, bytes]:
    with path.open("rb") as encrypted:
        if encrypted.read(len(MAGIC)) != MAGIC:
            raise DecryptionError("Invalid or unsupported encrypted file format.")

        metadata_length_bytes = encrypted.read(4)
        if len(metadata_length_bytes) != 4:
            raise DecryptionError("Encrypted file metadata is missing or corrupted.")

        metadata_length = int.from_bytes(metadata_length_bytes, "big")
        if metadata_length <= 0 or metadata_length > 1024 * 1024:
            raise DecryptionError("Encrypted file metadata is invalid.")

        metadata_bytes = encrypted.read(metadata_length)
        if len(metadata_bytes) != metadata_length:
            raise DecryptionError("Encrypted file metadata is incomplete.")

        try:
            metadata = json.loads(metadata_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DecryptionError("Encrypted file metadata cannot be read.") from exc

        ciphertext = encrypted.read()
        if not ciphertext:
            raise DecryptionError("Encrypted file payload is missing.")
    return metadata, metadata_bytes, ciphertext


def decrypt_file(
    file_path: str | Path,
    key_file: str | Path,
    output_dir: str | Path,
    database: EncryptionDatabase | None = None,
    progress_callback: Callable[[int], None] | None = None,
) -> Path:
    source = validate_file(file_path)
    output_directory = Path(output_dir).expanduser().resolve()
    _progress(progress_callback, 12)

    metadata, metadata_bytes, ciphertext = _read_encrypted_container(source)
    _progress(progress_callback, 34)

    try:
        nonce = base64.b64decode(str(metadata["nonce"]))
    except (KeyError, ValueError, TypeError) as exc:
        raise DecryptionError("Encrypted file metadata is missing the AES-GCM nonce.") from exc

    version = int(metadata.get("version") or 1)
    if version != ENC_VERSION:
        raise DecryptionError(
            "This file uses the legacy password-based format. "
            "The current app requires version 2 key-file encrypted files."
        )

    try:
        key = load_key_file(key_file)
    except KeyFileError as exc:
        raise DecryptionError(str(exc)) from exc

    aesgcm = AESGCM(key)
    _progress(progress_callback, 58)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, metadata_bytes)
    except InvalidTag as exc:
        raise DecryptionError("Wrong key file or corrupted encrypted file.") from exc

    original_name = str(metadata.get("original_name") or remove_enc_suffix(source))
    output_path = unique_output_path(output_directory, original_name)
    output_path.write_bytes(plaintext)
    _progress(progress_callback, 84)

    restored_hash = file_sha256(output_path)
    expected_hash = str(metadata.get("sha256") or "")
    if expected_hash and restored_hash != expected_hash:
        output_path.unlink(missing_ok=True)
        raise DecryptionError("Restored file failed integrity verification.")

    if database:
        database.record_decryption(
            filename=original_name,
            status="success",
            source_path=source,
            output_path=output_path,
            file_size=output_path.stat().st_size,
            sha256=restored_hash,
        )

    _progress(progress_callback, 100)
    return output_path
