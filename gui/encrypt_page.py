from __future__ import annotations

import logging
import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from crypto.encrypt import encrypt_file
from gui.animations import BG, CYAN, MUTED, TEXT, WARNING, animate_progress
from gui.components import GlassCard, NeonButton
from gui.file_panel import FilePanel


class EncryptPage(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color=BG)
        self.app = app
        self.files: list[Path] = []
        self.output_dir = ctk.StringVar(value=str(app.base_dir / "encrypted_files"))
        self.key_dir = ctk.StringVar(value=str(app.base_dir / "keys"))
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Encrypt File", text_color=TEXT, font=ctk.CTkFont(size=30, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        self.file_panel = FilePanel(self, "📂 Select File", self._set_files)
        self.file_panel.grid(row=1, column=0, sticky="nsew", pady=(20, 0), padx=(0, 10))

        controls = GlassCard(self)
        controls.grid(row=1, column=1, sticky="nsew", pady=(20, 0), padx=(10, 0))
        ctk.CTkLabel(controls, text="Encryption Controls", text_color=TEXT, font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=22, pady=(22, 16))
        ctk.CTkLabel(controls, text="Encrypted file output folder", text_color=MUTED).pack(anchor="w", padx=22)
        ctk.CTkEntry(controls, textvariable=self.output_dir, height=42, fg_color="#0B1020", border_color=CYAN).pack(fill="x", padx=22)
        NeonButton(controls, text="📁 Select Output Folder", command=self._choose_output, fg_color="#111827").pack(fill="x", padx=22, pady=(10, 14))

        ctk.CTkLabel(controls, text="Key file save folder", text_color=MUTED).pack(anchor="w", padx=22)
        ctk.CTkEntry(controls, textvariable=self.key_dir, height=42, fg_color="#0B1020", border_color=WARNING).pack(fill="x", padx=22)
        NeonButton(controls, text="🗝 Generate Key Folder", command=self._choose_key_dir, fg_color="#111827").pack(fill="x", padx=22, pady=(10, 16))
        ctk.CTkLabel(
            controls,
            text="Keep your .key file safe. Without the key file, encrypted files cannot be recovered. Do not share your key file.",
            text_color=WARNING,
            wraplength=380,
            justify="left",
        ).pack(anchor="w", padx=22, pady=(0, 18))

        self.progress = ctk.CTkProgressBar(controls, height=16, progress_color=CYAN)
        self.progress.pack(fill="x", padx=22, pady=(0, 18))
        self.progress.set(0)
        NeonButton(controls, text="🔒 Encrypt File", command=self._encrypt).pack(fill="x", padx=22, pady=(0, 10))
        NeonButton(controls, text="Clear", command=self.clear, fg_color="#111827").pack(fill="x", padx=22, pady=(0, 10))
        NeonButton(controls, text="Cancel", command=lambda: self.app.notify("No active job to cancel.", "warning"), fg_color="#2B1B3F").pack(fill="x", padx=22, pady=(0, 22))

    def _set_files(self, files: list[Path]) -> None:
        self.files = files

    def _choose_output(self) -> None:
        path = filedialog.askdirectory(title="Select encrypted output folder")
        if path:
            self.output_dir.set(path)

    def _choose_key_dir(self) -> None:
        path = filedialog.askdirectory(title="Select key file save folder")
        if path:
            self.key_dir.set(path)

    def _encrypt(self) -> None:
        if not self.files:
            self.app.notify("Select at least one file to encrypt.", "warning")
            return
        if not self.key_dir.get():
            self.app.notify("Select a folder where the .key file will be saved.", "warning")
            return
        self.app.notify("Encryption started.", "info")
        threading.Thread(target=self._run_encrypt, daemon=True).start()

    def _run_encrypt(self) -> None:
        completed = 0
        total = len(self.files)
        for index, path in enumerate(self.files, start=1):
            try:
                def progress(value: int, index: int = index) -> None:
                    target = (((index - 1) / total) + (value / 100 / total))
                    self.after(0, animate_progress, self.progress, target)
                result = encrypt_file(path, self.output_dir.get(), self.key_dir.get(), self.app.database, progress)
                completed += 1
                self.after(0, self.app.notify, f"Encrypted: {result.encrypted_path.name} | Key: {result.key_path.name}", "success")
            except Exception as exc:
                logging.exception("Encryption failed")
                self.app.database.record_encryption(
                    filename=path.name,
                    filetype=path.suffix.lower(),
                    status="failed",
                    source_path=path,
                    output_path=None,
                    file_size=path.stat().st_size if path.exists() else None,
                    sha256=None,
                )
                self.after(0, self.app.notify, f"{path.name}: {exc}", "error")
        self.after(0, animate_progress, self.progress, 1.0)
        self.after(0, self.app.notify, f"Encryption complete: {completed}/{total} file(s).", "success")

    def clear(self) -> None:
        self.file_panel.clear()
        self.progress.set(0)
