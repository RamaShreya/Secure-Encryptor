from __future__ import annotations

import customtkinter as ctk

from gui.animations import BG, CYAN, MUTED, NEON_BLUE, PURPLE, TEXT
from gui.components import GlassCard, NeonButton


class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color=BG)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self, text="History", text_color=TEXT, font=ctk.CTkFont(size=30, weight="bold")).grid(row=0, column=0, sticky="w")
        card = GlassCard(self)
        card.grid(row=1, column=0, sticky="nsew", pady=(20, 0))
        ctk.CTkLabel(card, text="Activity Logs", text_color=TEXT, font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=22, pady=(22, 12))
        self.history_box = ctk.CTkTextbox(card, fg_color="#0B1020", text_color=TEXT, corner_radius=14)
        self.history_box.pack(fill="both", expand=True, padx=22, pady=(0, 22))

    def refresh(self) -> None:
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        rows = self.app.database.recent_activity(50)
        if not rows:
            self.history_box.insert("end", "No activity yet.")
        for row in rows:
            timestamp = self.app.database.format_timestamp(row["timestamp"])
            self.history_box.insert(
                "end",
                f"{timestamp} | {row['status'].upper()} | {row['activity']} | {row['detail']}\n",
            )
        self.history_box.configure(state="disabled")


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color=BG)
        self.app = app
        self.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(self, text="Settings", text_color=TEXT, font=ctk.CTkFont(size=30, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w")

        security = GlassCard(self)
        security.grid(row=1, column=0, sticky="nsew", pady=(20, 0), padx=(0, 10))
        ctk.CTkLabel(security, text="Security Profile", text_color=TEXT, font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=22, pady=(22, 12))
        details = (
            "Cipher: AES-256-GCM\n"
            "Key mode: Direct .key file\n"
            "Key size: 256-bit random per file\n"
            "Nonce: 96-bit random per file\n"
            "Integrity: GCM authentication tag"
        )
        ctk.CTkLabel(security, text=details, text_color=CYAN, justify="left").pack(anchor="w", padx=22, pady=(0, 22))

        future = GlassCard(self)
        future.grid(row=1, column=1, sticky="nsew", pady=(20, 0), padx=(10, 0))
        ctk.CTkLabel(future, text="Scalability Hooks", text_color=TEXT, font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=22, pady=(22, 12))
        ctk.CTkLabel(
            future,
            text="Prepared modules for authentication, cloud encryption, secure sharing, folder encryption, and API integrations.",
            text_color=MUTED,
            justify="left",
            wraplength=360,
        ).pack(anchor="w", padx=22, pady=(0, 18))
        NeonButton(future, text="Open Dashboard", command=lambda: self.app.show_page("Home")).pack(fill="x", padx=22, pady=(0, 22))


class AboutPage(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color=BG)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="About", text_color=TEXT, font=ctk.CTkFont(size=30, weight="bold")).grid(row=0, column=0, sticky="w")
        card = GlassCard(self)
        card.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        ctk.CTkLabel(card, text="🔐 Secure Encryptor", text_color=NEON_BLUE, font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w", padx=24, pady=(24, 4))
        ctk.CTkLabel(card, text="Designed by Shreya | v1.0.0", text_color=CYAN, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=24, pady=(0, 10))
        ctk.CTkLabel(
            card,
            text=(
                "A modern desktop file encryption console built with Python, CustomTkinter, "
                "AES-256-GCM direct key files, and SQLite. It supports any binary file type "
                "and restores original filenames during decryption."
            ),
            text_color=TEXT,
            wraplength=780,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 20))
        ctk.CTkFrame(card, height=3, fg_color=PURPLE, corner_radius=99).pack(fill="x", padx=24, pady=(0, 24))
        ctk.CTkLabel(card, text="Secure Encryptor © 2026", text_color=MUTED).pack(anchor="w", padx=24, pady=(0, 24))
