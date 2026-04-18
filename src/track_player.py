import tkinter as tk
from tkinter import messagebox, ttk

from . import cover_manager
from . import font_manager as fonts
from . import track_library as lib
from .add_remove_tracks import AddRemoveTracks
from .create_track_list import CreateTrackList
from .gui_helpers import clear_tree, draw_bar_chart, stars_text
from .library_item import AlbumTrack
from .track_statistics import TrackStatistics
from .update_tracks import UpdateTracks
from .validation import get_valid_rating, normalise_track_number
from .view_tracks import TrackViewer


class JukeBoxApp:
    def __init__(self, current_user: str = "Guest", on_logout=None):
        self.window = tk.Tk()
        self.current_user = current_user or "Guest"
        self.on_logout = on_logout
        self.window.title("JukeBox")

        self.open_windows: dict[str, tk.Toplevel] = {}
        self.selected_track_key: str | None = None
        self.current_track_key: str | None = None
        self.cover_image = None
        self.player_cover_image = None
        self._responsive_mode = None
        self._detail_cover_size = 170
        self._player_cover_size = 64

        self._configure_window_size()
        fonts.configure()
        fonts.apply_theme(self.window)
        self._configure_local_styles()

        self.window.columnconfigure(0, minsize=self.sidebar_width)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=0)

        self._build_sidebar()
        self._build_main_area()
        self._build_player_bar()

        self.chart_canvas.bind("<Configure>", lambda event: self._refresh_stats_panel())
        self.window.bind("<Configure>", self._on_window_resize)

        self._populate_library_table(lib.get_track_records())
        self._show_empty_state()
        self._set_player_empty()
        self._refresh_stats_panel()

        self.window.after(120, self._update_responsive_layout)

    def _configure_window_size(self):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        self.compact_screen = screen_width <= 1366 or screen_height <= 768
        self.sidebar_width = 170 if self.compact_screen else 210

        start_width = min(max(int(screen_width * 0.94), 980), screen_width)
        start_height = min(max(int(screen_height * 0.92), 640), screen_height)

        min_width = min(980, max(860, screen_width - 60))
        min_height = min(640, max(560, screen_height - 80))
        self.window.minsize(min_width, min_height)

        if screen_width >= 1500 and screen_height >= 880:
            try:
                self.window.state("zoomed")
                return
            except tk.TclError:
                pass

        pos_x = max(0, (screen_width - start_width) // 2)
        pos_y = max(0, (screen_height - start_height) // 2)
        self.window.geometry(f"{start_width}x{start_height}+{pos_x}+{pos_y}")

    def _configure_local_styles(self):
        style = ttk.Style(self.window)
        button_font = ("Segoe UI", 10 if self.compact_screen else 11, "bold")
        active_font = ("Segoe UI", 10 if self.compact_screen else 11, "bold")

        style.configure(
            "SidebarActive.TButton",
            background=fonts.CARD_ALT,
            foreground=fonts.ACCENT,
            bordercolor=fonts.CARD_ALT,
            relief="flat",
            padding=(14, 10),
            anchor="w",
            font=active_font,
        )
        style.map(
            "SidebarActive.TButton",
            background=[("active", fonts.CARD_ALT), ("pressed", fonts.CARD_ALT)],
            foreground=[("active", fonts.ACCENT), ("pressed", fonts.ACCENT)],
        )

        style.configure(
            "DetailPrimary.TButton",
            background=fonts.ACCENT_SOFT,
            foreground=fonts.TEXT,
            bordercolor=fonts.ACCENT,
            padding=(10, 8),
            font=button_font,
        )
        style.map(
            "DetailPrimary.TButton",
            background=[("active", fonts.ACCENT_DARK), ("pressed", fonts.ACCENT_DARK)],
        )

        style.configure(
            "PlayerGhost.TButton",
            background=fonts.CARD_ALT,
            foreground=fonts.TEXT,
            bordercolor=fonts.CARD_ALT,
            padding=(8, 8),
            font=button_font,
        )
        style.map(
            "PlayerGhost.TButton",
            background=[("active", fonts.SELECT_BG), ("pressed", fonts.SELECT_BG)],
        )

    def _build_sidebar(self):
        self.sidebar = ttk.Frame(self.window, style="Sidebar.TFrame", padding=(16, 18))
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")
        self.sidebar.columnconfigure(0, weight=1)

        ttk.Label(self.sidebar, text="◎", style="Logo.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.sidebar,
            text="JukeBox Music",
            style="Sidebar.TLabel",
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(6, 18))

        user_card = ttk.Frame(self.sidebar, style="Card.TFrame", padding=(12, 10))
        user_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        user_card.columnconfigure(0, weight=1)

        ttk.Label(
            user_card,
            text="Signed in as",
            style="CardMuted.TLabel"
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            user_card,
            text=self.current_user,
            style="CardTitle.TLabel",
            justify="left",
            wraplength=150
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        ttk.Button(
            self.sidebar,
            text="Library",
            style="SidebarActive.TButton",
            command=self.refresh_library,
        ).grid(row=3, column=0, sticky="ew", pady=(0, 8))

        ttk.Button(
            self.sidebar,
            text="Playlist Builder",
            style="Sidebar.TButton",
            command=lambda: self.open_child_window("create_track_list", "Opening Playlist Builder.", CreateTrackList),
        ).grid(row=4, column=0, sticky="ew", pady=3)

        ttk.Button(
            self.sidebar,
            text="Add / Remove",
            style="Sidebar.TButton",
            command=lambda: self.open_child_window("add_remove_tracks", "Opening Add / Remove Tracks.", AddRemoveTracks),
        ).grid(row=5, column=0, sticky="ew", pady=3)

        ttk.Button(
            self.sidebar,
            text="Statistics",
            style="Sidebar.TButton",
            command=lambda: self.open_child_window("statistics", "Opening Statistics window.", TrackStatistics),
        ).grid(row=6, column=0, sticky="ew", pady=3)

        ttk.Button(
            self.sidebar,
            text="Update Tracks",
            style="Sidebar.TButton",
            command=lambda: self.open_child_window("update_tracks", "Opening Update Tracks window.", UpdateTracks),
        ).grid(row=7, column=0, sticky="ew", pady=3)

        ttk.Button(
            self.sidebar,
            text="View Tracks",
            style="Sidebar.TButton",
            command=lambda: self.open_child_window("view_tracks", "Opening Library Browser.", TrackViewer),
        ).grid(row=8, column=0, sticky="ew", pady=3)

        spacer = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        spacer.grid(row=9, column=0, sticky="nsew")
        self.sidebar.rowconfigure(9, weight=1)

        ttk.Button(
            self.sidebar,
            text="Log Out",
            style="Ghost.TButton",
            command=self.logout,
        ).grid(row=10, column=0, sticky="ew", pady=(14, 6))

        ttk.Button(
            self.sidebar,
            text="Close App",
            style="Danger.TButton",
            command=self.window.destroy,
        ).grid(row=11, column=0, sticky="ew")

    def _build_main_area(self):
        self.container = ttk.Frame(self.window, style="Root.TFrame", padding=(16, 14, 16, 10))
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.columnconfigure(0, weight=5)
        self.container.columnconfigure(1, weight=3)
        self.container.rowconfigure(0, weight=0)
        self.container.rowconfigure(1, weight=0)
        self.container.rowconfigure(2, weight=1)

        self.header = ttk.Frame(self.container, style="Root.TFrame")
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        self.header.columnconfigure(0, weight=1)
        self.header.columnconfigure(1, weight=1)

        ttk.Label(self.header, text="Library", style="Hero.TLabel").grid(row=0, column=0, sticky="w")

        self.search_frame = ttk.Frame(self.header, style="Root.TFrame")
        self.search_frame.grid(row=0, column=1, sticky="e")
        self.search_frame.columnconfigure(0, weight=1)

        self.search_entry = ttk.Entry(self.search_frame)
        self.search_entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.search_tracks())

        ttk.Button(
            self.search_frame,
            text="Search",
            style="Neon.TButton",
            command=self.search_tracks,
        ).grid(row=0, column=1)

        self.left_side = ttk.Frame(self.container, style="Root.TFrame")
        self.left_side.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=(0, 10))
        self.left_side.columnconfigure(0, weight=1)
        self.left_side.rowconfigure(1, weight=1)

        self.right_side = ttk.Frame(self.container, style="Root.TFrame")
        self.right_side.grid(row=1, column=1, rowspan=2, sticky="nsew")
        self.right_side.columnconfigure(0, weight=1)
        self.right_side.rowconfigure(0, weight=0)
        self.right_side.rowconfigure(1, weight=1)

        self.control_card = ttk.Frame(self.left_side, style="Card.TFrame", padding=12)
        self.control_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for i in range(5):
            self.control_card.columnconfigure(i, weight=1)

        ttk.Label(self.control_card, text="Quick Filters", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )

        self.rating_filter = ttk.Combobox(
            self.control_card,
            values=["0", "1", "2", "3", "4", "5"],
            state="readonly",
        )
        self.rating_filter.grid(row=0, column=1, padx=6, sticky="ew")
        self.rating_filter.set("1")

        ttk.Button(
            self.control_card,
            text="Filter",
            style="Ghost.TButton",
            command=self.filter_by_rating,
        ).grid(row=0, column=2, padx=6, sticky="ew")

        ttk.Button(
            self.control_card,
            text="Show All",
            style="Ghost.TButton",
            command=self.refresh_library,
        ).grid(row=0, column=3, padx=6, sticky="ew")

        ttk.Button(
            self.control_card,
            text="Play",
            style="Neon.TButton",
            command=self.play_selected_track,
        ).grid(row=1, column=0, pady=(8, 0), sticky="ew")

        ttk.Button(
            self.control_card,
            text="Playlist",
            style="Ghost.TButton",
            command=lambda: self.open_child_window(
                "create_track_list",
                "Opening Playlist Builder.",
                CreateTrackList,
            ),
        ).grid(row=1, column=1, padx=6, pady=(8, 0), sticky="ew")

        ttk.Button(
            self.control_card,
            text="Refresh Stats",
            style="Ghost.TButton",
            command=self._refresh_stats_panel,
        ).grid(row=1, column=2, padx=6, pady=(8, 0), sticky="ew")

        self.table_card = ttk.Frame(self.left_side, style="Card.TFrame", padding=14)
        self.table_card.grid(row=1, column=0, sticky="nsew")
        self.table_card.columnconfigure(0, weight=1)
        self.table_card.rowconfigure(1, weight=1)

        table_header = ttk.Frame(self.table_card, style="Card.TFrame")
        table_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        table_header.columnconfigure(0, weight=1)

        ttk.Label(table_header, text="Track Library", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.result_count_label = ttk.Label(
            table_header,
            text="0 track(s)",
            style="CardMuted.TLabel"
        )
        self.result_count_label.grid(row=0, column=1, sticky="e")

        table_wrap = ttk.Frame(self.table_card, style="Card.TFrame")
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        columns = ("key", "title", "artist", "album", "year", "rating")
        self.library_tree = ttk.Treeview(table_wrap, columns=columns, show="headings")

        headings = {
            "key": ("#", 50),
            "title": ("Song Title", 220),
            "artist": ("Artist", 160),
            "album": ("Album", 160),
            "year": ("Year", 70),
            "rating": ("Rating", 110),
        }

        for column, (label, width) in headings.items():
            self.library_tree.heading(column, text=label)
            self.library_tree.column(column, width=width, anchor="w", stretch=True)

        y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.library_tree.yview)
        x_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.library_tree.xview)
        self.library_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.library_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.library_tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        self.info_card = ttk.Frame(self.right_side, style="Card.TFrame", padding=14)
        self.info_card.grid(row=0, column=0, sticky="nsew")
        self.info_card.columnconfigure(0, weight=1)

        ttk.Label(self.info_card, text="Track Details", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        self.detail_top = ttk.Frame(self.info_card, style="Card.TFrame")
        self.detail_top.grid(row=1, column=0, sticky="ew", pady=(12, 10))
        self.detail_top.columnconfigure(0, weight=0)
        self.detail_top.columnconfigure(1, weight=1)

        self.cover_canvas = tk.Canvas(self.detail_top, width=self._detail_cover_size, height=self._detail_cover_size)
        fonts.style_canvas(self.cover_canvas, bg=fonts.CARD_ALT)
        self.cover_canvas.grid(row=0, column=0, sticky="nw", padx=(0, 12))

        self.meta_wrap = ttk.Frame(self.detail_top, style="Card.TFrame")
        self.meta_wrap.grid(row=0, column=1, sticky="nsew")
        self.meta_wrap.columnconfigure(0, weight=1)

        self.detail_title = ttk.Label(
            self.meta_wrap,
            text="No track selected",
            style="CardTitle.TLabel",
            justify="left",
            wraplength=220,
        )
        self.detail_title.grid(row=0, column=0, sticky="w")

        self.detail_artist = ttk.Label(
            self.meta_wrap,
            text="Artist: —",
            style="CardMuted.TLabel",
            justify="left",
            wraplength=220,
        )
        self.detail_artist.grid(row=1, column=0, sticky="w", pady=(4, 10))

        self.detail_meta = ttk.Label(
            self.meta_wrap,
            text="Album: —\nYear: —\nTimes Played: —\nRating: —",
            style="CardMuted.TLabel",
            justify="left",
            wraplength=220,
        )
        self.detail_meta.grid(row=2, column=0, sticky="nw")

        self.detail_buttons = ttk.Frame(self.info_card, style="Card.TFrame")
        self.detail_buttons.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        self.detail_buttons.columnconfigure(0, weight=1)
        self.detail_buttons.columnconfigure(1, weight=1)

        ttk.Button(
            self.detail_buttons,
            text="Update Info",
            style="Neon.TButton",
            command=lambda: self.open_child_window(
                "update_tracks",
                "Opening Update Tracks window.",
                UpdateTracks
            )
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            self.detail_buttons,
            text="Delete Track",
            style="Danger.TButton",
            command=self.delete_selected_track
        ).grid(row=0, column=1, sticky="ew")

        self.stats_card = ttk.Frame(self.right_side, style="Card.TFrame", padding=14)
        self.stats_card.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        self.stats_card.columnconfigure(0, weight=1)
        self.stats_card.rowconfigure(1, weight=1)

        stats_header = ttk.Frame(self.stats_card, style="Card.TFrame")
        stats_header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        stats_header.columnconfigure(0, weight=1)

        ttk.Label(stats_header, text="Statistics", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.stats_summary = ttk.Label(
            stats_header,
            text="",
            style="CardMuted.TLabel"
        )
        self.stats_summary.grid(row=0, column=1, sticky="e")

        self.chart_canvas = tk.Canvas(self.stats_card, height=190)
        fonts.style_canvas(self.chart_canvas, bg=fonts.CARD)
        self.chart_canvas.grid(row=1, column=0, sticky="nsew")

    def _build_player_bar(self):
        self.player_bar = ttk.Frame(self.window, style="Panel.TFrame", padding=(16, 12))
        self.player_bar.grid(row=1, column=1, sticky="ew", padx=(16, 16), pady=(0, 16))
        self.player_bar.columnconfigure(0, weight=0)
        self.player_bar.columnconfigure(1, weight=0)
        self.player_bar.columnconfigure(2, weight=1)
        self.player_bar.columnconfigure(3, weight=0)

        self.player_left = ttk.Frame(self.player_bar, style="Panel.TFrame")
        self.player_left.grid(row=0, column=0, sticky="w")
        self.player_left.columnconfigure(1, weight=1)

        self.player_cover_canvas = tk.Canvas(
            self.player_left,
            width=self._player_cover_size,
            height=self._player_cover_size,
        )
        fonts.style_canvas(self.player_cover_canvas, bg=fonts.CARD_ALT)
        self.player_cover_canvas.grid(row=0, column=0, padx=(0, 10))

        self.player_info = ttk.Label(
            self.player_left,
            text="No track selected\nChoose a song from the library.",
            style="Panel.TLabel",
            justify="left",
        )
        self.player_info.grid(row=0, column=1, sticky="w")

        self.controls = ttk.Frame(self.player_bar, style="Panel.TFrame")
        self.controls.grid(row=0, column=1, sticky="w", padx=(14, 10))

        ttk.Button(
            self.controls,
            text="◀",
            style="Ghost.TButton",
            command=self._player_previous
        ).pack(side="left")

        ttk.Button(
            self.controls,
            text="▶",
            style="Neon.TButton",
            command=self.play_selected_track
        ).pack(side="left", padx=8)

        ttk.Button(
            self.controls,
            text="▶▶",
            style="Ghost.TButton",
            command=self._player_next
        ).pack(side="left")

        self.progress_wrap = ttk.Frame(self.player_bar, style="Panel.TFrame")
        self.progress_wrap.grid(row=0, column=2, sticky="ew", padx=(8, 8))
        self.progress_wrap.columnconfigure(1, weight=1)

        ttk.Label(self.progress_wrap, text="1:30", style="Panel.TLabel").grid(row=0, column=0, sticky="w")

        self.progress = tk.Scale(
            self.progress_wrap,
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
            sliderlength=12,
        )
        self.progress.grid(row=0, column=1, sticky="ew", padx=10)
        self.progress.set(35)

        ttk.Label(self.progress_wrap, text="3:02", style="Panel.TLabel").grid(row=0, column=2, sticky="e")

        self.volume_wrap = ttk.Frame(self.player_bar, style="Panel.TFrame")
        self.volume_wrap.grid(row=0, column=3, sticky="e")
        ttk.Label(self.volume_wrap, text="🔊", style="Panel.TLabel").pack(side="left", padx=(0, 6))

        self.volume = tk.Scale(
            self.volume_wrap,
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
            sliderlength=12,
            length=110,
        )
        self.volume.pack(side="left")
        self.volume.set(65)

    def _on_window_resize(self, event=None):
        if event is not None and event.widget is not self.window:
            return
        self.window.after_idle(self._update_responsive_layout)

    def _update_responsive_layout(self):
        width = self.window.winfo_width()
        if width <= 1:
            return

        new_mode = "stacked" if width < 1280 else "wide"
        if self._responsive_mode != new_mode:
            self._responsive_mode = new_mode
            self._apply_main_layout(new_mode)
            self._apply_player_layout(new_mode)

        self._detail_cover_size = 130 if width < 1180 else 150 if width < 1450 else 170
        self._player_cover_size = 52 if width < 1180 else 60 if width < 1450 else 64

        self.cover_canvas.configure(width=self._detail_cover_size, height=self._detail_cover_size)
        self.player_cover_canvas.configure(width=self._player_cover_size, height=self._player_cover_size)
        self.volume.configure(length=90 if width < 1180 else 110 if width < 1450 else 130)

        detail_width = max(180, self.info_card.winfo_width() - self._detail_cover_size - 70)
        self.detail_title.configure(wraplength=detail_width)
        self.detail_artist.configure(wraplength=detail_width)
        self.detail_meta.configure(wraplength=detail_width)

        if self.selected_track_key is not None and lib.get_item(self.selected_track_key) is not None:
            self._show_track_detail(self.selected_track_key)
        else:
            self._show_empty_state()

        if self.current_track_key is not None and lib.get_item(self.current_track_key) is not None:
            self._update_player_now_playing(self.current_track_key)
        else:
            self._set_player_empty()

    def _apply_main_layout(self, mode: str):
        if mode == "stacked":
            self.header.grid_configure(row=0, column=0, columnspan=2, sticky="ew")
            self.search_frame.grid_configure(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
            self.left_side.grid_configure(row=1, column=0, columnspan=2, rowspan=1, sticky="nsew", padx=(0, 0), pady=(0, 10))
            self.right_side.grid_configure(row=2, column=0, columnspan=2, rowspan=1, sticky="nsew")
            self.container.rowconfigure(1, weight=3)
            self.container.rowconfigure(2, weight=2)
        else:
            self.header.grid_configure(row=0, column=0, columnspan=2, sticky="ew")
            self.search_frame.grid_configure(row=0, column=1, columnspan=1, sticky="e", pady=(0, 0))
            self.left_side.grid_configure(row=1, column=0, columnspan=1, rowspan=2, sticky="nsew", padx=(0, 10), pady=(0, 0))
            self.right_side.grid_configure(row=1, column=1, columnspan=1, rowspan=2, sticky="nsew")
            self.container.rowconfigure(1, weight=0)
            self.container.rowconfigure(2, weight=1)

    def _apply_player_layout(self, mode: str):
        if mode == "stacked":
            self.player_bar.columnconfigure(0, weight=1)
            self.player_bar.columnconfigure(1, weight=0)
            self.player_bar.columnconfigure(2, weight=0)
            self.player_bar.columnconfigure(3, weight=0)

            self.player_left.grid_configure(row=0, column=0, columnspan=2, sticky="w")
            self.controls.grid_configure(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
            self.progress_wrap.grid_configure(row=2, column=0, columnspan=2, sticky="ew", padx=(0, 0), pady=(10, 0))
            self.volume_wrap.grid_configure(row=1, column=1, sticky="e", pady=(10, 0))
        else:
            self.player_bar.columnconfigure(0, weight=0)
            self.player_bar.columnconfigure(1, weight=0)
            self.player_bar.columnconfigure(2, weight=1)
            self.player_bar.columnconfigure(3, weight=0)

            self.player_left.grid_configure(row=0, column=0, columnspan=1, sticky="w")
            self.controls.grid_configure(row=0, column=1, sticky="w", padx=(14, 10), pady=(0, 0))
            self.progress_wrap.grid_configure(row=0, column=2, columnspan=1, sticky="ew", padx=(8, 8), pady=(0, 0))
            self.volume_wrap.grid_configure(row=0, column=3, sticky="e", pady=(0, 0))

    def _draw_placeholder(self, canvas: tk.Canvas, size: int, title: str, subtitle: str = "", accent=False):
        canvas.delete("all")
        pad = max(6, size // 12)
        mid = size // 2
        outline = fonts.ACCENT if accent else fonts.BORDER
        fill = fonts.CARD_ALT
        canvas.create_rectangle(pad, pad, size - pad, size - pad, outline=outline, width=2, fill=fill)
        if subtitle:
            canvas.create_text(
                mid,
                max(18, int(size * 0.42)),
                text=title,
                fill=fonts.TEXT,
                font=("Segoe UI", 11, "bold"),
                width=max(90, size - 30),
            )
            canvas.create_text(
                mid,
                max(36, int(size * 0.68)),
                text=subtitle,
                fill=fonts.MUTED,
                font=("Segoe UI", 9),
                width=max(80, size - 34),
            )
        else:
            canvas.create_text(
                mid,
                mid,
                text=title,
                fill=fonts.MUTED if not accent else fonts.ACCENT,
                font=("Segoe UI", max(14, size // 3), "bold"),
            )

    def _populate_library_table(self, records: list[dict]):
        clear_tree(self.library_tree)
        for record in records:
            self.library_tree.insert(
                "",
                "end",
                values=(
                    record["key"],
                    record["name"],
                    record["artist"],
                    record["album"] or "Common",
                    record["year"] or "—",
                    stars_text(record["rating"]),
                ),
            )
        self.result_count_label.configure(text=f"{len(records)} track(s)")

    def _show_empty_state(self):
        self.cover_image = None
        self._draw_placeholder(
            self.cover_canvas,
            self._detail_cover_size,
            "No track selected",
            "Select a row to preview.",
            accent=False,
        )
        self.detail_title.configure(text="No track selected")
        self.detail_artist.configure(text="Artist: —")
        self.detail_meta.configure(text="Album: —\nYear: —\nTimes Played: —\nRating: —")

    def _set_player_empty(self):
        self.player_cover_image = None
        self.player_info.configure(text="No track selected\nChoose a song from the library.")
        self._draw_placeholder(self.player_cover_canvas, self._player_cover_size, "♪", accent=False)

    def _update_player_now_playing(self, track_key: str):
        item = lib.get_item(track_key)
        if item is None:
            self._set_player_empty()
            return

        self.player_info.configure(text=f"{item.name}\n{item.artist}")

        self.player_cover_canvas.delete("all")
        self.player_cover_image = cover_manager.load_cover_image(
            track_key,
            max_size=max(44, self._player_cover_size - 4)
        )

        if self.player_cover_image is not None:
            self.player_cover_canvas.create_image(
                self._player_cover_size // 2,
                self._player_cover_size // 2,
                image=self.player_cover_image
            )
        else:
            self._draw_placeholder(self.player_cover_canvas, self._player_cover_size, "♪", accent=True)

    def _show_track_detail(self, track_key: str):
        item = lib.get_item(track_key)
        if item is None:
            self._show_empty_state()
            return

        self.selected_track_key = track_key

        album = item.album if isinstance(item, AlbumTrack) and item.album else "—"
        year = item.year if isinstance(item, AlbumTrack) and item.year is not None else "—"

        self.detail_title.configure(text=item.name)
        self.detail_artist.configure(text=f"Artist: {item.artist}")
        self.detail_meta.configure(
            text=(
                f"Album: {album}\n"
                f"Year: {year}\n"
                f"Times Played: {item.play_count}\n"
                f"Rating: {item.stars()}"
            )
        )

        self.cover_canvas.delete("all")
        self.cover_image = cover_manager.load_cover_image(
            track_key,
            max_size=max(100, self._detail_cover_size - 12)
        )

        if self.cover_image is not None:
            self.cover_canvas.create_image(
                self._detail_cover_size // 2,
                self._detail_cover_size // 2,
                image=self.cover_image
            )
        else:
            self._draw_placeholder(
                self.cover_canvas,
                self._detail_cover_size,
                item.name,
                item.artist,
                accent=True
            )

    def _refresh_stats_panel(self):
        stats = lib.get_statistics()
        self.stats_summary.configure(text=f"{stats['total_tracks']} track(s) • {stats['total_plays']} plays")

        top_tracks = sorted(
            stats["tracks"],
            key=lambda item: (-item["play_count"], item["key"])
        )[:6]

        values = [track["play_count"] for track in top_tracks]
        labels = [track["key"] for track in top_tracks]
        draw_bar_chart(self.chart_canvas, values, labels)

    def _on_tree_select(self, event=None):
        selection = self.library_tree.selection()
        if not selection:
            return
        values = self.library_tree.item(selection[0], "values")
        self._show_track_detail(values[0])

    def refresh_library(self):
        self._populate_library_table(lib.get_track_records())
        self._refresh_stats_panel()
        self.status_message("Library refreshed.")

    def search_tracks(self):
        keyword = self.search_entry.get().strip().lower()
        records = [
            record
            for record in lib.get_track_records()
            if keyword == ""
            or keyword in record["name"].lower()
            or keyword in record["artist"].lower()
            or keyword in (record["album"] or "").lower()
        ]
        self._populate_library_table(records)

        if keyword == "":
            self.status_message("Search box was empty, so all tracks were shown.")
        elif records:
            self.status_message(f"Showing search results for '{keyword}'.")
        else:
            self.status_message("No matching tracks were found.")
            self._show_empty_state()

    def filter_by_rating(self):
        rating = get_valid_rating(self.rating_filter.get(), allow_zero=True)
        if rating is None:
            self.status_message("Filter score must be between 0 and 5.")
            return

        records = [record for record in lib.get_track_records() if record["rating"] == rating]
        self._populate_library_table(records)

        if records:
            self.status_message(f"Showing tracks with rating {rating}.")
        else:
            self.status_message(f"No tracks were found with rating {rating}.")
            self._show_empty_state()

    def play_selected_track(self):
        track_key = self.selected_track_key
        if track_key is None:
            selection = self.library_tree.selection()
            if selection:
                track_key = self.library_tree.item(selection[0], "values")[0]

        if track_key is None:
            self.status_message("Select a track first.")
            return

        track_key = normalise_track_number(track_key)
        if track_key is None or lib.get_name(track_key) is None:
            self.status_message("That track number does not exist.")
            return

        if not lib.increment_play_count(track_key, auto_save=False):
            self.status_message(f"Track {track_key} could not be played.")
            return

        lib.add_history_entry(track_key, source="dashboard")
        lib.save_library()

        self.current_track_key = track_key
        self.selected_track_key = track_key
        self.progress.set(min(100, self.progress.get() + 10))

        self.refresh_library()
        self._show_track_detail(track_key)
        self._update_player_now_playing(track_key)
        self.status_message(f"Now playing: {lib.get_name(track_key)}.")

    def delete_selected_track(self):
        track_key = self.selected_track_key
        if track_key is None:
            self.status_message("Select a track before deleting.")
            return

        track_name = lib.get_name(track_key)
        if track_name is None:
            self.status_message("That track no longer exists.")
            return

        confirmed = messagebox.askyesno(
            "Delete Track",
            f"Are you sure you want to delete track {track_key}: '{track_name}'?",
            parent=self.window,
        )
        if not confirmed:
            self.status_message("Delete track cancelled.")
            return

        if not lib.delete_track(track_key):
            self.status_message("Track could not be deleted.")
            return

        if self.current_track_key == track_key:
            self.current_track_key = None
            self._set_player_empty()

        self.selected_track_key = None
        self.refresh_library()
        self._show_empty_state()
        self.status_message(f"Deleted track {track_key}: '{track_name}'.")

    def _player_previous(self):
        records = lib.get_track_records()
        if not records:
            return

        if self.current_track_key is None:
            self.selected_track_key = records[0]["key"]
            self.play_selected_track()
            return

        keys = [record["key"] for record in records]
        if self.current_track_key not in keys:
            self.current_track_key = keys[0]

        index = keys.index(self.current_track_key)
        self.selected_track_key = keys[(index - 1) % len(keys)]
        self.play_selected_track()

    def _player_next(self):
        records = lib.get_track_records()
        if not records:
            return

        if self.current_track_key is None:
            self.selected_track_key = records[0]["key"]
            self.play_selected_track()
            return

        keys = [record["key"] for record in records]
        if self.current_track_key not in keys:
            self.current_track_key = keys[0]

        index = keys.index(self.current_track_key)
        self.selected_track_key = keys[(index + 1) % len(keys)]
        self.play_selected_track()

    def open_child_window(self, key, status_message, window_class):
        existing_window = self.open_windows.get(key)
        if existing_window is not None and existing_window.winfo_exists():
            existing_window.lift()
            existing_window.focus_force()
            self.status_message(f"{window_class.__name__} is already open.")
            return

        child = tk.Toplevel(self.window)
        self.open_windows[key] = child

        def on_close():
            self.open_windows.pop(key, None)
            child.destroy()
            self.refresh_library()

        child.protocol("WM_DELETE_WINDOW", on_close)
        window_class(child)
        self.status_message(status_message)

    def _close_all_child_windows(self):
        for child in list(self.open_windows.values()):
            if child is not None and child.winfo_exists():
                child.destroy()
        self.open_windows.clear()

    def logout(self):
        confirmed = messagebox.askyesno(
            "Log Out",
            f"Are you sure you want to sign out '{self.current_user}'?",
            parent=self.window,
        )
        if not confirmed:
            return

        self._close_all_child_windows()
        self.window.destroy()

        if callable(self.on_logout):
            self.on_logout()

    def status_message(self, text: str):
        self.window.title(f"JukeBox - {text}")

    def run(self):
        self.window.mainloop()


def main():
    app = JukeBoxApp(current_user="Guest")
    app.run()


if __name__ == "__main__":
    main()