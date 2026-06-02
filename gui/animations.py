from __future__ import annotations

import customtkinter as ctk


NEON_BLUE = "#00D9FF"
CYAN = "#55F6FF"
PURPLE = "#8B5CF6"
PINK = "#EC4899"
CARD = "#151B2E"
CARD_HOVER = "#1D2540"
BG = "#070B16"
TEXT = "#EAF6FF"
MUTED = "#8FA3BF"
SUCCESS = "#20E3B2"
ERROR = "#FF4D6D"
WARNING = "#FACC15"


def pulse_widget(widget: ctk.CTkBaseClass, colors: tuple[str, str], step: int = 0) -> None:
    color = colors[step % len(colors)]
    try:
        widget.configure(border_color=color)
        widget.after(650, lambda: pulse_widget(widget, colors, step + 1))
    except Exception:
        return


def animate_progress(progress: ctk.CTkProgressBar, target: float, current: float = 0.0) -> None:
    if abs(target - current) < 0.01:
        progress.set(target)
        return
    next_value = current + ((target - current) * 0.22)
    progress.set(next_value)
    progress.after(16, lambda: animate_progress(progress, target, next_value))


class Toast(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, message: str, kind: str = "success", on_close=None) -> None:
        self.on_close = on_close
        colors = {"success": SUCCESS, "error": ERROR, "warning": WARNING, "info": NEON_BLUE}
        super().__init__(
            master,
            fg_color="#101827",
            border_width=1,
            border_color=colors.get(kind, NEON_BLUE),
            corner_radius=16,
        )
        self.place(relx=0.98, rely=0.05, anchor="ne")
        ctk.CTkLabel(
            self,
            text=message,
            text_color=TEXT,
            font=ctk.CTkFont(size=13, weight="bold"),
            wraplength=360,
        ).pack(padx=18, pady=14)
        self.after(3200, self.close)

    def close(self) -> None:
        self.destroy()
        if self.on_close:
            self.on_close()
