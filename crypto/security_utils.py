from __future__ import annotations

import hashlib
import logging
import shutil
from pathlib import Path


SUPPORTED_DISPLAY_TYPES = (
    ("All files", "*.*"),
    ("Encrypted files", "*.enc"),
    ("Documents", "*.pdf *.txt *.docx *.xlsx *.pptx *.csv"),
    ("Images", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
    ("Videos", "*.mp4 *.avi *.mkv *.mov"),
    ("Archives", "*.zip *.rar *.7z"),
)


def ensure_directories(base_dir: Path) -> None:
    for relative in (
        "encrypted_files",
        "decrypted_files",
        "keys",
        "logs",
        "database",
        "temp",
        "assets/icons",
        "assets/images",
        "assets/themes",
        "docs",
        "screenshots",
    ):
        (base_dir / relative).mkdir(parents=True, exist_ok=True)


def cleanup_temp_files(base_dir: Path) -> None:
    temp_dir = base_dir / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    for item in temp_dir.iterdir():
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        except OSError:
            logging.exception("Unable to clean temporary item: %s", item)


def validate_file(path: str | Path) -> Path:
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError("Selected file does not exist.")
    if not file_path.is_file():
        raise ValueError("Selected path is not a file.")
    if file_path.stat().st_size == 0:
        raise ValueError("Selected file is empty.")
    try:
        with file_path.open("rb"):
            pass
    except OSError as exc:
        raise OSError(f"Selected file cannot be read: {exc}") from exc
    return file_path


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def human_file_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} {unit}"
        value /= 1024
    return f"{size} B"


def unique_output_path(directory: Path, filename: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / filename
    if not target.exists():
        return target

    stem = target.stem
    suffix = target.suffix
    counter = 1
    while True:
        candidate = directory / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def remove_enc_suffix(path: Path) -> str:
    if path.name.lower().endswith(".enc"):
        return path.name[:-4]
    return f"{path.stem}.decrypted"


def detect_file_type(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if not suffix:
        return "Binary"
    return suffix.upper()
