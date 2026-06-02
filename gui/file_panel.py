from __future__ import annotations

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from crypto.security_utils import SUPPORTED_DISPLAY_TYPES, detect_file_type, human_file_size, validate_file
from gui.animations import CYAN, MUTED, NEON_BLUE, TEXT, pulse_widget
from gui.components import GlassCard, NeonButton


class FilePanel(GlassCard):
    def __init__(self, master, title: str, on_files_changed) -> None:
        super().__init__(master, border_color=NEON_BLUE)
        self.on_files_changed = on_files_changed
        self.files: list[Path] = []
        self.title_label = ctk.CTkLabel(self, text=title, text_color=TEXT, font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.pack(anchor="w", padx=22, pady=(20, 6))
        self.drop_label = ctk.CTkLabel(
            self,
            text="Drop files here or browse securely",
            text_color=CYAN,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.drop_label.pack(padx=22, pady=(22, 6))
        self.meta_label = ctk.CTkLabel(self, text="Any extension supported", text_color=MUTED)
        self.meta_label.pack(padx=22, pady=(0, 16))
        NeonButton(self, text="📂 Select File", command=self.browse).pack(padx=22, pady=(0, 20), fill="x")
        self.preview = ctk.CTkTextbox(self, height=116, fg_color="#0B1020", text_color=TEXT, corner_radius=14)
        self.preview.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        self.preview.insert("1.0", "No files selected.")
        self.preview.configure(state="disabled")
        self._enable_drop()
        pulse_widget(self, (NEON_BLUE, "#314A86", CYAN))

    def _enable_drop(self) -> None:
        try:
            self.drop_target_register("DND_Files")
            self.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            return

    def _on_drop(self, event) -> None:
        raw = self.tk.splitlist(event.data)
        self.set_files([Path(item) for item in raw])

    def browse(self) -> None:
        paths = filedialog.askopenfilenames(title="Select files", filetypes=SUPPORTED_DISPLAY_TYPES)
        if paths:
            self.set_files([Path(path) for path in paths])

    def set_files(self, files: list[Path]) -> None:
        valid_files: list[Path] = []
        rejected: list[str] = []
        for path in files:
            try:
                valid_files.append(validate_file(path))
            except (FileNotFoundError, OSError, ValueError) as exc:
                rejected.append(f"{Path(path).name}: {exc}")

        if rejected:
            self.winfo_toplevel().notify("\n".join(rejected), "error")

        self.files = valid_files
        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        lines = []
        total_size = 0
        for path in valid_files:
            size = path.stat().st_size if path.exists() else 0
            total_size += size
            lines.append(f"{path.name} | {detect_file_type(path)} | {human_file_size(size)}")
        self.preview.insert("1.0", "\n".join(lines) if lines else "No files selected.")
        self.preview.configure(state="disabled")
        self.meta_label.configure(text=f"{len(valid_files)} file(s) | {human_file_size(total_size)}")
        self.on_files_changed(valid_files)

    def clear(self) -> None:
        self.set_files([])
