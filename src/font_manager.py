import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

BG = "#07111f"
PANEL = "#0b1728"
CARD = "#0f1e33"
CARD_ALT = "#132641"
TEXT = "#e6edf7"
MUTED = "#91a4c3"
BORDER = "#274567"
ACCENT = "#4de2ff"
ACCENT_SOFT = "#1b7ca0"
ACCENT_DARK = "#0f5c80"
SUCCESS = "#2dd4bf"
DANGER = "#fb7185"
WARNING = "#fbbf24"
INPUT_BG = "#091423"
SELECT_BG = "#173355"
TREE_ROW = "#0d1a2d"


def configure():
    try:
        tkfont.nametofont("TkDefaultFont").configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkTextFont").configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkMenuFont").configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkHeadingFont").configure(family="Segoe UI", size=11, weight="bold")
        tkfont.nametofont("TkCaptionFont").configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkSmallCaptionFont").configure(family="Segoe UI", size=9)
        tkfont.nametofont("TkIconFont").configure(family="Segoe UI", size=10)
        tkfont.nametofont("TkTooltipFont").configure(family="Segoe UI", size=9)
        tkfont.nametofont("TkFixedFont").configure(family="Consolas", size=10)
    except tk.TclError:
        pass


def apply_theme(window: tk.Misc):
    window.configure(bg=BG)
    style = ttk.Style(window)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("TFrame", background=BG)
    style.configure("Root.TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)
    style.configure("Card.TFrame", background=CARD, relief="flat")
    style.configure("AltCard.TFrame", background=CARD_ALT, relief="flat")
    style.configure("Sidebar.TFrame", background=PANEL)

    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Panel.TLabel", background=PANEL, foreground=TEXT)
    style.configure("Card.TLabel", background=CARD, foreground=TEXT)
    style.configure("AltCard.TLabel", background=CARD_ALT, foreground=TEXT)
    style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 18, "bold"))
    style.configure("Hero.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 22, "bold"))
    style.configure("SectionTitle.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 13, "bold"))
    style.configure("CardTitle.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 12, "bold"))
    style.configure("Metric.TLabel", background=CARD, foreground=ACCENT, font=("Segoe UI", 22, "bold"))
    style.configure("Muted.TLabel", background=BG, foreground=MUTED)
    style.configure("SmallMuted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
    style.configure("CardMuted.TLabel", background=CARD, foreground=MUTED)
    style.configure("Status.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 10))
    style.configure("Sidebar.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 12, "bold"))
    style.configure("Logo.TLabel", background=PANEL, foreground=ACCENT, font=("Segoe UI", 18, "bold"))

    style.configure("TLabelframe", background=BG, foreground=TEXT, bordercolor=BORDER, relief="solid", borderwidth=1)
    style.configure("TLabelframe.Label", background=BG, foreground=TEXT, font=("Segoe UI", 11, "bold"))
    style.configure("Section.TLabelframe", background=BG, bordercolor=BORDER, relief="solid", borderwidth=1)
    style.configure("Section.TLabelframe.Label", background=BG, foreground=TEXT, font=("Segoe UI", 11, "bold"))

    style.configure(
        "TButton",
        background=CARD_ALT,
        foreground=TEXT,
        bordercolor=BORDER,
        relief="flat",
        padding=(12, 8),
        font=("Segoe UI", 10, "bold"),
    )
    style.map("TButton", background=[("active", SELECT_BG), ("pressed", ACCENT_DARK)], foreground=[("disabled", MUTED)])

    style.configure("Sidebar.TButton", background=PANEL, foreground=TEXT, bordercolor=PANEL, padding=(14, 10), anchor="w", font=("Segoe UI", 11))
    style.map("Sidebar.TButton", background=[("active", CARD_ALT), ("pressed", SELECT_BG)])

    style.configure("Neon.TButton", background=ACCENT_SOFT, foreground=TEXT, bordercolor=ACCENT, padding=(12, 8), font=("Segoe UI", 10, "bold"))
    style.map("Neon.TButton", background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)])

    style.configure("Danger.TButton", background="#42121e", foreground=DANGER, bordercolor="#7c253b", padding=(12, 8), font=("Segoe UI", 10, "bold"))
    style.map("Danger.TButton", background=[("active", "#5b1627"), ("pressed", "#781b32")])

    style.configure("Ghost.TButton", background=CARD, foreground=MUTED, bordercolor=BORDER, padding=(10, 7))
    style.map("Ghost.TButton", background=[("active", CARD_ALT), ("pressed", SELECT_BG)])

    style.configure("TEntry", fieldbackground=INPUT_BG, foreground=TEXT, insertcolor=TEXT, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, padding=6)
    style.map("TEntry", bordercolor=[("focus", ACCENT)])

    style.configure("TCombobox", fieldbackground=INPUT_BG, background=INPUT_BG, foreground=TEXT, arrowcolor=TEXT, bordercolor=BORDER, padding=6)

    style.configure("Treeview", background=TREE_ROW, fieldbackground=TREE_ROW, foreground=TEXT, bordercolor=BORDER, relief="flat", rowheight=30, font=("Segoe UI", 10))
    style.map("Treeview", background=[("selected", SELECT_BG)], foreground=[("selected", TEXT)])
    style.configure("Treeview.Heading", background=CARD_ALT, foreground=TEXT, bordercolor=BORDER, relief="flat", font=("Segoe UI", 10, "bold"))
    style.map("Treeview.Heading", background=[("active", SELECT_BG)])

    try:
        window.option_add("*TCombobox*Listbox.background", INPUT_BG)
        window.option_add("*TCombobox*Listbox.foreground", TEXT)
        window.option_add("*TCombobox*Listbox.selectBackground", SELECT_BG)
        window.option_add("*TCombobox*Listbox.selectForeground", TEXT)
    except tk.TclError:
        pass


def style_text_widget(widget: tk.Text):
    widget.configure(
        bg=INPUT_BG,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        borderwidth=1,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        padx=10,
        pady=10,
    )


def style_canvas(widget: tk.Canvas, bg: str | None = None):
    widget.configure(bg=bg or CARD, bd=0, highlightthickness=1, highlightbackground=BORDER)