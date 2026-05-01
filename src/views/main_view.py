"""Main JukeBox window view: sidebar, content host, and player bar."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from . import font_manager as fonts


NAV_ITEMS = [
    ("now_playing", "♪", "Now Playing"),
    ("library", "≡", "Library"),
    ("manage", "✎", "Manage"),
    ("playlists", "♫", "Playlists"),
    ("statistics", "▤", "Statistics"),
]


class MainView:
    """Builds the main window chrome (sidebar, page host, player bar).

    Action callbacks are exposed as attributes the controller assigns:
    on_nav_click(key), on_view_tracks, on_logout, on_close,
    on_play_pause, on_previous, on_next,
    on_volume_change(value), on_volume_up, on_volume_down,
    on_progress_press, on_progress_release.
    """

    def __init__(self, current_user: str = "Guest"):
        self.window = tk.Tk()
        self.current_user = current_user or "Guest"
        self.window.title("JukeBox Music")

        self._nav_buttons: dict[str, ttk.Button] = {}
        self.player_cover_image = None

        self.on_nav_click = None
        self.on_view_tracks = None
        self.on_logout = None
        self.on_close = None
        self.on_play_pause = None
        self.on_previous = None
        self.on_next = None
        self.on_volume_change = None
        self.on_volume_up = None
        self.on_volume_down = None
        self.on_progress_press = None
        self.on_progress_release = None

        self._configure_window_size()
        fonts.configure()
        fonts.apply_theme(self.window)

        self.window.columnconfigure(0, minsize=self.sidebar_width)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=0)

        self._build_sidebar()
        self._build_content_area()
        self._build_player_bar()

        self.window.protocol("WM_DELETE_WINDOW", self._fire_close)

    def _configure_window_size(self):
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()

        self.compact_screen = sw <= 1366 or sh <= 768
        self.sidebar_width = 210 if not self.compact_screen else 180

        start_w = min(max(int(sw * 0.9), 1100), sw)
        start_h = min(max(int(sh * 0.88), 680), sh)

        min_w = min(1080, max(960, sw - 60))
        min_h = min(680, max(620, sh - 80))
        self.window.minsize(min_w, min_h)

        if sw >= 1500 and sh >= 880:
            try:
                self.window.state("zoomed")
                return
            except tk.TclError:
                pass

        pos_x = max(0, (sw - start_w) // 2)
        pos_y = max(0, (sh - start_h) // 2)
        self.window.geometry(f"{start_w}x{start_h}+{pos_x}+{pos_y}")

    def _build_sidebar(self):
        sidebar = ttk.Frame(self.window, style="Sidebar.TFrame", padding=(18, 20))
        sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")
        sidebar.columnconfigure(0, weight=1)

        brand = ttk.Frame(sidebar, style="Sidebar.TFrame")
        brand.grid(row=0, column=0, sticky="ew", pady=(0, 22))
        brand.columnconfigure(1, weight=1)

        ttk.Label(brand, text="♪", style="Logo.TLabel").grid(row=0, column=0, padx=(0, 10))

        brand_text = ttk.Frame(brand, style="Sidebar.TFrame")
        brand_text.grid(row=0, column=1, sticky="w")
        ttk.Label(brand_text, text="JukeBox", style="Sidebar.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(brand_text, text="music library", style="SidebarMuted.TLabel").grid(
            row=1, column=0, sticky="w"
        )

        user_card = ttk.Frame(sidebar, style="Card.TFrame", padding=(14, 12))
        user_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        user_card.columnconfigure(1, weight=1)

        initial = (self.current_user[:1] or "?").upper()
        ttk.Label(user_card, text=initial, style="Metric.TLabel").grid(
            row=0, column=0, rowspan=2, padx=(0, 10)
        )
        ttk.Label(user_card, text="Signed in", style="CardSubtitle.TLabel").grid(
            row=0, column=1, sticky="w"
        )
        ttk.Label(
            user_card,
            text=self.current_user,
            style="CardTitle.TLabel",
            wraplength=130,
            justify="left",
        ).grid(row=1, column=1, sticky="w")

        ttk.Label(sidebar, text="MENU", style="SidebarMuted.TLabel").grid(
            row=2, column=0, sticky="w", pady=(0, 8)
        )

        nav_container = ttk.Frame(sidebar, style="Sidebar.TFrame")
        nav_container.grid(row=3, column=0, sticky="ew")
        nav_container.columnconfigure(0, weight=1)

        for row_index, (key, icon, label) in enumerate(NAV_ITEMS):
            button = ttk.Button(
                nav_container,
                text=f"  {icon}   {label}",
                style="Nav.TButton",
                command=lambda k=key: self._fire_nav(k),
            )
            button.grid(row=row_index, column=0, sticky="ew", pady=3)
            self._nav_buttons[key] = button

        spacer = ttk.Frame(sidebar, style="Sidebar.TFrame")
        spacer.grid(row=4, column=0, sticky="nsew")
        sidebar.rowconfigure(4, weight=1)

        ttk.Button(
            sidebar,
            text="View Tracks",
            style="Ghost.TButton",
            command=lambda: callable(self.on_view_tracks) and self.on_view_tracks(),
        ).grid(row=5, column=0, sticky="ew", pady=(14, 6))

        ttk.Button(
            sidebar,
            text="Log Out",
            style="Ghost.TButton",
            command=lambda: callable(self.on_logout) and self.on_logout(),
        ).grid(row=6, column=0, sticky="ew", pady=(6, 6))

        ttk.Button(
            sidebar,
            text="Close App",
            style="Danger.TButton",
            command=self.window.destroy,
        ).grid(row=7, column=0, sticky="ew")

    def _build_content_area(self):
        self.content = ttk.Frame(self.window, style="Root.TFrame", padding=(22, 18, 22, 10))
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.page_host = ttk.Frame(self.content, style="Root.TFrame")
        self.page_host.grid(row=0, column=0, sticky="nsew")
        self.page_host.columnconfigure(0, weight=1)
        self.page_host.rowconfigure(0, weight=1)

    def _build_player_bar(self):
        bar = ttk.Frame(self.window, style="Panel.TFrame", padding=(18, 12))
        bar.grid(row=1, column=1, sticky="ew")
        bar.columnconfigure(1, weight=1)

        left = ttk.Frame(bar, style="Panel.TFrame")
        left.grid(row=0, column=0, sticky="w")
        left.columnconfigure(1, weight=1)

        self.player_cover_canvas = tk.Canvas(left, width=56, height=56)
        fonts.style_canvas(self.player_cover_canvas, bg=fonts.CARD_ALT)
        self.player_cover_canvas.grid(row=0, column=0, rowspan=2, padx=(0, 14))

        self.player_title_lbl = ttk.Label(
            left,
            text="No track loaded",
            style="Panel.TLabel",
            font=fonts._ff(12, "bold"),
            wraplength=220,
            justify="left",
        )
        self.player_title_lbl.grid(row=0, column=1, sticky="w")

        self.player_artist_lbl = ttk.Label(
            left,
            text="Pick a song from your library",
            background=fonts.PANEL,
            foreground=fonts.MUTED,
            font=fonts._ff(10),
            wraplength=220,
            justify="left",
        )
        self.player_artist_lbl.grid(row=1, column=1, sticky="w")

        center = ttk.Frame(bar, style="Panel.TFrame")
        center.grid(row=0, column=1, sticky="nsew", padx=16)
        center.columnconfigure(0, weight=1)

        controls = ttk.Frame(center, style="Panel.TFrame")
        controls.grid(row=0, column=0)

        ttk.Button(
            controls, text="⏮", style="IconButton.TButton",
            command=lambda: callable(self.on_previous) and self.on_previous(),
        ).grid(row=0, column=0, padx=3)

        self.play_btn = ttk.Button(
            controls, text="▶", style="PlayFab.TButton",
            command=lambda: callable(self.on_play_pause) and self.on_play_pause(),
        )
        self.play_btn.grid(row=0, column=1, padx=8)

        ttk.Button(
            controls, text="⏭", style="IconButton.TButton",
            command=lambda: callable(self.on_next) and self.on_next(),
        ).grid(row=0, column=2, padx=3)

        progress = ttk.Frame(center, style="Panel.TFrame")
        progress.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        progress.columnconfigure(1, weight=1)

        self.time_cur_lbl = ttk.Label(
            progress, text="0:00", background=fonts.PANEL, foreground=fonts.MUTED, font=fonts._ff(9)
        )
        self.time_cur_lbl.grid(row=0, column=0, sticky="w")

        self.progress = tk.Scale(
            progress,
            from_=0,
            to=100,
            orient="horizontal",
            showvalue=False,
            bd=0,
            highlightthickness=0,
            troughcolor=fonts.CARD_ALT,
            bg=fonts.PANEL,
            fg=fonts.TEXT,
            activebackground=fonts.ACCENT,
            sliderlength=14,
        )
        self.progress.grid(row=0, column=1, sticky="ew", padx=8)
        self.progress.bind("<ButtonPress-1>", self._fire_progress_press)
        self.progress.bind("<ButtonRelease-1>", self._fire_progress_release)

        self.time_total_lbl = ttk.Label(
            progress,
            text="0:00",
            background=fonts.PANEL,
            foreground=fonts.MUTED,
            font=fonts._ff(9),
        )
        self.time_total_lbl.grid(row=0, column=2, sticky="e")

        right = ttk.Frame(bar, style="Panel.TFrame")
        right.grid(row=0, column=2, sticky="e")

        self.volume_icon_lbl = ttk.Label(
            right,
            text="🔊",
            background=fonts.PANEL,
            foreground=fonts.ACCENT_GLOW,
            font=fonts._ff(13),
        )
        self.volume_icon_lbl.grid(row=0, column=0, padx=(0, 6))

        ttk.Button(
            right,
            text="−",
            style="IconButton.TButton",
            command=lambda: callable(self.on_volume_down) and self.on_volume_down(),
            width=2,
        ).grid(row=0, column=1, padx=(0, 4))

        self.volume = tk.Scale(
            right,
            from_=0,
            to=100,
            orient="horizontal",
            showvalue=False,
            bd=0,
            highlightthickness=0,
            troughcolor=fonts.CARD_ALT,
            bg=fonts.PANEL,
            fg=fonts.TEXT,
            activebackground=fonts.ACCENT,
            sliderlength=14,
            length=120,
        )
        self.volume.grid(row=0, column=2)
        self.volume.set(70)
        self.volume.configure(command=self._fire_volume_change)
        self.volume.bind("<MouseWheel>", self._on_volume_wheel)
        self.volume.bind("<Button-4>", lambda e: callable(self.on_volume_up) and self.on_volume_up())
        self.volume.bind("<Button-5>", lambda e: callable(self.on_volume_down) and self.on_volume_down())

        ttk.Button(
            right,
            text="+",
            style="IconButton.TButton",
            command=lambda: callable(self.on_volume_up) and self.on_volume_up(),
            width=2,
        ).grid(row=0, column=3, padx=(4, 6))

        self.volume_pct_lbl = ttk.Label(
            right,
            text="70%",
            background=fonts.PANEL,
            foreground=fonts.MUTED,
            font=fonts._ff(9, "bold"),
            width=4,
            anchor="e",
        )
        self.volume_pct_lbl.grid(row=0, column=4)

    def _fire_nav(self, key: str):
        if callable(self.on_nav_click):
            self.on_nav_click(key)

    def _fire_progress_press(self, event=None):
        if callable(self.on_progress_press):
            self.on_progress_press(event)

    def _fire_progress_release(self, event=None):
        if callable(self.on_progress_release):
            self.on_progress_release(event)

    def _fire_volume_change(self, value):
        if callable(self.on_volume_change):
            self.on_volume_change(value)

    def _fire_close(self):
        if callable(self.on_close):
            self.on_close()
        else:
            self.window.destroy()

    def _on_volume_wheel(self, event):
        if event.delta > 0 and callable(self.on_volume_up):
            self.on_volume_up()
        elif event.delta < 0 and callable(self.on_volume_down):
            self.on_volume_down()

    def highlight_nav(self, active_key: str):
        for key, button in self._nav_buttons.items():
            button.configure(style="NavActive.TButton" if key == active_key else "Nav.TButton")

    def update_volume_visuals(self, pct: float):
        pct_int = max(0, min(100, int(round(pct))))
        self.volume_pct_lbl.configure(text=f"{pct_int}%")
        if pct_int == 0:
            icon = "🔇"
            colour = fonts.MUTED
        elif pct_int < 34:
            icon = "🔈"
            colour = fonts.ACCENT_GLOW
        elif pct_int < 67:
            icon = "🔉"
            colour = fonts.ACCENT_GLOW
        else:
            icon = "🔊"
            colour = fonts.ACCENT_GLOW
        self.volume_icon_lbl.configure(text=icon, foreground=colour)

    def set_status_title(self, text: str):
        self.window.title(f"JukeBox Music — {text}")

    def run(self):
        self.window.mainloop()
