import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

BG = "#0a0d1f"
PANEL = "#121638"
SIDEBAR = "#0d1029"
CARD = "#1a1f42"
CARD_ALT = "#252a55"
CARD_HOVER = "#2d3366"
TEXT = "#f0f2ff"
TEXT_SOFT = "#cdd2f0"
MUTED = "#8088b8"
BORDER = "#2d3366"
BORDER_SOFT = "#1f2547"

ACCENT = "#a78bfa"
ACCENT_SOFT = "#7c3aed"
ACCENT_DARK = "#5b21b6"
ACCENT_GLOW = "#c4b5fd"

HIGHLIGHT = "#22d3ee"
HIGHLIGHT_SOFT = "#0891b2"

SUCCESS = "#34d399"
SUCCESS_SOFT = "#047857"
DANGER = "#f87171"
DANGER_SOFT = "#991b1b"
WARNING = "#fbbf24"

INPUT_BG = "#161a3a"
INPUT_FOCUS = "#1f2547"
SELECT_BG = "#3730a3"
TREE_ROW = "#141833"
TREE_ROW_ALT = "#191e42"


def _pick_font_family() -> str:
    for family in ("SF Pro Display", "Inter", "Segoe UI", "Helvetica Neue", "Arial"):
        try:
            tkfont.Font(family=family, size=10)
            return family
        except tk.TclError:
            continue
    return "TkDefaultFont"


FONT_FAMILY = None


def configure():
    global FONT_FAMILY
    FONT_FAMILY = _pick_font_family()
    try:
        tkfont.nametofont("TkDefaultFont").configure(family=FONT_FAMILY, size=10)
        tkfont.nametofont("TkTextFont").configure(family=FONT_FAMILY, size=10)
        tkfont.nametofont("TkMenuFont").configure(family=FONT_FAMILY, size=10)
        tkfont.nametofont("TkHeadingFont").configure(family=FONT_FAMILY, size=11, weight="bold")
        tkfont.nametofont("TkCaptionFont").configure(family=FONT_FAMILY, size=10)
        tkfont.nametofont("TkSmallCaptionFont").configure(family=FONT_FAMILY, size=9)
        tkfont.nametofont("TkIconFont").configure(family=FONT_FAMILY, size=10)
        tkfont.nametofont("TkTooltipFont").configure(family=FONT_FAMILY, size=9)
        tkfont.nametofont("TkFixedFont").configure(family="Menlo", size=10)
    except tk.TclError:
        pass


def ff(size: int, weight: str = "normal") -> tuple:
    family = FONT_FAMILY or "Segoe UI"
    return (family, size, weight)


_ff = ff


def apply_theme(window: tk.Misc):
    window.configure(bg=BG)
    style = ttk.Style(window)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    base_font = _ff(10)

    style.configure(".", background=BG, foreground=TEXT, font=base_font)

    style.configure("TFrame", background=BG)
    style.configure("Root.TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)
    style.configure("Sidebar.TFrame", background=SIDEBAR)
    style.configure("Card.TFrame", background=CARD, relief="flat")
    style.configure("AltCard.TFrame", background=CARD_ALT, relief="flat")
    style.configure("Soft.TFrame", background=INPUT_BG, relief="flat")
    style.configure("Accent.TFrame", background=ACCENT_SOFT, relief="flat")

    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Panel.TLabel", background=PANEL, foreground=TEXT)
    style.configure("Sidebar.TLabel", background=SIDEBAR, foreground=TEXT, font=_ff(13, "bold"))
    style.configure("SidebarMuted.TLabel", background=SIDEBAR, foreground=MUTED, font=_ff(9))
    style.configure("Card.TLabel", background=CARD, foreground=TEXT)
    style.configure("CardSoft.TLabel", background=CARD, foreground=TEXT_SOFT)
    style.configure("AltCard.TLabel", background=CARD_ALT, foreground=TEXT)
    style.configure("Soft.TLabel", background=INPUT_BG, foreground=TEXT)

    style.configure("Hero.TLabel", background=BG, foreground=TEXT, font=_ff(26, "bold"))
    style.configure("Title.TLabel", background=BG, foreground=TEXT, font=_ff(20, "bold"))
    style.configure("SectionTitle.TLabel", background=BG, foreground=TEXT, font=_ff(14, "bold"))
    style.configure("CardTitle.TLabel", background=CARD, foreground=TEXT, font=_ff(13, "bold"))
    style.configure("CardSubtitle.TLabel", background=CARD, foreground=MUTED, font=_ff(10))
    style.configure("Metric.TLabel", background=CARD, foreground=ACCENT_GLOW, font=_ff(26, "bold"))
    style.configure("MetricLabel.TLabel", background=CARD, foreground=MUTED, font=_ff(10))
    style.configure("Muted.TLabel", background=BG, foreground=MUTED)
    style.configure("SmallMuted.TLabel", background=BG, foreground=MUTED, font=_ff(9))
    style.configure("CardMuted.TLabel", background=CARD, foreground=MUTED)
    style.configure("Status.TLabel", background=BG, foreground=MUTED, font=_ff(10))
    style.configure("Logo.TLabel", background=SIDEBAR, foreground=ACCENT, font=_ff(22, "bold"))
    style.configure("Tag.TLabel", background=CARD_ALT, foreground=ACCENT_GLOW, font=_ff(9, "bold"), padding=(8, 4))
    style.configure("Accent.TLabel", background=BG, foreground=ACCENT, font=_ff(11, "bold"))
    style.configure("NowPlayingTitle.TLabel", background=BG, foreground=TEXT, font=_ff(28, "bold"))
    style.configure("NowPlayingArtist.TLabel", background=BG, foreground=ACCENT_GLOW, font=_ff(16))
    style.configure("NowPlayingAlbum.TLabel", background=BG, foreground=MUTED, font=_ff(11))

    style.configure(
        "TLabelframe",
        background=BG,
        foreground=TEXT,
        bordercolor=BORDER,
        relief="solid",
        borderwidth=1,
    )
    style.configure("TLabelframe.Label", background=BG, foreground=TEXT, font=_ff(11, "bold"))

    style.configure(
        "TButton",
        background=CARD_ALT,
        foreground=TEXT,
        bordercolor=CARD_ALT,
        lightcolor=CARD_ALT,
        darkcolor=CARD_ALT,
        focuscolor=CARD_ALT,
        relief="flat",
        padding=(14, 9),
        font=_ff(10, "bold"),
    )
    style.map(
        "TButton",
        background=[("active", CARD_HOVER), ("pressed", ACCENT_DARK)],
        foreground=[("disabled", MUTED)],
    )

    style.configure(
        "Nav.TButton",
        background=SIDEBAR,
        foreground=TEXT_SOFT,
        bordercolor=SIDEBAR,
        lightcolor=SIDEBAR,
        darkcolor=SIDEBAR,
        focuscolor=SIDEBAR,
        padding=(16, 12),
        anchor="w",
        font=_ff(11),
    )
    style.map(
        "Nav.TButton",
        background=[("active", CARD), ("pressed", CARD)],
        foreground=[("active", TEXT), ("pressed", TEXT)],
    )

    style.configure(
        "NavActive.TButton",
        background=ACCENT_SOFT,
        foreground=TEXT,
        bordercolor=ACCENT_SOFT,
        lightcolor=ACCENT_SOFT,
        darkcolor=ACCENT_SOFT,
        focuscolor=ACCENT_SOFT,
        padding=(16, 12),
        anchor="w",
        font=_ff(11, "bold"),
    )
    style.map(
        "NavActive.TButton",
        background=[("active", ACCENT_SOFT), ("pressed", ACCENT_SOFT)],
        foreground=[("active", TEXT), ("pressed", TEXT)],
    )

    style.configure(
        "Neon.TButton",
        background=ACCENT_SOFT,
        foreground=TEXT,
        bordercolor=ACCENT_SOFT,
        lightcolor=ACCENT_SOFT,
        darkcolor=ACCENT_SOFT,
        focuscolor=ACCENT_SOFT,
        padding=(14, 9),
        font=_ff(10, "bold"),
    )
    style.map(
        "Neon.TButton",
        background=[("active", ACCENT), ("pressed", ACCENT_DARK)],
    )

    style.configure(
        "Success.TButton",
        background=SUCCESS_SOFT,
        foreground=TEXT,
        bordercolor=SUCCESS_SOFT,
        lightcolor=SUCCESS_SOFT,
        darkcolor=SUCCESS_SOFT,
        focuscolor=SUCCESS_SOFT,
        padding=(14, 9),
        font=_ff(10, "bold"),
    )
    style.map("Success.TButton", background=[("active", SUCCESS), ("pressed", SUCCESS_SOFT)])

    style.configure(
        "Danger.TButton",
        background=DANGER_SOFT,
        foreground=TEXT,
        bordercolor=DANGER_SOFT,
        lightcolor=DANGER_SOFT,
        darkcolor=DANGER_SOFT,
        focuscolor=DANGER_SOFT,
        padding=(14, 9),
        font=_ff(10, "bold"),
    )
    style.map("Danger.TButton", background=[("active", DANGER), ("pressed", DANGER_SOFT)])

    style.configure(
        "Ghost.TButton",
        background=CARD,
        foreground=TEXT_SOFT,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        focuscolor=CARD,
        padding=(12, 8),
        font=_ff(10),
    )
    style.map(
        "Ghost.TButton",
        background=[("active", CARD_HOVER), ("pressed", CARD_ALT)],
        foreground=[("active", TEXT), ("pressed", TEXT)],
    )

    style.configure(
        "Chip.TButton",
        background=CARD_ALT,
        foreground=TEXT_SOFT,
        bordercolor=CARD_ALT,
        lightcolor=CARD_ALT,
        darkcolor=CARD_ALT,
        focuscolor=CARD_ALT,
        padding=(10, 6),
        font=_ff(9, "bold"),
    )
    style.map("Chip.TButton", background=[("active", ACCENT_SOFT)], foreground=[("active", TEXT)])

    style.configure(
        "IconButton.TButton",
        background=CARD,
        foreground=TEXT,
        bordercolor=CARD,
        lightcolor=CARD,
        darkcolor=CARD,
        focuscolor=CARD,
        padding=(10, 8),
        font=_ff(13),
    )
    style.map("IconButton.TButton", background=[("active", CARD_HOVER), ("pressed", ACCENT_SOFT)])

    style.configure(
        "PlayFab.TButton",
        background=ACCENT_SOFT,
        foreground=TEXT,
        bordercolor=ACCENT_SOFT,
        lightcolor=ACCENT_SOFT,
        darkcolor=ACCENT_SOFT,
        focuscolor=ACCENT_SOFT,
        padding=(18, 14),
        font=_ff(16, "bold"),
    )
    style.map("PlayFab.TButton", background=[("active", ACCENT), ("pressed", ACCENT_DARK)])

    style.configure(
        "Link.TButton",
        background=CARD,
        foreground=ACCENT_GLOW,
        bordercolor=CARD,
        lightcolor=CARD,
        darkcolor=CARD,
        focuscolor=CARD,
        padding=(4, 2),
        font=_ff(9, "bold"),
    )
    style.map("Link.TButton", background=[("active", CARD)], foreground=[("active", ACCENT)])

    style.configure(
        "TEntry",
        fieldbackground=INPUT_BG,
        foreground=TEXT,
        insertcolor=TEXT,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        padding=8,
    )
    style.map("TEntry", bordercolor=[("focus", ACCENT)], lightcolor=[("focus", ACCENT)])

    style.configure(
        "TCombobox",
        fieldbackground=INPUT_BG,
        background=INPUT_BG,
        foreground=TEXT,
        arrowcolor=ACCENT_GLOW,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        padding=6,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", INPUT_BG), ("disabled", INPUT_BG)],
        background=[("readonly", INPUT_BG), ("active", INPUT_BG)],
        foreground=[("readonly", TEXT), ("disabled", MUTED)],
        selectbackground=[("readonly", INPUT_BG)],
        selectforeground=[("readonly", TEXT)],
        bordercolor=[("focus", ACCENT), ("readonly", BORDER)],
        lightcolor=[("focus", ACCENT), ("readonly", BORDER)],
        darkcolor=[("focus", ACCENT), ("readonly", BORDER)],
    )

    style.configure(
        "Treeview",
        background=TREE_ROW,
        fieldbackground=TREE_ROW,
        foreground=TEXT,
        bordercolor=BORDER_SOFT,
        relief="flat",
        rowheight=34,
        font=_ff(10),
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT_SOFT)],
        foreground=[("selected", TEXT)],
    )
    style.configure(
        "Treeview.Heading",
        background=PANEL,
        foreground=ACCENT_GLOW,
        bordercolor=BORDER_SOFT,
        relief="flat",
        font=_ff(10, "bold"),
        padding=(8, 6),
    )
    style.map("Treeview.Heading", background=[("active", CARD_ALT)])

    style.configure(
        "TNotebook",
        background=BG,
        bordercolor=BORDER_SOFT,
        tabmargins=(0, 0, 0, 0),
    )
    style.configure(
        "TNotebook.Tab",
        background=CARD,
        foreground=MUTED,
        bordercolor=CARD,
        lightcolor=CARD,
        darkcolor=CARD,
        padding=(16, 10),
        font=_ff(10, "bold"),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", ACCENT_SOFT), ("active", CARD_HOVER)],
        foreground=[("selected", TEXT), ("active", TEXT)],
    )

    style.configure(
        "Horizontal.TProgressbar",
        background=ACCENT,
        troughcolor=CARD_ALT,
        bordercolor=CARD_ALT,
        lightcolor=ACCENT,
        darkcolor=ACCENT_SOFT,
    )

    style.configure("TScrollbar", background=CARD, troughcolor=BG, bordercolor=BG, arrowcolor=MUTED)
    style.map("TScrollbar", background=[("active", CARD_HOVER)])

    try:
        window.option_add("*TCombobox*Listbox.background", INPUT_BG)
        window.option_add("*TCombobox*Listbox.foreground", TEXT)
        window.option_add("*TCombobox*Listbox.selectBackground", ACCENT_SOFT)
        window.option_add("*TCombobox*Listbox.selectForeground", TEXT)
        window.option_add("*TCombobox*Listbox.font", _ff(10))
    except tk.TclError:
        pass


def style_text_widget(widget: tk.Text):
    widget.configure(
        bg=INPUT_BG,
        fg=TEXT,
        insertbackground=ACCENT,
        relief="flat",
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=BORDER_SOFT,
        highlightcolor=ACCENT,
        padx=14,
        pady=12,
        font=_ff(10),
        selectbackground=ACCENT_SOFT,
        selectforeground=TEXT,
    )


def style_canvas(widget: tk.Canvas, bg: str | None = None):
    widget.configure(
        bg=bg or CARD,
        bd=0,
        highlightthickness=1,
        highlightbackground=BORDER_SOFT,
    )
