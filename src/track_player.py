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
        self.window.minsize(1380, 820)
        self.window.state("zoomed")

        fonts.configure()
        fonts.apply_theme(self.window)

        self.open_windows: dict[str, tk.Toplevel] = {}
        self.selected_track_key: str | None = None
        self.current_track_key: str | None = None
        self.cover_image = None

        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()
        self._build_player_bar()

        self.chart_canvas.bind("<Configure>", lambda event: self._refresh_stats_panel())
        self._populate_library_table(lib.get_track_records())
        self._show_empty_state()
        self._refresh_stats_panel()

    def _build_sidebar(self):
        sidebar = ttk.Frame(self.window, style="Sidebar.TFrame", padding=18)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.columnconfigure(0, weight=1)

        ttk.Label(sidebar, text="◉", style="Logo.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            sidebar,
            text="JukeBox Music",
            style="Sidebar.TLabel",
            justify="left"
        ).grid(row=1, column=0, sticky="w", pady=(4, 26))

        nav_items = [
            ("Library", self.refresh_library),
            ("Playlist Builder",
             lambda: self.open_child_window("create_track_list", "Opening Playlist Builder.", CreateTrackList)),
            ("Add / Remove",
             lambda: self.open_child_window("add_remove_tracks", "Opening Add / Remove Tracks.", AddRemoveTracks)),
            ("Statistics", lambda: self.open_child_window("statistics", "Opening Statistics window.", TrackStatistics)),
            ("Update Tracks",
             lambda: self.open_child_window("update_tracks", "Opening Update Tracks window.", UpdateTracks)),
            ("View Tracks", lambda: self.open_child_window("view_tracks", "Opening Library Browser.", TrackViewer)),
        ]

        for index, (label, command) in enumerate(nav_items, start=2):
            ttk.Button(sidebar, text=label, style="Sidebar.TButton", command=command).grid(
                row=index, column=0, sticky="ew", pady=4
            )

        ttk.Button(
            sidebar,
            text="Close App",
            style="Danger.TButton",
            command=self.window.destroy
        ).grid(row=20, column=0, sticky="ew", pady=(24, 0))

    def _build_main_area(self):
        container = ttk.Frame(self.window, style="Root.TFrame", padding=(18, 18, 18, 10))
        container.grid(row=0, column=1, sticky="nsew")
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(1, weight=1)
        container.rowconfigure(2, weight=0)

        header = ttk.Frame(container, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=1)
        ttk.Label(header, text="Library", style="Hero.TLabel").grid(row=0, column=0, sticky="w")

        search_frame = ttk.Frame(header, style="Root.TFrame")
        search_frame.grid(row=0, column=1, sticky="e")
        self.search_entry = ttk.Entry(search_frame, width=34)
        self.search_entry.grid(row=0, column=0, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda event: self.search_tracks())
        ttk.Button(search_frame, text="Search", style="Neon.TButton", command=self.search_tracks).grid(row=0, column=1)

        top_filters = ttk.Frame(container, style="Root.TFrame")
        top_filters.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        top_filters.columnconfigure(0, weight=1)
        top_filters.rowconfigure(1, weight=1)

        control_card = ttk.Frame(top_filters, style="Card.TFrame", padding=14)
        control_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        for i in range(4):
            control_card.columnconfigure(i, weight=1)

        ttk.Label(control_card, text="Quick Filters", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )

        self.rating_filter = ttk.Combobox(
            control_card,
            values=["0", "1", "2", "3", "4", "5"],
            state="readonly"
        )
        self.rating_filter.grid(row=0, column=1, padx=8, sticky="ew")
        self.rating_filter.set("5")

        ttk.Button(
            control_card,
            text="Filter",
            style="Ghost.TButton",
            command=self.filter_by_rating
        ).grid(row=0, column=2, padx=8, sticky="ew")

        ttk.Button(
            control_card,
            text="Show All",
            style="Ghost.TButton",
            command=self.refresh_library
        ).grid(row=0, column=3, padx=(8, 0), sticky="ew")

        ttk.Button(
            control_card,
            text="Play",
            style="Neon.TButton",
            command=self.play_selected_track
        ).grid(row=1, column=0, pady=(10, 0), sticky="ew")

        ttk.Button(
            control_card,
            text="Playlist",
            style="Ghost.TButton",
            command=lambda: self.open_child_window(
                "create_track_list",
                "Opening Playlist Builder.",
                CreateTrackList
            )
        ).grid(row=1, column=1, padx=8, pady=(10, 0), sticky="ew")

        ttk.Button(
            control_card,
            text="Refresh Stats",
            style="Ghost.TButton",
            command=self._refresh_stats_panel
        ).grid(row=1, column=2, padx=8, pady=(10, 0), sticky="ew")

        table_card = ttk.Frame(top_filters, style="Card.TFrame", padding=18)
        table_card.grid(row=1, column=0, sticky="nsew")
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)
        table_header = ttk.Frame(table_card, style="Card.TFrame")
        table_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        table_header.columnconfigure(0, weight=1)
        ttk.Label(table_header, text="Track Library", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.result_count_label = ttk.Label(table_header, text="0 tracks", style="CardMuted.TLabel")
        self.result_count_label.grid(row=0, column=1, sticky="e")

        columns = ("key", "title", "artist", "album", "year", "rating")
        self.library_tree = ttk.Treeview(table_card, columns=columns, show="headings")
        headings = {
            "key": ("#", 52),
            "title": ("Song Title", 260),
            "artist": ("Artist", 170),
            "album": ("Album", 190),
            "year": ("Year", 70),
            "rating": ("Rating", 130),
        }
        for column, (label, width) in headings.items():
            self.library_tree.heading(column, text=label)
            self.library_tree.column(column, width=width, anchor="w")
        self.library_tree.grid(row=1, column=0, sticky="nsew")
        self.library_tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        right_side = ttk.Frame(container, style="Root.TFrame")
        right_side.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        right_side.columnconfigure(0, weight=1)
        right_side.rowconfigure(1, weight=1)

        info_card = ttk.Frame(right_side, style="Card.TFrame", padding=18)
        info_card.grid(row=0, column=0, sticky="ew")
        info_card.columnconfigure(0, weight=1)
        ttk.Label(info_card, text="Track Details", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        self.cover_canvas = tk.Canvas(info_card, height=220)
        fonts.style_canvas(self.cover_canvas)
        self.cover_canvas.grid(row=1, column=0, sticky="ew", pady=(12, 12))

        self.detail_title = ttk.Label(info_card, text="No track selected", style="CardTitle.TLabel")
        self.detail_title.grid(row=2, column=0, sticky="w")
        self.detail_artist = ttk.Label(info_card, text="", style="CardMuted.TLabel")
        self.detail_artist.grid(row=3, column=0, sticky="w", pady=(4, 10))
        self.detail_meta = ttk.Label(info_card, text="", style="CardMuted.TLabel", justify="left")
        self.detail_meta.grid(row=4, column=0, sticky="w")

        detail_buttons = ttk.Frame(info_card, style="Card.TFrame")
        detail_buttons.grid(row=5, column=0, sticky="ew", pady=(14, 0))
        detail_buttons.columnconfigure(0, weight=1)
        detail_buttons.columnconfigure(1, weight=1)
        ttk.Button(detail_buttons, text="Update Info", style="Neon.TButton", command=lambda: self.open_child_window("update_tracks", "Opening Update Tracks window.", UpdateTracks)).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(detail_buttons, text="Delete Track", style="Danger.TButton", command=self.delete_selected_track).grid(row=0, column=1, sticky="ew")

        stats_card = ttk.Frame(right_side, style="Card.TFrame", padding=18)
        stats_card.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        stats_card.columnconfigure(0, weight=1)
        stats_card.rowconfigure(1, weight=1)
        stats_header = ttk.Frame(stats_card, style="Card.TFrame")
        stats_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        stats_header.columnconfigure(0, weight=1)
        ttk.Label(stats_header, text="Statistics", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.stats_summary = ttk.Label(stats_header, text="", style="CardMuted.TLabel")
        self.stats_summary.grid(row=0, column=1, sticky="e")
        self.chart_canvas = tk.Canvas(stats_card, height=220)
        fonts.style_canvas(self.chart_canvas)
        self.chart_canvas.grid(row=1, column=0, sticky="nsew")

        status_row = ttk.Frame(container, style="Root.TFrame")
        status_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        status_row.columnconfigure(0, weight=1)
        self.status_lbl = ttk.Label(status_row, text="Ready.", style="Status.TLabel")
        self.status_lbl.grid(row=0, column=0, sticky="w")
        self.online_lbl = ttk.Label(status_row, text="Status: ready ●", style="Status.TLabel")
        self.online_lbl.grid(row=0, column=1, sticky="e")

    def _build_player_bar(self):
        player_bar = ttk.Frame(self.window, style="Panel.TFrame", padding=(18, 14))
        player_bar.place(relx=0.19, rely=0.92, relwidth=0.79, relheight=0.08, anchor="nw")
        player_bar.columnconfigure(1, weight=1)
        player_bar.columnconfigure(2, weight=2)
        player_bar.columnconfigure(3, weight=1)

        self.player_info = ttk.Label(player_bar, text="No track selected\nChoose a song from the library.", style="Panel.TLabel", justify="left")
        self.player_info.grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(player_bar, style="Panel.TFrame")
        controls.grid(row=0, column=1, sticky="ew")
        ttk.Button(controls, text="◀", style="Ghost.TButton", command=self._player_previous).pack(side="left")
        ttk.Button(controls, text="▶", style="Neon.TButton", command=self.play_selected_track).pack(side="left", padx=8)
        ttk.Button(controls, text="▶▶", style="Ghost.TButton", command=self._player_next).pack(side="left")

        self.progress = tk.Scale(player_bar, from_=0, to=100, orient="horizontal", showvalue=False, troughcolor=fonts.CARD_ALT, bg=fonts.PANEL, fg=fonts.TEXT, highlightthickness=0)
        self.progress.grid(row=0, column=2, sticky="ew", padx=14)
        self.progress.set(35)

        self.volume = tk.Scale(player_bar, from_=0, to=100, orient="horizontal", showvalue=False, troughcolor=fonts.CARD_ALT, bg=fonts.PANEL, fg=fonts.TEXT, highlightthickness=0)
        self.volume.grid(row=0, column=3, sticky="ew")
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
        self.cover_canvas.create_rectangle(18, 18, 302, 202, outline=fonts.BORDER, width=2, fill=fonts.CARD_ALT)
        self.cover_canvas.create_text(160, 88, text="No track selected", fill=fonts.TEXT, font=("Segoe UI", 15, "bold"))
        self.cover_canvas.create_text(160, 132, text="Select a row to preview the track here.", fill=fonts.MUTED, font=("Segoe UI", 10), width=220)
        self.detail_title.configure(text="No track selected")
        self.detail_artist.configure(text="")
        self.detail_meta.configure(text="Use the sidebar or the main library table to start.")

    def _show_track_detail(self, track_key: str):
        item = lib.get_item(track_key)
        if item is None:
            self._show_empty_state()
            return
        self.selected_track_key = track_key
        self.detail_title.configure(text=item.name)
        self.detail_artist.configure(text=item.artist)
        album = item.album if isinstance(item, AlbumTrack) and item.album else "—"
        year = item.year if isinstance(item, AlbumTrack) and item.year is not None else "—"
        self.detail_meta.configure(text=f"Album: {album}\nYear: {year}\nTimes Played: {item.play_count}\nRating: {item.stars()}")

        self.cover_canvas.delete("all")
        self.cover_image = cover_manager.load_cover_image(track_key, max_size=190)
        if self.cover_image is not None:
            self.cover_canvas.create_image(160, 110, image=self.cover_image)
        else:
            self.cover_canvas.create_rectangle(18, 18, 302, 202, outline=fonts.ACCENT, width=2, fill=fonts.CARD_ALT)
            self.cover_canvas.create_text(160, 84, text=item.name, fill=fonts.TEXT, font=("Segoe UI", 14, "bold"), width=230)
            self.cover_canvas.create_text(160, 125, text=item.artist, fill=fonts.ACCENT, font=("Segoe UI", 11), width=230)
            self.cover_canvas.create_text(160, 165, text="No cover image found.\nUse 01.png, 02.png ... or default.png", fill=fonts.MUTED, font=("Segoe UI", 10), width=230)

        self.player_info.configure(text=f"{item.name}\n{item.artist}")
        self.status_lbl.configure(text=f"Selected track {track_key}: {item.name}.")

    def _refresh_stats_panel(self):
        stats = lib.get_statistics()
        self.stats_summary.configure(text=f"{stats['total_tracks']} tracks • {stats['total_plays']} plays")
        top_tracks = sorted(stats["tracks"], key=lambda item: (-item["play_count"], item["key"]))[:6]
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
        self.status_lbl.configure(text="Library refreshed.")

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
            self.status_lbl.configure(text="Search box was empty, so all tracks were shown.")
        elif records:
            self.status_lbl.configure(text=f"Showing search results for '{keyword}'.")
        else:
            self.status_lbl.configure(text="No matching tracks were found.")
            self._show_empty_state()

    def filter_by_rating(self):
        rating = get_valid_rating(self.rating_filter.get(), allow_zero=True)
        if rating is None:
            self.status_lbl.configure(text="Filter score must be between 0 and 5.")
            return
        records = [record for record in lib.get_track_records() if record["rating"] == rating]
        self._populate_library_table(records)
        if records:
            self.status_lbl.configure(text=f"Showing tracks with rating {rating}.")
        else:
            self.status_lbl.configure(text=f"No tracks were found with rating {rating}.")
            self._show_empty_state()

    def play_selected_track(self):
        track_key = self.selected_track_key
        if track_key is None:
            selection = self.library_tree.selection()
            if selection:
                track_key = self.library_tree.item(selection[0], "values")[0]
        if track_key is None:
            self.status_lbl.configure(text="Select a track first.")
            return
        track_key = normalise_track_number(track_key)
        if track_key is None or lib.get_name(track_key) is None:
            self.status_lbl.configure(text="That track number does not exist.")
            return
        if not lib.increment_play_count(track_key, auto_save=False):
            self.status_lbl.configure(text=f"Track {track_key} could not be played.")
            return
        lib.add_history_entry(track_key, source="dashboard")
        lib.save_library()
        self.current_track_key = track_key
        self.selected_track_key = track_key
        self.progress.set(min(100, self.progress.get() + 12))
        self.refresh_library()
        self._show_track_detail(track_key)
        self.status_lbl.configure(text=f"Now playing: {lib.get_name(track_key)}.")

    def delete_selected_track(self):
        track_key = self.selected_track_key
        if track_key is None:
            self.status_lbl.configure(text="Select a track before deleting.")
            return
        track_name = lib.get_name(track_key)
        if track_name is None:
            self.status_lbl.configure(text="That track no longer exists.")
            return
        confirmed = messagebox.askyesno("Delete Track", f"Are you sure you want to delete track {track_key}: '{track_name}'?", parent=self.window)
        if not confirmed:
            self.status_lbl.configure(text="Delete track cancelled.")
            return
        if not lib.delete_track(track_key):
            self.status_lbl.configure(text="Track could not be deleted.")
            return
        if self.current_track_key == track_key:
            self.current_track_key = None
            self.player_info.configure(text="No track selected\nChoose a song from the library.")
        self.selected_track_key = None
        self.refresh_library()
        self._show_empty_state()
        self.status_lbl.configure(text=f"Deleted track {track_key}: '{track_name}'.")

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
            self.status_lbl.configure(text=f"{window_class.__name__} is already open.")
            return
        child = tk.Toplevel(self.window)
        self.open_windows[key] = child

        def on_close():
            self.open_windows.pop(key, None)
            child.destroy()
            self.refresh_library()

        child.protocol("WM_DELETE_WINDOW", on_close)
        window_class(child)
        self.status_lbl.configure(text=status_message)

    def run(self):
        self.window.mainloop()


def main():
    app = JukeBoxApp()
    app.run()


if __name__ == "__main__":
    main()