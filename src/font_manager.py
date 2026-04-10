"""Shared font and ttk theme configuration for the JukeBox GUIs."""

from __future__ import annotations

import tkinter.font as tkfont
from tkinter import ttk


BG_MAIN = "#F5F7FB"
BG_PANEL = "#FFFFFF"
BG_SECTION = "#EEF2FF"
TEXT_MAIN = "#1F2937"
TEXT_MUTED = "#475569"
PRIMARY = "#4F46E5"
PRIMARY_ACTIVE = "#4338CA"
PRIMARY_PRESSED = "#3730A3"
DANGER = "#DC2626"
DANGER_ACTIVE = "#B91C1C"
ENTRY_BG = "#FFFFFF"
BORDER = "#D6DAE5"


def configure() -> None:
    family = "Segoe UI"

    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=11, family=family)

    text_font = tkfont.nametofont("TkTextFont")
    text_font.configure(size=11, family=family)

    fixed_font = tkfont.nametofont("TkFixedFont")
    fixed_font.configure(size=10, family="Consolas")

    heading_font = tkfont.nametofont("TkHeadingFont")
    heading_font.configure(size=11, family=family, weight="bold")


def apply_theme(root) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=BG_MAIN)

    style.configure(
        ".",
        background=BG_MAIN,
        foreground=TEXT_MAIN,
    )

    style.configure(
        "TLabel",
        background=BG_MAIN,
        foreground=TEXT_MAIN,
    )

    style.configure(
        "Title.TLabel",
        font=("Segoe UI", 17, "bold"),
        background=BG_MAIN,
        foreground="#0F172A",
    )

    style.configure(
        "Status.TLabel",
        font=("Segoe UI", 10),
        background=BG_MAIN,
        foreground=TEXT_MUTED,
    )

    style.configure(
        "Section.TLabelframe",
        background=BG_MAIN,
        borderwidth=1,
        relief="solid",
    )

    style.configure(
        "Section.TLabelframe.Label",
        font=("Segoe UI", 11, "bold"),
        background=BG_MAIN,
        foreground="#0F172A",
    )

    style.configure(
        "TFrame",
        background=BG_MAIN,
    )

    style.configure(
        "TEntry",
        padding=(6, 4),
        fieldbackground=ENTRY_BG,
        foreground=TEXT_MAIN,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        insertcolor=TEXT_MAIN,
    )

    style.map(
        "TEntry",
        bordercolor=[("focus", PRIMARY)],
        lightcolor=[("focus", PRIMARY)],
        darkcolor=[("focus", PRIMARY)],
    )

    style.configure(
        "TButton",
        padding=(12, 7),
        font=("Segoe UI", 10, "bold"),
        background=PRIMARY,
        foreground="white",
        borderwidth=0,
        focusthickness=0,
        relief="flat",
    )

    style.map(
        "TButton",
        background=[
            ("pressed", PRIMARY_PRESSED),
            ("active", PRIMARY_ACTIVE),
            ("disabled", "#A5B4FC"),
        ],
        foreground=[
            ("disabled", "#F8FAFC"),
        ],
    )

    style.configure(
        "Danger.TButton",
        padding=(12, 7),
        font=("Segoe UI", 10, "bold"),
        background=DANGER,
        foreground="white",
        borderwidth=0,
        focusthickness=0,
        relief="flat",
    )

    style.map(
        "Danger.TButton",
        background=[
            ("pressed", "#991B1B"),
            ("active", DANGER_ACTIVE),
            ("disabled", "#FCA5A5"),
        ],
        foreground=[
            ("disabled", "#FFF1F2"),
        ],
    )

    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
    )