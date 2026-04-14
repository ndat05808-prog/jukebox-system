import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

BG = "#F5F7FB"
SURFACE = "#FFFFFF"
TEXT = "#111827"
MUTED = "#475569"
BORDER = "#D6DAE5"
ACCENT = "#4F46E5"
ACCENT_DARK = "#4338CA"
DANGER = "#DC2626"


def configure():
    """Cấu hình font mặc định cho ứng dụng."""
    try:
        tkfont.nametofont("TkDefaultFont").configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkTextFont").configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkMenuFont").configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkHeadingFont").configure(family="Segoe UI", size=10, weight="bold")
        tkfont.nametofont("TkCaptionFont").configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkSmallCaptionFont").configure(family="Segoe UI", size=9)
        tkfont.nametofont("TkIconFont").configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkTooltipFont").configure(family="Segoe UI", size=9)
        tkfont.nametofont("TkFixedFont").configure(family="Consolas", size=10)
    except tk.TclError:
        pass


def apply_theme(window):
    """Áp dụng màu và style ttk cho một cửa sổ."""
    window.configure(bg=BG)

    style = ttk.Style(window)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))

    style.configure("TFrame", background=BG)

    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 16, "bold"))
    style.configure("Status.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))

    style.configure("TLabelframe", background=BG, bordercolor=BORDER, relief="solid")
    style.configure("TLabelframe.Label", background=BG, foreground=TEXT, font=("Segoe UI", 10, "bold"))

    style.configure("Section.TLabelframe", background=BG, bordercolor=BORDER, relief="solid")
    style.configure("Section.TLabelframe.Label", background=BG, foreground=TEXT, font=("Segoe UI", 10, "bold"))

    style.configure("TButton", padding=(10, 6), font=("Segoe UI", 10))
    style.configure("Danger.TButton", padding=(10, 6), font=("Segoe UI", 10), foreground=DANGER)

    style.configure("TEntry", padding=4)
    style.configure("TCombobox", padding=4)

    style.configure(
        "Treeview",
        background=SURFACE,
        fieldbackground=SURFACE,
        foreground=TEXT,
        rowheight=26,
        bordercolor=BORDER,
        relief="solid",
    )
    style.configure(
        "Treeview.Heading",
        background=BG,
        foreground=TEXT,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
    )

    style.map(
        "TButton",
        background=[("active", ACCENT_DARK)],
    )