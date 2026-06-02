from __future__ import annotations

import customtkinter as ctk

from gui.animations import CARD, CARD_HOVER, CYAN, MUTED, NEON_BLUE, PURPLE, TEXT


class GlassCard(ctk.CTkFrame):
    def __init__(self, master, **kwargs) -> None:
        normal_color = kwargs.pop("fg_color", CARD)
        super().__init__(
            master,
            fg_color=normal_color,
            border_color=kwargs.pop("border_color", "#26345C"),
            border_width=kwargs.pop("border_width", 1),
            corner_radius=kwargs.pop("corner_radius", 18),
            **kwargs,
        )
        self._normal_color = normal_color
        self.bind("<Enter>", lambda _event: self.configure(fg_color=CARD_HOVER))
        self.bind("<Leave>", lambda _event: self.configure(fg_color=self._normal_color))


class NeonButton(ctk.CTkButton):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            fg_color=kwargs.pop("fg_color", PURPLE),
            hover_color=kwargs.pop("hover_color", NEON_BLUE),
            text_color=kwargs.pop("text_color", "#FFFFFF"),
            corner_radius=kwargs.pop("corner_radius", 14),
            height=kwargs.pop("height", 44),
            border_width=kwargs.pop("border_width", 1),
            border_color=kwargs.pop("border_color", CYAN),
            font=kwargs.pop("font", ctk.CTkFont(size=14, weight="bold")),
            **kwargs,
        )


class StatCard(GlassCard):
    def __init__(self, master, title: str, value: str, accent: str = NEON_BLUE) -> None:
        super().__init__(master)
        ctk.CTkLabel(self, text=title, text_color=MUTED, font=ctk.CTkFont(size=13)).pack(anchor="w", padx=18, pady=(16, 2))
        ctk.CTkLabel(self, text=value, text_color=TEXT, font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=18)
        ctk.CTkFrame(self, height=3, fg_color=accent, corner_radius=99).pack(fill="x", padx=18, pady=(12, 16))
