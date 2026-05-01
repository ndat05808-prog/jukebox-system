import tkinter as tk
from tkinter import ttk

from ..models import cover_manager
from . import font_manager as fonts
from ..models import track_library as lib
from .gui_helpers import clear_tree, setup_page_container, stars_text
from ..models.library_item import AlbumTrack
from ..models.validation import get_valid_rating, normalise_track_number


class TrackViewer:
    def __init__(self, window):
        self.window = window
        self.cover_image = None

        setup_page_container(
            window,
            title="View Tracks",
            geometry="1280x820",
            minsize=(1120, 720),
        )

        window.columnconfigure(0, weight=3, uniform="main_cols")
        window.columnconfigure(1, weight=1, uniform="main_cols")
        window.rowconfigure(2, weight=1)

        header = ttk.Frame(window, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(18, 8))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Library Browser",
            style="Hero.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            header,
            text="This replaces the old text-heavy viewer with a cleaner dashboard-style layout.",
            style="Muted.TLabel"
        ).grid(row=1, column=0, sticky="w")

        self._build_toolbar()
        self._build_main_panels()

        self.status_lbl = ttk.Label(window, text="Ready.", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 16))

        self.window.bind("<Configure>", self._on_resize)

        self.list_tracks_clicked()
        self.display_empty_state()

    def _build_toolbar(self):
        toolbar_card = ttk.Frame(self.window, style="Card.TFrame", padding=14)
        toolbar_card.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=10)

        toolbar_card.columnconfigure(0, weight=3)
        toolbar_card.columnconfigure(2, weight=1)

        self.search_txt = ttk.Entry(toolbar_card)
        self.search_txt.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.search_txt.bind("<Return>", lambda event: self.search_tracks_clicked())

        ttk.Button(
            toolbar_card,
            text="Search",
            style="Neon.TButton",
            command=self.search_tracks_clicked
        ).grid(row=0, column=1, sticky="ew", padx=8)

        self.rating_filter_txt = ttk.Combobox(
            toolbar_card,
            values=["0", "1", "2", "3", "4", "5"],
            state="readonly"
        )
        self.rating_filter_txt.grid(row=0, column=2, sticky="ew", padx=8)
        self.rating_filter_txt.set("5")

        ttk.Button(
            toolbar_card,
            text="Filter Rating",
            style="Ghost.TButton",
            command=self.filter_by_score_clicked
        ).grid(row=0, column=3, sticky="ew", padx=(8, 0))

    def _build_main_panels(self):
        left = ttk.Frame(self.window, style="Root.TFrame")
        left.grid(row=2, column=0, sticky="nsew", padx=(18, 10), pady=10)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        right = ttk.Frame(self.window, style="Root.TFrame")
        right.grid(row=2, column=1, sticky="nsew", padx=(10, 18), pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        library_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        library_card.grid(row=0, column=0, sticky="nsew")
        library_card.columnconfigure(0, weight=1)
        library_card.rowconfigure(1, weight=1)

        header = ttk.Frame(library_card, style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Library",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            header,
            text="Show All",
            style="Ghost.TButton",
            command=self.list_tracks_clicked
        ).grid(row=0, column=1, sticky="e")

        table_wrap = ttk.Frame(library_card, style="Card.TFrame")
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        columns = ("key", "title", "artist", "album", "year", "rating")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings")

        headers = {
            "key": ("#", 55),
            "title": ("Song Title", 260),
            "artist": ("Artist", 180),
            "album": ("Album", 180),
            "year": ("Year", 80),
            "rating": ("Rating", 130),
        }

        for column, (label, width) in headers.items():
            self.tree.heading(column, text=label)
            self.tree.column(column, width=width, anchor="w", stretch=True)

        tree_y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        tree_x_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=tree_y_scroll.set,
            xscrollcommand=tree_x_scroll.set
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_y_scroll.grid(row=0, column=1, sticky="ns")
        tree_x_scroll.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self._select_track_from_tree)

        self.detail_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        self.detail_card.grid(row=0, column=0, sticky="nsew")
        self.detail_card.columnconfigure(0, weight=1)
        self.detail_card.rowconfigure(3, weight=1)

        ttk.Label(
            self.detail_card,
            text="Selected Track",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.cover_canvas = tk.Canvas(self.detail_card, width=200, height=200)
        fonts.style_canvas(self.cover_canvas)
        self.cover_canvas.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        self.title_lbl = ttk.Label(
            self.detail_card,
            text="No Track Selected",
            style="CardTitle.TLabel",
            justify="left",
            wraplength=260
        )
        self.title_lbl.grid(row=2, column=0, sticky="w", pady=(0, 8))

        self.detail_message = tk.Message(
            self.detail_card,
            text="Choose a track number or click a row to see details.",
            width=280,
            justify="left",
            anchor="nw",
            bg=fonts.INPUT_BG,
            fg=fonts.TEXT,
            font=("Segoe UI", 10),
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=fonts.BORDER,
            highlightcolor=fonts.ACCENT,
            padx=10,
            pady=10,
        )
        self.detail_message.grid(row=3, column=0, sticky="nsew")

    def _on_resize(self, event=None):
        if event is not None and event.widget is not self.window:
            return

        if not hasattr(self, "detail_card"):
            return

        width = max(240, self.detail_card.winfo_width() - 50)
        self.title_lbl.configure(wraplength=width)
        self.detail_message.configure(width=max(220, width - 20))

    def _set_detail_text(self, text: str):
        self.detail_message.configure(text=text)

    def _populate_tree(self, records):
        clear_tree(self.tree)
        for record in records:
            self.tree.insert(
                "",
                "end",
                values=(
                    record["key"],
                    record["name"],
                    record["artist"],
                    record["album"] or "—",
                    record["year"] or "—",
                    stars_text(record["rating"]),
                ),
            )

    def _select_track_from_tree(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.show_track(values[0])

    def display_empty_state(self):
        self.cover_image = None
        self.cover_canvas.delete("all")
        self.cover_canvas.create_rectangle(
            16, 16, 184, 184,
            outline=fonts.BORDER,
            width=2,
            fill=fonts.CARD_ALT
        )
        self.cover_canvas.create_text(
            100, 88,
            text="No Track Selected",
            fill=fonts.TEXT,
            font=("Segoe UI", 13, "bold"),
            width=140
        )
        self.cover_canvas.create_text(
            100, 138,
            text="Select a track from the table to preview it.",
            fill=fonts.MUTED,
            font=("Segoe UI", 10),
            width=145
        )

        self.title_lbl.configure(text="No Track Selected")
        self._set_detail_text("Choose a track number or click a row to see details.")

    def display_track_cover(self, track_key: str):
        track_name = lib.get_name(track_key) or "Unknown Track"
        artist_name = lib.get_artist(track_key) or "Unknown Artist"

        self.cover_canvas.delete("all")
        self.cover_image = cover_manager.load_cover_image(track_key, max_size=170)

        if self.cover_image is not None:
            self.cover_canvas.create_image(100, 100, image=self.cover_image)
            return

        self.cover_canvas.create_rectangle(
            16, 16, 184, 184,
            outline=fonts.ACCENT,
            width=2,
            fill=fonts.CARD_ALT
        )
        self.cover_canvas.create_text(
            100, 78,
            text=track_name,
            fill=fonts.TEXT,
            font=("Segoe UI", 13, "bold"),
            width=140
        )
        self.cover_canvas.create_text(
            100, 116,
            text=artist_name,
            fill=fonts.ACCENT,
            font=("Segoe UI", 11),
            width=140
        )
        self.cover_canvas.create_text(
            100, 154,
            text="No cover image found.",
            fill=fonts.MUTED,
            font=("Segoe UI", 10),
            width=140
        )

    def show_track(self, track_key: str):
        track_key = normalise_track_number(track_key)
        if track_key is None:
            self.display_empty_state()
            self._set_detail_text("Track number must contain digits only.")
            self.status_lbl.configure(text="Track number must contain digits only.")
            return

        item = lib.get_item(track_key)
        if item is None:
            self.display_empty_state()
            self._set_detail_text(f"No track exists with number {track_key}.")
            self.status_lbl.configure(text="That track number does not exist.")
            return

        self.display_track_cover(track_key)

        album = item.album if isinstance(item, AlbumTrack) and item.album else "—"
        year = item.year if isinstance(item, AlbumTrack) and item.year is not None else "—"

        self.title_lbl.configure(text=item.name)

        detail_lines = [
            f"Artist: {item.artist}",
            f"Album: {album}",
            f"Year: {year}",
            f"Times Played: {item.play_count}",
            f"Rating: {item.stars()}",
            "",
            "Full Details:",
            lib.get_details(track_key) or ""
        ]

        self._set_detail_text("\n".join(detail_lines))
        self.status_lbl.configure(text=f"Showing details for track {track_key}.")

    def list_tracks_clicked(self):
        self._populate_tree(lib.get_track_records())
        self.status_lbl.configure(text="All tracks are now displayed.")

    def search_tracks_clicked(self):
        keyword = self.search_txt.get().strip().lower()
        records = [
            record for record in lib.get_track_records()
            if keyword == ""
            or keyword in record["name"].lower()
            or keyword in record["artist"].lower()
            or keyword in (record["album"] or "").lower()
        ]

        self._populate_tree(records)

        if records:
            self.status_lbl.configure(
                text=f"Showing search results for '{self.search_txt.get().strip() or 'all tracks'}'."
            )
        else:
            self.status_lbl.configure(text="Search finished: 0 matches.")
            self.display_empty_state()

    def filter_by_score_clicked(self):
        rating = get_valid_rating(self.rating_filter_txt.get(), allow_zero=True)
        if rating is None:
            self.status_lbl.configure(text="Filter score must be between 0 and 5.")
            return

        records = [
            record for record in lib.get_track_records()
            if record["rating"] == rating
        ]

        self._populate_tree(records)

        if records:
            self.status_lbl.configure(text=f"Showing tracks with rating {rating}.")
        else:
            self.status_lbl.configure(text=f"Filter finished: 0 tracks with rating {rating}.")
            self.display_empty_state()


if __name__ == "__main__":
    root = tk.Tk()
    fonts.configure()
    TrackViewer(root)
    root.mainloop()