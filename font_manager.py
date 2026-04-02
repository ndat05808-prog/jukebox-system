"""Shared font and ttk theme configuration for the JukeBox GUIs."""

from __future__ import annotations

import tkinter.font as tkfont
from tkinter import ttk


def configure() -> None:
    family = "Helvetica"
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=11, family=family)

    text_font = tkfont.nametofont("TkTextFont")
    text_font.configure(size=11, family=family)

    fixed_font = tkfont.nametofont("TkFixedFont")
    fixed_font.configure(size=10, family=family)

    heading_font = tkfont.nametofont("TkHeadingFont")
    heading_font.configure(size=11, family=family, weight="bold")


def apply_theme(root) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure("Title.TLabel", font=("Helvetica", 14, "bold"))
    style.configure("Section.TLabelframe.Label", font=("Helvetica", 11, "bold"))
    style.configure("Status.TLabel", font=("Helvetica", 10))
    style.configure("TButton", padding=(8, 5))
    style.configure("TEntry", padding=(4, 3))
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))