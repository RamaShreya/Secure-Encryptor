from __future__ import annotations

import logging
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

try:
    from tkinterdnd2 import TkinterDnD
except Exception:
    TkinterDnD = None

from crypto.security_utils import cleanup_temp_files, ensure_directories
from database.database import EncryptionDatabase
from gui.animations import BG, CYAN, MUTED, NEON_BLUE, PURPLE, TEXT, Toast
from gui.components import GlassCard, NeonButton, StatCard
from gui.decrypt_page import DecryptPage
from gui.encrypt_page import EncryptPage
from gui.settings_page import AboutPage, HistoryPage


class SecureEncryptorApp(ctk.CTk, TkinterDnD.DnDWrapper if TkinterDnD else object):
    def __init__(self, base_dir: Path) -> None:
        super().__init__()
        if TkinterDnD:
            try:
                self.TkdndVersion = TkinterDnD._require(self)
            except Exception:
                logging.exception("Drag-and-drop support is unavailable; continuing without tkdnd.")

        self.base_dir = base_dir
        ensure_directories(base_dir)
        self.database = EncryptionDatabase(base_dir / "database" / "logs.db")
        self.database.record_activity("Application opened", "info", "Secure Encryptor dashboard started")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Secure Encryptor")
        self.geometry("1180x740")
        self.minsize(980, 640)
        self.configure(fg_color=BG)

        self.pages: dict[str, ctk.CTkFrame] = {}
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        self.notification_queue: list[tuple[str, str]] = []
        self.active_notification = False
        self._build_layout()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.show_page("Home")

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=246, fg_color="#0B1020", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="🔐 Secure Encryptor", text_color=TEXT, font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=(28, 4))
        ctk.CTkLabel(sidebar, text="Designed by Shreya", text_color=CYAN, font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=22, pady=(0, 24))

        labels = {
            "Home": "⌂  Home",
            "Encrypt File": "🔒  Encrypt File",
            "Decrypt File": "🔓  Decrypt File",
            "History": "▤  History",
            "About": "ⓘ  About",
        }
        for item in ("Home", "Encrypt File", "Decrypt File", "History", "About"):
            button = ctk.CTkButton(
                sidebar,
                text=labels[item],
                anchor="w",
                height=44,
                corner_radius=12,
                fg_color="transparent",
                hover_color="#17213A",
                text_color=TEXT,
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda name=item: self.show_page(name),
            )
            button.pack(fill="x", padx=18, pady=5)
            self.nav_buttons[item] = button

        ctk.CTkFrame(sidebar, fg_color="transparent").pack(expand=True)
        NeonButton(sidebar, text="Refresh Stats", command=self.refresh_current_page, fg_color="#111827").pack(fill="x", padx=18, pady=(10, 24))
        ctk.CTkLabel(sidebar, text="Secure Encryptor © 2026", text_color=MUTED, font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20, pady=(0, 18))

        self.content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.page_host = ctk.CTkFrame(self.content, fg_color=BG, corner_radius=0)
        self.page_host.grid(row=0, column=0, sticky="nsew")
        self.page_host.grid_columnconfigure(0, weight=1)
        self.page_host.grid_rowconfigure(0, weight=1)

        self.pages["Home"] = HomePage(self.page_host, self)
        self.pages["Encrypt File"] = EncryptPage(self.page_host, self)
        self.pages["Decrypt File"] = DecryptPage(self.page_host, self)
        self.pages["History"] = HistoryPage(self.page_host, self)
        self.pages["About"] = AboutPage(self.page_host, self)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew", padx=22, pady=22)

    def show_page(self, name: str) -> None:
        for item, button in self.nav_buttons.items():
            button.configure(fg_color=PURPLE if item == name else "transparent")
        page = self.pages[name]
        if hasattr(page, "refresh"):
            page.refresh()
        page.tkraise()

    def refresh_current_page(self) -> None:
        for page in self.pages.values():
            if hasattr(page, "refresh"):
                page.refresh()
        self.notify("Dashboard data refreshed.", "info")

    def notify(self, message: str, kind: str = "success") -> None:
        if kind == "error":
            messagebox.showerror("Secure Encryptor", message)
        self.notification_queue.append((message, kind))
        self._show_next_notification()

    def _on_close(self) -> None:
        cleanup_temp_files(self.base_dir)
        self.database.record_activity("Application closed", "info", "Secure Encryptor closed")
        self.destroy()

    def _show_next_notification(self) -> None:
        if self.active_notification or not self.notification_queue:
            return
        message, kind = self.notification_queue.pop(0)
        self.active_notification = True
        Toast(self, message, kind, on_close=self._notification_closed)

    def _notification_closed(self) -> None:
        self.active_notification = False
        self._show_next_notification()


class HomePage(ctk.CTkFrame):
    def __init__(self, master, app: SecureEncryptorApp) -> None:
        super().__init__(master, fg_color=BG)
        self.app = app
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self, text="Security Dashboard", text_color=TEXT, font=ctk.CTkFont(size=30, weight="bold")).grid(row=0, column=0, columnspan=3, sticky="w")
        ctk.CTkLabel(self, text="Real-time encryption activity, file protection stats, and secure workspace health.", text_color=MUTED).grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 20))

        self.stat_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stat_frame.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.stat_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.activity = GlassCard(self)
        self.activity.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(20, 0))
        ctk.CTkLabel(self.activity, text="Recent Activities", text_color=TEXT, font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(18, 6))
        self.activity_box = ctk.CTkTextbox(self.activity, fg_color="#0B1020", text_color=TEXT, corner_radius=14)
        self.activity_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def refresh(self) -> None:
        for child in self.stat_frame.winfo_children():
            child.destroy()
        stats = self.app.database.stats()
        StatCard(self.stat_frame, "Encrypted Files", str(stats["encrypted"]), NEON_BLUE).grid(row=0, column=0, sticky="ew", padx=(0, 10))
        StatCard(self.stat_frame, "Decrypted Files", str(stats["decrypted"]), CYAN).grid(row=0, column=1, sticky="ew", padx=10)
        StatCard(self.stat_frame, "Activity Events", str(stats["activities"]), PURPLE).grid(row=0, column=2, sticky="ew", padx=(10, 0))

        self.activity_box.configure(state="normal")
        self.activity_box.delete("1.0", "end")
        for row in self.app.database.recent_activity(10):
            timestamp = self.app.database.format_timestamp(row["timestamp"])
            self.activity_box.insert("end", f"{timestamp}  {row['activity']}  {row['detail']}\n")
        self.activity_box.configure(state="disabled")
