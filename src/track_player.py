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
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("JukeBox")
        self.window.minsize(1450, 860)

        try:
            self.window.state("zoomed")
        except tk.TclError:
            self.window.geometry("1600x920")

        fonts.configure()
        fonts.apply_theme(self.window)
        self._configure_local_styles()

        self.open_windows: dict[str, tk.Toplevel] = {}
        self.selected_track_key: str | None = None
        self.current_track_key: str | None = None
        self.cover_image = None
        self.player_cover_image = None

        self.window.columnconfigure(0, minsize=210)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=0)

        self._build_sidebar()
        self._build_main_area()
        self._build_player_bar()

        self.chart_canvas.bind("<Configure>", lambda event: self._refresh_stats_panel())
        self._populate_library_table(lib.get_track_records())
        self._show_empty_state()
        self._set_player_empty()
        self._refresh_stats_panel()

    def _configure_local_styles(self):
        style = ttk.Style(self.window)

        style.configure(
            "SidebarActive.TButton",
            background=fonts.CARD_ALT,
            foreground=fonts.ACCENT,
            bordercolor=fonts.CARD_ALT,
            relief="flat",
            padding=(16, 12),
            anchor="w",
            font=("Segoe UI", 11, "bold"),
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
            padding=(12, 10),
            font=("Segoe UI", 10, "bold"),
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
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "PlayerGhost.TButton",
            background=[("active", fonts.SELECT_BG), ("pressed", fonts.SELECT_BG)],
        )

    def _build_sidebar(self):
        sidebar = ttk.Frame(self.window, style="Sidebar.TFrame", padding=(18, 22))
        sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")
        sidebar.columnconfigure(0, weight=1)

        ttk.Label(sidebar, text="◎", style="Logo.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            sidebar,
            text="JukeBox Music",
            style="Sidebar.TLabel",
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(6, 28))

        ttk.Button(
            sidebar,
            text="Library",
            style="SidebarActive.TButton",
            command=self.refresh_library,
        ).grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(
            sidebar,
            text="Playlist Builder",
            style="Sidebar.TButton",
            command=lambda: self.open_child_window("create_track_list", "Opening Playlist Builder.", CreateTrackList),
        ).grid(row=3, column=0, sticky="ew", pady=4)

        ttk.Button(
            sidebar,
            text="Add / Remove",
            style="Sidebar.TButton",
            command=lambda: self.open_child_window("add_remove_tracks", "Opening Add / Remove Tracks.", AddRemoveTracks),
        ).grid(row=4, column=0, sticky="ew", pady=4)

        ttk.Button(
            sidebar,
            text="Statistics",
            style="Sidebar.TButton",
            command=lambda: self.open_child_window("statistics", "Opening Statistics window.", TrackStatistics),
        ).grid(row=5, column=0, sticky="ew", pady=4)

        ttk.Button(
            sidebar,
            text="Update Tracks",
            style="Sidebar.TButton",
            command=lambda: self.open_child_window("update_tracks", "Opening Update Tracks window.", UpdateTracks),
        ).grid(row=6, column=0, sticky="ew", pady=4)

        ttk.Button(
            sidebar,
            text="View Tracks",
            style="Sidebar.TButton",
            command=lambda: self.open_child_window("view_tracks", "Opening Library Browser.", TrackViewer),
        ).grid(row=7, column=0, sticky="ew", pady=4)

        spacer = ttk.Frame(sidebar, style="Sidebar.TFrame")
        spacer.grid(row=8, column=0, sticky="nsew")
        sidebar.rowconfigure(8, weight=1)

        ttk.Button(
            sidebar,
            text="Close App",
            style="Danger.TButton",
            command=self.window.destroy,
        ).grid(row=9, column=0, sticky="ew", pady=(18, 0))

    def _build_main_area(self):
        container = ttk.Frame(self.window, style="Root.TFrame", padding=(20, 18, 20, 10))
        container.grid(row=0, column=1, sticky="nsew")
        container.columnconfigure(0, weight=6, minsize=820)
        container.columnconfigure(1, weight=3, minsize=430)
        container.rowconfigure(0, weight=0)
        container.rowconfigure(1, weight=0)
        container.rowconfigure(2, weight=1)

        header = ttk.Frame(container, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=1)

        ttk.Label(header, text="Library", style="Hero.TLabel").grid(row=0, column=0, sticky="w")

        search_frame = ttk.Frame(header, style="Root.TFrame")
        search_frame.grid(row=0, column=1, sticky="e")

        self.search_entry = ttk.Entry(search_frame, width=28)
        self.search_entry.grid(row=0, column=0, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda event: self.search_tracks())

        ttk.Button(
            search_frame,
            text="Search",
            style="Neon.TButton",
            command=self.search_tracks,
        ).grid(row=0, column=1)

        left_side = ttk.Frame(container, style="Root.TFrame")
        left_side.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=(0, 12))
        left_side.columnconfigure(0, weight=1)
        left_side.rowconfigure(1, weight=1)

        right_side = ttk.Frame(container, style="Root.TFrame")
        right_side.grid(row=1, column=1, rowspan=2, sticky="nsew")
        right_side.columnconfigure(0, weight=1)
        right_side.rowconfigure(0, weight=0)
        right_side.rowconfigure(1, weight=1)

        control_card = ttk.Frame(left_side, style="Card.TFrame", padding=14)
        control_card.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        for i in range(5):
            control_card.columnconfigure(i, weight=1)

        ttk.Label(control_card, text="Quick Filters", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )

        self.rating_filter = ttk.Combobox(
            control_card,
            values=["0", "1", "2", "3", "4", "5"],
            state="readonly",
            width=10,
        )
        self.rating_filter.grid(row=0, column=1, padx=8, sticky="ew")
        self.rating_filter.set("1")

        ttk.Button(
            control_card,
            text="Filter",
            style="Ghost.TButton",
            command=self.filter_by_rating,
        ).grid(row=0, column=2, padx=8, sticky="ew")

        ttk.Button(
            control_card,
            text="Show All",
            style="Ghost.TButton",
            command=self.refresh_library,
        ).grid(row=0, column=3, padx=8, sticky="ew")

        ttk.Button(
            control_card,
            text="Play",
            style="Neon.TButton",
            command=self.play_selected_track,
        ).grid(row=1, column=0, pady=(10, 0), sticky="ew")

        ttk.Button(
            control_card,
            text="Playlist",
            style="Ghost.TButton",
            command=lambda: self.open_child_window(
                "create_track_list",
                "Opening Playlist Builder.",
                CreateTrackList,
            ),
        ).grid(row=1, column=1, padx=8, pady=(10, 0), sticky="ew")

        ttk.Button(
            control_card,
            text="Refresh Stats",
            style="Ghost.TButton",
            command=self._refresh_stats_panel,
        ).grid(row=1, column=2, padx=8, pady=(10, 0), sticky="ew")

        table_card = ttk.Frame(left_side, style="Card.TFrame", padding=18)
        table_card.grid(row=1, column=0, sticky="nsew")
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)

        table_header = ttk.Frame(table_card, style="Card.TFrame")
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

        table_wrap = ttk.Frame(table_card, style="Card.TFrame")
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        columns = ("key", "title", "artist", "album", "year", "rating")
        self.library_tree = ttk.Treeview(table_wrap, columns=columns, show="headings")

        headings = {
            "key": ("#", 55),
            "title": ("Song Title", 260),
            "artist": ("Artist", 180),
            "album": ("Album", 180),
            "year": ("Year", 80),
            "rating": ("Rating", 120),
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

        info_card = ttk.Frame(right_side, style="Card.TFrame", padding=18)
        info_card.grid(row=0, column=0, sticky="ew")
        info_card.columnconfigure(0, weight=1)

        ttk.Label(info_card, text="Track Details", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        detail_top = ttk.Frame(info_card, style="Card.TFrame")
        detail_top.grid(row=1, column=0, sticky="ew", pady=(14, 12))
        detail_top.columnconfigure(0, weight=0)
        detail_top.columnconfigure(1, weight=1)

        self.cover_canvas = tk.Canvas(detail_top, width=170, height=170)
        fonts.style_canvas(self.cover_canvas, bg=fonts.CARD_ALT)
        self.cover_canvas.grid(row=0, column=0, sticky="nw", padx=(0, 14))

        meta_wrap = ttk.Frame(detail_top, style="Card.TFrame")
        meta_wrap.grid(row=0, column=1, sticky="nsew")
        meta_wrap.columnconfigure(0, weight=1)

        self.detail_title = ttk.Label(
            meta_wrap,
            text="No track selected",
            style="CardTitle.TLabel",
            justify="left",
            wraplength=220,
        )
        self.detail_title.grid(row=0, column=0, sticky="w")

        self.detail_artist = ttk.Label(
            meta_wrap,
            text="Artist: —",
            style="CardMuted.TLabel",
            justify="left",
            wraplength=220,
        )
        self.detail_artist.grid(row=1, column=0, sticky="w", pady=(4, 10))

        self.detail_meta = ttk.Label(
            meta_wrap,
            text="Album: —\nYear: —\nTimes Played: —\nRating: —",
            style="CardMuted.TLabel",
            justify="left",
            wraplength=220,
        )
        self.detail_meta.grid(row=2, column=0, sticky="nw")

        detail_buttons = ttk.Frame(info_card, style="Card.TFrame")
        detail_buttons.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        detail_buttons.columnconfigure(0, weight=1)
        detail_buttons.columnconfigure(1, weight=1)

        ttk.Button(
            detail_buttons,
            text="Update Info",
            style="Neon.TButton",
            command=lambda: self.open_child_window(
                "update_tracks",
                "Opening Update Tracks window.",
                UpdateTracks
            )
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ttk.Button(
            detail_buttons,
            text="Delete Track",
            style="Danger.TButton",
            command=self.delete_selected_track
        ).grid(row=0, column=1, sticky="ew")

        stats_card = ttk.Frame(right_side, style="Card.TFrame", padding=18)
        stats_card.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        stats_card.columnconfigure(0, weight=1)
        stats_card.rowconfigure(1, weight=1)

        stats_header = ttk.Frame(stats_card, style="Card.TFrame")
        stats_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
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

        self.chart_canvas = tk.Canvas(stats_card, height=200)
        fonts.style_canvas(self.chart_canvas, bg=fonts.CARD)
        self.chart_canvas.grid(row=1, column=0, sticky="nsew")

    def _build_player_bar(self):
        player_bar = ttk.Frame(self.window, style="Panel.TFrame", padding=(18, 14))
        player_bar.grid(row=1, column=1, sticky="ew", padx=(20, 20), pady=(0, 18))
        player_bar.columnconfigure(0, weight=0)
        player_bar.columnconfigure(1, weight=1)
        player_bar.columnconfigure(2, weight=2)
        player_bar.columnconfigure(3, weight=1)

        self.player_info = ttk.Label(
            player_bar,
            text="No track selected\nChoose a song from the library.",
            style="Panel.TLabel",
            justify="left",
        )
        self.player_info.grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(player_bar, style="Panel.TFrame")
        controls.grid(row=0, column=1, sticky="ew", padx=(18, 10))

        ttk.Button(
            controls,
            text="◀",
            style="Ghost.TButton",
            command=self._player_previous
        ).pack(side="left")

        ttk.Button(
            controls,
            text="▶",
            style="Neon.TButton",
            command=self.play_selected_track
        ).pack(side="left", padx=8)

        ttk.Button(
            controls,
            text="▶▶",
            style="Ghost.TButton",
            command=self._player_next
        ).pack(side="left")

        progress_wrap = ttk.Frame(player_bar, style="Panel.TFrame")
        progress_wrap.grid(row=0, column=2, sticky="ew", padx=(10, 10))
        progress_wrap.columnconfigure(1, weight=1)

        ttk.Label(progress_wrap, text="1:30", style="Panel.TLabel").grid(row=0, column=0, sticky="w")

        self.progress = tk.Scale(
            progress_wrap,
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

        ttk.Label(progress_wrap, text="3:02", style="Panel.TLabel").grid(row=0, column=2, sticky="e")

        volume_wrap = ttk.Frame(player_bar, style="Panel.TFrame")
        volume_wrap.grid(row=0, column=3, sticky="e")
        ttk.Label(volume_wrap, text="🔊", style="Panel.TLabel").pack(side="left", padx=(0, 8))

        self.volume = tk.Scale(
            volume_wrap,
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
            length=130,
        )
        self.volume.pack(side="left")
        self.volume.set(65)

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
        self.cover_canvas.delete("all")
        self.cover_canvas.create_rectangle(
            14, 14, 156, 156,
            outline=fonts.BORDER,
            width=2,
            fill=fonts.CARD_ALT
        )
        self.cover_canvas.create_text(
            85, 72,
            text="No track selected",
            fill=fonts.TEXT,
            font=("Segoe UI", 12, "bold"),
            width=110
        )
        self.cover_canvas.create_text(
            85, 112,
            text="Select a row to preview.",
            fill=fonts.MUTED,
            font=("Segoe UI", 9),
            width=110
        )

        self.detail_title.configure(text="No track selected")
        self.detail_artist.configure(text="Artist: —")
        self.detail_meta.configure(text="Album: —\nYear: —\nTimes Played: —\nRating: —")

    def _set_player_empty(self):
        self.player_cover_image = None
        self.player_info.configure(text="No track selected\nChoose a song from the library.")

    def _update_player_now_playing(self, track_key: str):
        item = lib.get_item(track_key)
        if item is None:
            self._set_player_empty()
            return
        self.player_info.configure(text=f"{item.name}\n{item.artist}")

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
        self.cover_image = cover_manager.load_cover_image(track_key, max_size=145)
        if self.cover_image is not None:
            self.cover_canvas.create_image(85, 85, image=self.cover_image)
        else:
            self.cover_canvas.create_rectangle(
                14, 14, 156, 156,
                outline=fonts.ACCENT,
                width=2,
                fill=fonts.CARD_ALT
            )
            self.cover_canvas.create_text(
                85, 66,
                text=item.name,
                fill=fonts.TEXT,
                font=("Segoe UI", 11, "bold"),
                width=110
            )
            self.cover_canvas.create_text(
                85, 98,
                text=item.artist,
                fill=fonts.ACCENT,
                font=("Segoe UI", 10),
                width=110
            )
            self.cover_canvas.create_text(
                85, 128,
                text="No cover image",
                fill=fonts.MUTED,
                font=("Segoe UI", 9),
                width=100
            )

        self.player_info.configure(text=f"{item.name}\n{item.artist}")

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

    def status_message(self, text: str):
        self.window.title(f"JukeBox - {text}")

    def run(self):
        self.window.mainloop()


def main():
    app = JukeBoxApp()
    app.run()


if __name__ == "__main__":
    main()