import tkinter as tk
from tkinter import ttk

from . import cover_manager
from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import clear_tree, stars_text
from .library_item import AlbumTrack
from .validation import get_valid_rating, normalise_track_number


class TrackViewer:
    def __init__(self, window):
        self.window = window
        self.cover_image = None

        window.geometry("1360x820")
        window.minsize(1180, 720)
        window.title("View Tracks")
        fonts.apply_theme(window)

        window.columnconfigure(0, weight=3)
        window.columnconfigure(1, weight=2)
        window.rowconfigure(2, weight=1)

        ttk.Label(window, text="Library Browser", style="Hero.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 6))
        ttk.Label(window, text="This replaces the old text-heavy viewer with a cleaner dashboard-style layout.", style="Muted.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(56, 12))

        topbar = ttk.Frame(window, style="Root.TFrame")
        topbar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=10)
        for i in range(7):
            topbar.columnconfigure(i, weight=1)

        self.search_txt = ttk.Entry(topbar)
        self.search_txt.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.search_txt.bind("<Return>", lambda event: self.search_tracks_clicked())
        ttk.Button(topbar, text="Search", style="Neon.TButton", command=self.search_tracks_clicked).grid(row=0, column=2, padx=8, sticky="ew")

        self.rating_filter_txt = ttk.Combobox(topbar, values=["0", "1", "2", "3", "4", "5"], state="readonly")
        self.rating_filter_txt.grid(row=0, column=3, sticky="ew")
        self.rating_filter_txt.set("5")
        ttk.Button(topbar, text="Filter Rating", style="Ghost.TButton", command=self.filter_by_score_clicked).grid(row=0, column=4, padx=8, sticky="ew")

        self.input_txt = ttk.Entry(topbar)
        self.input_txt.grid(row=0, column=5, sticky="ew")
        self.input_txt.bind("<Return>", lambda event: self.view_track_clicked())
        ttk.Button(topbar, text="View Details", style="Ghost.TButton", command=self.view_track_clicked).grid(row=0, column=6, padx=(8, 0), sticky="ew")

        left = ttk.Frame(window, style="Root.TFrame")
        left.grid(row=2, column=0, sticky="nsew", padx=(18, 10), pady=10)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        right = ttk.Frame(window, style="Root.TFrame")
        right.grid(row=2, column=1, sticky="nsew", padx=(10, 18), pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        table_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        table_card.grid(row=0, column=0, sticky="nsew")
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)
        header = ttk.Frame(table_card, style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Library", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Button(header, text="Show All", style="Ghost.TButton", command=self.list_tracks_clicked).grid(row=0, column=1, sticky="e")

        columns = ("key", "title", "artist", "album", "year", "plays", "rating")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings")
        headers = {
            "key": ("#", 60),
            "title": ("Song Title", 250),
            "artist": ("Artist", 180),
            "album": ("Album", 180),
            "year": ("Year", 80),
            "plays": ("Plays", 80),
            "rating": ("Rating", 140),
        }
        for column, (label, width) in headers.items():
            self.tree.heading(column, text=label)
            self.tree.column(column, width=width, anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._select_track_from_tree)

        detail_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        detail_card.grid(row=0, column=0, sticky="nsew")
        detail_card.columnconfigure(0, weight=1)
        detail_card.rowconfigure(2, weight=1)
        ttk.Label(detail_card, text="Selected Track", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        self.cover_canvas = tk.Canvas(detail_card, height=240)
        fonts.style_canvas(self.cover_canvas)
        self.cover_canvas.grid(row=1, column=0, sticky="ew", pady=(12, 12))

        meta_frame = ttk.Frame(detail_card, style="Card.TFrame")
        meta_frame.grid(row=2, column=0, sticky="nsew")
        meta_frame.columnconfigure(0, weight=1)
        self.title_lbl = ttk.Label(meta_frame, text="No track selected", style="CardTitle.TLabel")
        self.title_lbl.grid(row=0, column=0, sticky="w")
        self.artist_lbl = ttk.Label(meta_frame, text="", style="CardMuted.TLabel")
        self.artist_lbl.grid(row=1, column=0, sticky="w", pady=(4, 12))
        self.meta_lbl = ttk.Label(meta_frame, text="", style="CardMuted.TLabel", justify="left")
        self.meta_lbl.grid(row=2, column=0, sticky="w")

        self.detail_text = tk.Text(detail_card, height=12, wrap="word")
        fonts.style_text_widget(self.detail_text)
        self.detail_text.grid(row=3, column=0, sticky="nsew", pady=(12, 0))

        self.status_lbl = ttk.Label(window, text="Ready.", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 16))

        self.list_tracks_clicked()
        self.display_cover_placeholder()

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
                    record["play_count"],
                    stars_text(record["rating"]),
                ),
            )

    def _select_track_from_tree(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.input_txt.delete(0, tk.END)
        self.input_txt.insert(0, values[0])
        self.show_track(values[0])

    def display_cover_placeholder(self, title="No Track Selected", subtitle="Select a track from the table to preview it."):
        self.cover_image = None
        self.cover_canvas.delete("all")
        self.cover_canvas.create_rectangle(18, 18, 282, 222, outline=fonts.BORDER, width=2, fill=fonts.CARD_ALT)
        self.cover_canvas.create_text(150, 92, text=title, fill=fonts.TEXT, font=("Segoe UI", 14, "bold"), width=220)
        self.cover_canvas.create_text(150, 140, text=subtitle, fill=fonts.MUTED, font=("Segoe UI", 10), width=220)
        self.title_lbl.configure(text=title)
        self.artist_lbl.configure(text="")
        self.meta_lbl.configure(text="")
        self._set_detail_text("Choose a track number or click a row to see details.")

    def _set_detail_text(self, text: str):
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert("1.0", text)
        self.detail_text.configure(state="disabled")

    def display_track_cover(self, track_key: str):
        track_name = lib.get_name(track_key) or "Unknown Track"
        artist_name = lib.get_artist(track_key) or "Unknown Artist"
        self.cover_canvas.delete("all")
        self.cover_image = cover_manager.load_cover_image(track_key, max_size=210)
        if self.cover_image is not None:
            self.cover_canvas.create_image(150, 120, image=self.cover_image)
            return
        self.cover_canvas.create_rectangle(18, 18, 282, 222, outline=fonts.ACCENT, width=2, fill=fonts.CARD_ALT)
        self.cover_canvas.create_text(150, 88, text=track_name, fill=fonts.TEXT, font=("Segoe UI", 14, "bold"), width=220)
        self.cover_canvas.create_text(150, 126, text=artist_name, fill=fonts.ACCENT, font=("Segoe UI", 11), width=220)
        self.cover_canvas.create_text(150, 172, text=f"No cover image found for {track_key}.\nUse {track_key}.png or default.png", fill=fonts.MUTED, font=("Segoe UI", 10), width=220)

    def show_track(self, track_key: str):
        track_key = normalise_track_number(track_key)
        if track_key is None:
            self.display_cover_placeholder("Invalid Input", "Track number must contain digits only.")
            self.status_lbl.configure(text="Track number must contain digits only.")
            return
        item = lib.get_item(track_key)
        if item is None:
            self.display_cover_placeholder("Track Not Found", f"No track exists with number {track_key}.")
            self.status_lbl.configure(text="That track number does not exist.")
            return
        self.display_track_cover(track_key)
        album = item.album if isinstance(item, AlbumTrack) else "—"
        year = item.year if isinstance(item, AlbumTrack) and item.year is not None else "—"
        self.title_lbl.configure(text=item.name)
        self.artist_lbl.configure(text=item.artist)
        self.meta_lbl.configure(text=f"Album: {album}\nYear: {year}\nPlays: {item.play_count}\nRating: {item.stars()}")
        self._set_detail_text(lib.get_details(track_key) or "")
        self.status_lbl.configure(text=f"Showing details for track {track_key}.")

    def view_track_clicked(self):
        self.show_track(self.input_txt.get())

    def list_tracks_clicked(self):
        self._populate_tree(lib.get_track_records())
        self.status_lbl.configure(text="All tracks are now displayed.")

    def search_tracks_clicked(self):
        keyword = self.search_txt.get().strip().lower()
        records = [record for record in lib.get_track_records() if keyword == "" or keyword in record["name"].lower() or keyword in record["artist"].lower() or keyword in (record["album"] or "").lower()]
        self._populate_tree(records)
        if records:
            self.status_lbl.configure(text=f"Showing search results for '{self.search_txt.get().strip() or 'all tracks'}'.")
        else:
            self.status_lbl.configure(text="Search finished: 0 matches.")
            self.display_cover_placeholder("No Results", "No matching tracks were found.")

    def filter_by_score_clicked(self):
        rating = get_valid_rating(self.rating_filter_txt.get(), allow_zero=True)
        if rating is None:
            self.status_lbl.configure(text="Filter score must be between 0 and 5.")
            return
        records = [record for record in lib.get_track_records() if record["rating"] == rating]
        self._populate_tree(records)
        if records:
            self.status_lbl.configure(text=f"Showing tracks with rating {rating}.")
        else:
            self.status_lbl.configure(text=f"Filter finished: 0 tracks with rating {rating}.")
            self.display_cover_placeholder("No Results", f"No tracks were found with rating {rating}.")


if __name__ == "__main__":
    root = tk.Tk()
    fonts.configure()
    TrackViewer(root)
    root.mainloop()