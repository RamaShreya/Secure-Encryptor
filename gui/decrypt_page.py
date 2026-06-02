from __future__ import annotations

import logging
import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from crypto.decrypt import DecryptionError, decrypt_file
from gui.animations import BG, CYAN, MUTED, TEXT, WARNING, animate_progress
from gui.components import GlassCard, NeonButton
from gui.file_panel import FilePanel


class DecryptPage(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color=BG)
        self.app = app
        self.files: list[Path] = []
        self.output_dir = ctk.StringVar(value=str(app.base_dir / "decrypted_files"))
        self.key_file = ctk.StringVar()
        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Decrypt File", text_color=TEXT, font=ctk.CTkFont(size=30, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        self.file_panel = FilePanel(self, "📂 Select Encrypted File", self._set_files)
        self.file_panel.grid(row=1, column=0, sticky="nsew", pady=(20, 0), padx=(0, 10))

        controls = GlassCard(self)
        controls.grid(row=1, column=1, sticky="nsew", pady=(20, 0), padx=(10, 0))
        ctk.CTkLabel(controls, text="Decryption Controls", text_color=TEXT, font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=22, pady=(22, 16))
        ctk.CTkLabel(controls, text="Decrypted file output folder", text_color=MUTED).pack(anchor="w", padx=22)
        ctk.CTkEntry(controls, textvariable=self.output_dir, height=42, fg_color="#0B1020", border_color=CYAN).pack(fill="x", padx=22)
        NeonButton(controls, text="📁 Select Output Folder", command=self._choose_output, fg_color="#111827").pack(fill="x", padx=22, pady=(10, 14))
        ctk.CTkLabel(controls, text="Matching .key file", text_color=MUTED).pack(anchor="w", padx=22)
        ctk.CTkEntry(controls, textvariable=self.key_file, height=42, fg_color="#0B1020", border_color=WARNING).pack(fill="x", padx=22)
        NeonButton(controls, text="🗝 Select Key File", command=self._choose_key_file, fg_color="#111827").pack(fill="x", padx=22, pady=(10, 16))
        ctk.CTkLabel(
            controls,
            text="Select the exact .key file created during encryption. Without it, encrypted files cannot be recovered.",
            text_color=WARNING,
            wraplength=380,
            justify="left",
        ).pack(anchor="w", padx=22, pady=(0, 18))
        self.progress = ctk.CTkProgressBar(controls, height=16, progress_color=CYAN)
        self.progress.pack(fill="x", padx=22, pady=(0, 18))
        self.progress.set(0)
        NeonButton(controls, text="🔓 Decrypt File", command=self._decrypt).pack(fill="x", padx=22, pady=(0, 10))
        NeonButton(controls, text="Clear", command=self.clear, fg_color="#111827").pack(fill="x", padx=22, pady=(0, 10))
        NeonButton(controls, text="Cancel", command=lambda: self.app.notify("No active job to cancel.", "warning"), fg_color="#2B1B3F").pack(fill="x", padx=22, pady=(0, 22))

    def _set_files(self, files: list[Path]) -> None:
        self.files = files

    def _choose_output(self) -> None:
        path = filedialog.askdirectory(title="Select decrypted output folder")
        if path:
            self.output_dir.set(path)

    def _choose_key_file(self) -> None:
        path = filedialog.askopenfilename(title="Select key file", filetypes=(("Key files", "*.key"), ("All files", "*.*")))
        if path:
            self.key_file.set(path)

    def _decrypt(self) -> None:
        if not self.files:
            self.app.notify("Select one or more .enc files.", "warning")
            return
        if not self.key_file.get():
            self.app.notify("Select the matching .key file.", "warning")
            return
        self.app.notify("Decryption started.", "info")
        threading.Thread(target=self._run_decrypt, daemon=True).start()

    def _run_decrypt(self) -> None:
        completed = 0
        total = len(self.files)
        for index, path in enumerate(self.files, start=1):
            try:
                def progress(value: int, index: int = index) -> None:
                    target = (((index - 1) / total) + (value / 100 / total))
                    self.after(0, animate_progress, self.progress, target)
                result = decrypt_file(path, self.key_file.get(), self.output_dir.get(), self.app.database, progress)
                completed += 1
                self.after(0, self.app.notify, f"Decrypted: {result.name}", "success")
            except (DecryptionError, OSError, ValueError) as exc:
                logging.exception("Decryption failed")
                self.app.database.record_decryption(
                    filename=path.name,
                    status="failed",
                    source_path=path,
                    output_path=None,
                    file_size=path.stat().st_size if path.exists() else None,
                    sha256=None,
                )
                self.after(0, self.app.notify, f"{path.name}: {exc}", "error")
        self.after(0, animate_progress, self.progress, 1.0)
        self.after(0, self.app.notify, f"Decryption complete: {completed}/{total} file(s).", "success")

    def clear(self) -> None:
        self.file_panel.clear()
        self.key_file.set("")
        self.progress.set(0)
