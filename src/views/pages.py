"""Page-level views displayed in the main JukeBox window."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..models import cover_manager
from ..models import track_library as lib
from ..models.library_item import AlbumTrack
from ..models.validation import get_valid_rating
from . import font_manager as fonts
from .add_remove_tracks import AddRemoveTracks
from .create_track_list import CreateTrackList
from .gui_helpers import clear_tree, create_scrollable_column, stars_text
from .track_statistics import TrackStatistics
from .update_lyrics import UpdateLyrics
from .update_tracks import UpdateTracks


class NowPlayingPage:
    STACK_BREAKPOINT = 980

    def __init__(self, parent, app):
        self.app = app
        self.cover_image = None
        self.frame = ttk.Frame(parent, style="Root.TFrame")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        app.register_page("now_playing", self)

        self._scroll_host = ttk.Frame(self.frame, style="Root.TFrame")
        self._scroll_host.grid(row=0, column=0, sticky="nsew")
        self._content = create_scrollable_column(self._scroll_host)
        self._content.columnconfigure(0, weight=1)
        self._content.columnconfigure(1, weight=1)

        self._is_stacked: bool | None = None
        self._build()
        self._content.bind("<Configure>", self._on_resize)
        self.on_show()

    def _build(self):
        container = self._content
        container.columnconfigure(0, weight=0)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Manage Playback", style="Hero.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Enjoy your music — lyrics, cover art and metadata in one glance.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        # ===== Left column: cover + meta =====
        left = ttk.Frame(container, style="Card.TFrame", padding=24)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 14))
        left.columnconfigure(0, weight=1)
        self.left_card = left

        self.tag_lbl = ttk.Label(left, text="◈  NOW PLAYING", style="Tag.TLabel")
        self.tag_lbl.grid(row=0, column=0, sticky="w", pady=(0, 14))

        cover_wrap = ttk.Frame(left, style="Card.TFrame")
        cover_wrap.grid(row=1, column=0, sticky="n")

        self.cover_canvas = tk.Canvas(cover_wrap, width=320, height=320)
        fonts.style_canvas(self.cover_canvas, bg=fonts.CARD_ALT)
        self.cover_canvas.grid(row=0, column=0)

        self.title_lbl = ttk.Label(
            left,
            text="No track loaded",
            background=fonts.CARD,
            foreground=fonts.TEXT,
            font=fonts._ff(22, "bold"),
            wraplength=320,
            justify="left",
        )
        self.title_lbl.grid(row=2, column=0, sticky="w", pady=(20, 4))

        self.artist_lbl = ttk.Label(
            left,
            text="Pick a track to start playing",
            background=fonts.CARD,
            foreground=fonts.ACCENT_GLOW,
            font=fonts._ff(13),
            wraplength=320,
            justify="left",
        )
        self.artist_lbl.grid(row=3, column=0, sticky="w", pady=(0, 18))

        meta_grid = ttk.Frame(left, style="Card.TFrame")
        meta_grid.grid(row=4, column=0, sticky="ew")
        meta_grid.columnconfigure(0, weight=1)
        meta_grid.columnconfigure(1, weight=1)

        self.meta_labels = {}
        meta_keys = [("Album", "album"), ("Year", "year"), ("Plays", "plays"), ("Rating", "rating")]
        for idx, (label, key) in enumerate(meta_keys):
            row = idx // 2
            col = idx % 2
            cell = ttk.Frame(meta_grid, style="Card.TFrame", padding=(0, 0, 16, 12))
            cell.grid(row=row, column=col, sticky="w")
            ttk.Label(cell, text=label.upper(), style="CardSubtitle.TLabel").grid(row=0, column=0, sticky="w")
            value = ttk.Label(
                cell,
                text="—",
                background=fonts.CARD,
                foreground=fonts.TEXT,
                font=fonts._ff(12, "bold"),
                wraplength=150,
                justify="left",
            )
            value.grid(row=1, column=0, sticky="w", pady=(4, 0))
            self.meta_labels[key] = value

        actions = ttk.Frame(left, style="Card.TFrame")
        actions.grid(row=5, column=0, sticky="ew", pady=(18, 0))
        actions.columnconfigure(0, weight=1)

        ttk.Button(
            actions,
            text="Go to Library",
            style="Ghost.TButton",
            command=lambda: self.app.switch_page("library"),
        ).grid(row=0, column=0, sticky="ew")

        # ===== Right column: lyrics =====
        right = ttk.Frame(container, style="Card.TFrame", padding=24)
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)
        self.right_card = right

        ttk.Label(right, text="LYRICS", style="Tag.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.lyrics_heading = ttk.Label(
            right,
            text="No track loaded",
            background=fonts.CARD,
            foreground=fonts.ACCENT_GLOW,
            font=fonts._ff(14, "bold"),
            wraplength=520,
            justify="left",
        )
        self.lyrics_heading.grid(row=1, column=0, sticky="w", pady=(0, 14))

        lyrics_wrap = ttk.Frame(right, style="Card.TFrame")
        lyrics_wrap.grid(row=2, column=0, sticky="nsew")
        lyrics_wrap.columnconfigure(0, weight=1)
        lyrics_wrap.rowconfigure(0, weight=1)

        self.lyrics_txt = tk.Text(
            lyrics_wrap,
            wrap="word",
            width=1,
            height=1,
            padx=18,
            pady=16,
            spacing1=2,
            spacing3=4,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
        )
        fonts.style_text_widget(self.lyrics_txt)
        self.lyrics_txt.configure(font=fonts._ff(12), bg=fonts.CARD_ALT, fg=fonts.TEXT_SOFT)
        self.lyrics_txt.grid(row=0, column=0, sticky="nsew")

        lyrics_scroll = ttk.Scrollbar(lyrics_wrap, orient="vertical", command=self.lyrics_txt.yview)
        self.lyrics_txt.configure(yscrollcommand=lyrics_scroll.set)
        lyrics_scroll.grid(row=0, column=1, sticky="ns")

        self._set_lyrics_text("Pick a track to see its lyrics here.", placeholder=True)

    def _set_lyrics_text(self, text: str, placeholder: bool = False):
        self.lyrics_txt.configure(state="normal")
        self.lyrics_txt.delete("1.0", tk.END)
        if text:
            self.lyrics_txt.insert("1.0", text)
        self.lyrics_txt.configure(
            state="disabled",
            fg=fonts.MUTED if placeholder else fonts.TEXT_SOFT,
        )

    def _on_resize(self, event=None):
        if event is not None and event.widget is not self._content:
            return
        width = self._content.winfo_width()
        if width <= 1:
            return

        stacked = width < self.STACK_BREAKPOINT
        if stacked != self._is_stacked:
            if stacked:
                self.left_card.grid_configure(row=1, column=0, columnspan=2, padx=0)
                self.right_card.grid_configure(row=2, column=0, columnspan=2, padx=0, pady=(14, 0))
                self._content.rowconfigure(1, weight=0)
                self._content.rowconfigure(2, weight=1)
                self._content.columnconfigure(1, weight=0)
            else:
                self.left_card.grid_configure(row=1, column=0, columnspan=1, padx=(0, 14))
                self.right_card.grid_configure(row=1, column=1, columnspan=1, padx=0, pady=0)
                self._content.rowconfigure(1, weight=1)
                self._content.rowconfigure(2, weight=0)
                self._content.columnconfigure(1, weight=1)
            self._is_stacked = stacked

        left_w = max(220, self.left_card.winfo_width() - 60)
        right_w = max(280, self.right_card.winfo_width() - 60)
        self.title_lbl.configure(wraplength=left_w)
        self.artist_lbl.configure(wraplength=left_w)
        self.lyrics_heading.configure(wraplength=right_w)

    def on_show(self):
        self._draw_cover()
        self._draw_meta()

    def on_library_change(self):
        self.on_show()

    def _draw_cover(self):
        self.cover_canvas.delete("all")
        key = self.app.current_track_key

        if key is None:
            self.app._draw_cover_placeholder(self.cover_canvas, 320, "♪")
            return

        self.cover_image = cover_manager.load_cover_image(key, max_size=300)
        if self.cover_image is not None:
            self.cover_canvas.create_image(160, 160, image=self.cover_image)
        else:
            self.app._draw_cover_placeholder(self.cover_canvas, 320, "♪", accent=True)

    def _draw_meta(self):
        key = self.app.current_track_key
        item = lib.get_item(key) if key else None

        if item is None:
            self.title_lbl.configure(text="No track loaded")
            self.artist_lbl.configure(text="Pick a track to start playing")
            for label in self.meta_labels.values():
                label.configure(text="—")
            self.lyrics_heading.configure(text="No track loaded")
            self._set_lyrics_text("Pick a track to see its lyrics here.", placeholder=True)
            return

        album = item.album if isinstance(item, AlbumTrack) and item.album else "—"
        year = item.year if isinstance(item, AlbumTrack) and item.year is not None else "—"

        self.title_lbl.configure(text=item.name)
        self.artist_lbl.configure(text=item.artist)
        self.meta_labels["album"].configure(text=str(album))
        self.meta_labels["year"].configure(text=str(year))
        self.meta_labels["plays"].configure(text=str(item.play_count))
        self.meta_labels["rating"].configure(text=item.stars())

        self.lyrics_heading.configure(text=f"{item.name} — {item.artist}")
        if item.lyrics:
            self._set_lyrics_text(item.lyrics)
        else:
            self._set_lyrics_text(
                "No lyrics yet. Open Manage → Lyrics tab to add some.",
                placeholder=True,
            )


class LibraryPage:
    def __init__(self, parent, app):
        self.app = app
        self.cover_image = None
        self.selected_key: str | None = None
        self.frame = ttk.Frame(parent, style="Root.TFrame")
        self.frame.columnconfigure(0, weight=3)
        self.frame.columnconfigure(1, weight=2)
        self.frame.rowconfigure(2, weight=1)
        app.register_page("library", self)

        self._build_header()
        self._build_toolbar()
        self._build_body()
        self.refresh_tree()
        self._show_empty_detail()

    def _build_header(self):
        header = ttk.Frame(self.frame, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Manage Library", style="Hero.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Browse, search and filter your entire track collection.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _build_toolbar(self):
        toolbar = ttk.Frame(self.frame, style="Card.TFrame", padding=14)
        toolbar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        toolbar.columnconfigure(1, weight=1)

        ttk.Label(toolbar, text="⌕", style="CardTitle.TLabel").grid(row=0, column=0, padx=(4, 10))

        self.search_entry = ttk.Entry(toolbar)
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.bind("<Return>", lambda e: self.apply_filters())
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

        ttk.Button(toolbar, text="Search", style="Neon.TButton", command=self.apply_filters).grid(
            row=0, column=2, padx=(10, 0)
        )

        ttk.Label(toolbar, text="Rating", style="CardMuted.TLabel").grid(row=0, column=3, padx=(20, 6))

        self.rating_filter = ttk.Combobox(
            toolbar,
            values=["Any", "0", "1", "2", "3", "4", "5"],
            state="readonly",
            width=5,
        )
        self.rating_filter.grid(row=0, column=4)
        self.rating_filter.set("Any")
        self.rating_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Button(
            toolbar, text="Show All", style="Chip.TButton", command=self.reset_filters
        ).grid(row=0, column=5, padx=(10, 0))

    def _build_body(self):
        table_card = ttk.Frame(self.frame, style="Card.TFrame", padding=16)
        table_card.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)

        th = ttk.Frame(table_card, style="Card.TFrame")
        th.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        th.columnconfigure(0, weight=1)
        ttk.Label(th, text="Tracks", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.count_lbl = ttk.Label(th, text="0 track(s)", style="CardMuted.TLabel")
        self.count_lbl.grid(row=0, column=1, sticky="e")

        wrap = ttk.Frame(table_card, style="Card.TFrame")
        wrap.grid(row=1, column=0, sticky="nsew")
        wrap.columnconfigure(0, weight=1)
        wrap.rowconfigure(0, weight=1)

        columns = ("key", "title", "artist", "album", "year", "rating")
        self.tree = ttk.Treeview(wrap, columns=columns, show="headings")

        headings = {
            "key": ("#", 50),
            "title": ("Title", 220),
            "artist": ("Artist", 160),
            "album": ("Album", 150),
            "year": ("Year", 70),
            "rating": ("Rating", 100),
        }
        for col, (label, width) in headings.items():
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w", stretch=True)

        y = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        x = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y.set, xscrollcommand=x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y.grid(row=0, column=1, sticky="ns")
        x.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        self._build_detail_card()

    def _build_detail_card(self):
        card = ttk.Frame(self.frame, style="Card.TFrame", padding=18)
        card.grid(row=2, column=1, sticky="nsew")
        card.columnconfigure(0, weight=1)
        self.detail_card = card
        card.bind("<Configure>", self._on_detail_resize)

        ttk.Label(card, text="Details", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        self.cover_canvas = tk.Canvas(card, width=180, height=180)
        fonts.style_canvas(self.cover_canvas, bg=fonts.CARD_ALT)
        self.cover_canvas.grid(row=1, column=0, pady=(14, 16))

        self.title_lbl = ttk.Label(
            card,
            text="No track selected",
            style="CardTitle.TLabel",
            wraplength=260,
            justify="left",
        )
        self.title_lbl.grid(row=2, column=0, sticky="w")

        self.artist_lbl = ttk.Label(card, text="—", style="CardMuted.TLabel", wraplength=260, justify="left")
        self.artist_lbl.grid(row=3, column=0, sticky="w", pady=(4, 12))

        self.meta_lbl = ttk.Label(
            card,
            text="Album: —\nYear: —\nPlays: —\nRating: —",
            style="CardMuted.TLabel",
            justify="left",
        )
        self.meta_lbl.grid(row=4, column=0, sticky="w")

        action = ttk.Frame(card, style="Card.TFrame")
        action.grid(row=5, column=0, sticky="ew", pady=(18, 0))
        action.columnconfigure(0, weight=1)

        ttk.Button(action, text="▶  Play", style="Neon.TButton", command=self._play_selected).grid(
            row=0, column=0, sticky="ew"
        )

    def refresh_tree(self, records: list[dict] | None = None):
        data = records if records is not None else lib.get_track_records()
        clear_tree(self.tree)
        for rec in data:
            self.tree.insert(
                "",
                "end",
                values=(
                    rec["key"],
                    rec["name"],
                    rec["artist"],
                    rec["album"] or "—",
                    rec["year"] or "—",
                    stars_text(rec["rating"]),
                ),
            )
        self.count_lbl.configure(text=f"{len(data)} track(s)")

    def on_library_change(self):
        self.refresh_tree()
        if self.selected_key and lib.get_item(self.selected_key) is not None:
            self._show_detail(self.selected_key)
        else:
            self.selected_key = None
            self._show_empty_detail()

    def on_show(self):
        self.refresh_tree()

    def _show_detail(self, key: str):
        item = lib.get_item(key)
        if item is None:
            self._show_empty_detail()
            return

        album = item.album if isinstance(item, AlbumTrack) and item.album else "—"
        year = item.year if isinstance(item, AlbumTrack) and item.year is not None else "—"

        self.title_lbl.configure(text=item.name)
        self.artist_lbl.configure(text=item.artist)
        self.meta_lbl.configure(
            text=(
                f"Album: {album}\n"
                f"Year: {year}\n"
                f"Plays: {item.play_count}\n"
                f"Rating: {item.stars()}"
            )
        )

        self.cover_canvas.delete("all")
        self.cover_image = cover_manager.load_cover_image(key, max_size=170)
        if self.cover_image is not None:
            self.cover_canvas.create_image(90, 90, image=self.cover_image)
        else:
            self.app._draw_cover_placeholder(self.cover_canvas, 180, "♪", accent=True)

    def _show_empty_detail(self):
        self.cover_image = None
        self.app._draw_cover_placeholder(self.cover_canvas, 180, "♪")
        self.title_lbl.configure(text="No track selected")
        self.artist_lbl.configure(text="Pick a row on the left")
        self.meta_lbl.configure(text="Album: —\nYear: —\nPlays: —\nRating: —")

    def _on_detail_resize(self, event=None):
        if event is not None and event.widget is not self.detail_card:
            return
        width = self.detail_card.winfo_width()
        if width <= 1:
            return
        wrap = max(200, width - 40)
        self.title_lbl.configure(wraplength=wrap)
        self.artist_lbl.configure(wraplength=wrap)
        self.meta_lbl.configure(wraplength=wrap)

    def _on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        self.selected_key = values[0]
        self._show_detail(values[0])

    def _on_double_click(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        self.app.play_track(values[0])

    def apply_filters(self):
        keyword = self.search_entry.get().strip().lower()
        rating_raw = self.rating_filter.get()
        rating = None if rating_raw == "Any" else get_valid_rating(rating_raw, allow_zero=True)

        records = []
        for r in lib.get_track_records():
            if keyword and not (
                keyword in r["name"].lower()
                or keyword in r["artist"].lower()
                or keyword in (r["album"] or "").lower()
            ):
                continue
            if rating is not None and r["rating"] != rating:
                continue
            records.append(r)

        self.refresh_tree(records)

    def reset_filters(self):
        self.search_entry.delete(0, tk.END)
        self.rating_filter.set("Any")
        self.refresh_tree()

    def _play_selected(self):
        if self.selected_key is None:
            return
        self.app.play_track(self.selected_key)


class ManagePage:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent, style="Root.TFrame")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        app.register_page("manage", self)

        self._build()

    def _build(self):
        header = ttk.Frame(self.frame, style="Root.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Manage Tracks", style="Hero.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Add new tracks, update metadata or browse details.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        notebook = ttk.Notebook(self.frame)
        notebook.grid(row=1, column=0, sticky="nsew")

        create_frame = ttk.Frame(notebook, style="Root.TFrame")
        update_frame = ttk.Frame(notebook, style="Root.TFrame")
        delete_frame = ttk.Frame(notebook, style="Root.TFrame")
        lyrics_frame = ttk.Frame(notebook, style="Root.TFrame")

        notebook.add(create_frame, text="   ✚  Create   ")
        notebook.add(update_frame, text="   ✎  Update   ")
        notebook.add(delete_frame, text="   ✕  Delete   ")
        notebook.add(lyrics_frame, text="   ♬  Lyrics   ")

        self.create_tool = AddRemoveTracks(create_frame, mode="add")
        self.update_tool = UpdateTracks(update_frame)
        self.delete_tool = AddRemoveTracks(delete_frame, mode="remove")
        self.lyrics_tool = UpdateLyrics(lyrics_frame)

        self.create_tool.app_ref = self.app
        self.update_tool.app_ref = self.app
        self.delete_tool.app_ref = self.app
        self.lyrics_tool.app_ref = self.app

    def on_library_change(self):
        for tool in (self.create_tool, self.delete_tool):
            if hasattr(tool, "refresh_list"):
                tool.refresh_list()
        if hasattr(self.update_tool, "list_tracks_clicked"):
            self.update_tool.list_tracks_clicked()
        if hasattr(self.lyrics_tool, "list_tracks_clicked"):
            self.lyrics_tool.list_tracks_clicked()


class PlaylistsPage:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent, style="Root.TFrame")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        app.register_page("playlists", self)

        self.tool = CreateTrackList(self.frame)
        self.tool.app_ref = self.app

    def on_library_change(self):
        if hasattr(self.tool, "list_tracks_clicked"):
            self.tool.list_tracks_clicked()


class StatisticsPage:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.Frame(parent, style="Root.TFrame")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        app.register_page("statistics", self)

        self.tool = TrackStatistics(self.frame)

    def on_show(self):
        if hasattr(self.tool, "show_statistics_clicked"):
            self.tool.show_statistics_clicked()

    def on_library_change(self):
        self.on_show()
