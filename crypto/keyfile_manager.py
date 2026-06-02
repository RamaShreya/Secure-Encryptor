from __future__ import annotations

"""Read and write standalone AES key files used by the encryption workflow."""

import base64
import os
from pathlib import Path

from crypto.key_manager import KEY_SIZE, validate_secret_key
from crypto.security_utils import unique_output_path


KEY_FILE_SUFFIX = ".key"


class KeyFileError(Exception):
    pass


def default_key_filename(source: Path) -> str:
    return f"{source.stem}{KEY_FILE_SUFFIX}"


def save_key_file(key: bytes, key_directory: str | Path, source: str | Path) -> Path:
    """Save an AES key as Base64 text in a separate .key file."""
    try:
        validate_secret_key(key)
        directory = Path(key_directory).expanduser().resolve()
        output_path = unique_output_path(directory, default_key_filename(Path(source)))
        output_path.write_text(base64.b64encode(key).decode("ascii"), encoding="ascii")
        try:
            os.chmod(output_path, 0o600)
        except OSError:
            pass
    except OSError as exc:
        raise KeyFileError(f"Unable to save key file: {exc}") from exc
    return output_path


def load_key_file(key_file: str | Path) -> bytes:
    """Load a Base64 or raw-binary AES-256 key file."""
    path = Path(key_file).expanduser().resolve()
    if not path.exists():
        raise KeyFileError("Key file is missing.")
    if not path.is_file():
        raise KeyFileError("Selected key path is not a file.")

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise KeyFileError(f"Unable to read key file: {exc}") from exc

    stripped = raw.strip()
    candidates = [stripped]
    try:
        candidates.insert(0, base64.b64decode(stripped, validate=True))
    except Exception:
        pass

    for candidate in candidates:
        if len(candidate) == KEY_SIZE:
            return validate_secret_key(candidate)

    raise KeyFileError("Invalid or corrupted key file. Expected one AES-256 key.")
