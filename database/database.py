from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


class EncryptionDatabase:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS encrypted_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    filetype TEXT,
                    timestamp TEXT NOT NULL,
                    encryption_status TEXT NOT NULL,
                    source_path TEXT,
                    output_path TEXT,
                    key_file_path TEXT,
                    file_size INTEGER,
                    sha256 TEXT,
                    nonce_b64 TEXT,
                    encryption_version INTEGER DEFAULT 2
                );

                CREATE TABLE IF NOT EXISTS decrypted_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    decryption_status TEXT NOT NULL,
                    source_path TEXT,
                    output_path TEXT,
                    file_size INTEGER,
                    sha256 TEXT
                );

                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT,
                    detail TEXT
                );
                """
            )
            self._migrate_encrypted_files(connection)

    def _migrate_encrypted_files(self, connection: sqlite3.Connection) -> None:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(encrypted_files)").fetchall()
        }
        desired = {
            "id",
            "filename",
            "filetype",
            "timestamp",
            "encryption_status",
            "source_path",
            "output_path",
            "key_file_path",
            "file_size",
            "sha256",
            "nonce_b64",
            "encryption_version",
        }
        if columns == desired:
            return

        connection.executescript(
            """
            ALTER TABLE encrypted_files RENAME TO encrypted_files_legacy;

            CREATE TABLE encrypted_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filetype TEXT,
                timestamp TEXT NOT NULL,
                encryption_status TEXT NOT NULL,
                source_path TEXT,
                output_path TEXT,
                key_file_path TEXT,
                file_size INTEGER,
                sha256 TEXT,
                nonce_b64 TEXT,
                encryption_version INTEGER DEFAULT 2
            );
            """
        )
        legacy_columns = columns
        select_key_file = "key_file_path" if "key_file_path" in legacy_columns else "NULL"
        select_nonce = "nonce_b64" if "nonce_b64" in legacy_columns else "NULL"
        select_version = (
            "encryption_version" if "encryption_version" in legacy_columns else "1"
        )
        connection.execute(
            f"""
            INSERT INTO encrypted_files (
                id, filename, filetype, timestamp, encryption_status, source_path,
                output_path, key_file_path, file_size, sha256, nonce_b64, encryption_version
            )
            SELECT
                id, filename, filetype, timestamp, encryption_status, source_path,
                output_path, {select_key_file}, file_size, sha256, {select_nonce}, {select_version}
            FROM encrypted_files_legacy
            """
        )
        connection.execute("DROP TABLE encrypted_files_legacy")

    def _now(self) -> str:
        return datetime.now(IST).isoformat()

    def format_timestamp(self, timestamp: str) -> str:
        try:
            parsed = datetime.fromisoformat(timestamp)
        except ValueError:
            return timestamp[:19]
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=IST)
        return parsed.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S")

    def record_activity(self, activity: str, status: str = "info", detail: str = "") -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO activity_logs (activity, timestamp, status, detail)
                VALUES (?, ?, ?, ?)
                """,
                (activity, self._now(), status, detail),
            )

    def record_encryption(
        self,
        *,
        filename: str,
        filetype: str,
        status: str,
        source_path: Path,
        output_path: Path | None,
        file_size: int | None,
        sha256: str | None,
        key_file_path: Path | None = None,
        nonce_b64: str | None = None,
        encryption_version: int = 2,
    ) -> None:
        now = self._now()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO encrypted_files (
                    filename, filetype, timestamp, encryption_status, source_path,
                    output_path, key_file_path, file_size, sha256, nonce_b64, encryption_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    filename,
                    filetype,
                    now,
                    status,
                    str(source_path),
                    str(output_path) if output_path else None,
                    str(key_file_path) if key_file_path else None,
                    file_size,
                    sha256,
                    nonce_b64,
                    encryption_version,
                ),
            )
            connection.execute(
                """
                INSERT INTO activity_logs (activity, timestamp, status, detail)
                VALUES (?, ?, ?, ?)
                """,
                ("Encrypted file", now, status, filename),
            )

    def record_decryption(
        self,
        *,
        filename: str,
        status: str,
        source_path: Path,
        output_path: Path | None,
        file_size: int | None,
        sha256: str | None,
    ) -> None:
        now = self._now()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO decrypted_files (
                    filename, timestamp, decryption_status, source_path,
                    output_path, file_size, sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    filename,
                    now,
                    status,
                    str(source_path),
                    str(output_path) if output_path else None,
                    file_size,
                    sha256,
                ),
            )
            connection.execute(
                """
                INSERT INTO activity_logs (activity, timestamp, status, detail)
                VALUES (?, ?, ?, ?)
                """,
                ("Decrypted file", now, status, filename),
            )

    def stats(self) -> dict[str, int]:
        with self.connect() as connection:
            encrypted = connection.execute(
                "SELECT COUNT(*) FROM encrypted_files WHERE encryption_status = 'success'"
            ).fetchone()[0]
            decrypted = connection.execute(
                "SELECT COUNT(*) FROM decrypted_files WHERE decryption_status = 'success'"
            ).fetchone()[0]
            activities = connection.execute("SELECT COUNT(*) FROM activity_logs").fetchone()[0]
        return {
            "encrypted": int(encrypted),
            "decrypted": int(decrypted),
            "activities": int(activities),
        }

    def recent_activity(self, limit: int = 12) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT activity, timestamp, status, detail
                FROM activity_logs
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]
