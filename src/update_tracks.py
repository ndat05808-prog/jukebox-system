import tkinter as tk
from tkinter import ttk

from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import clear_tree, set_text, stars_text
from .library_item import AlbumTrack
from .validation import get_valid_rating, get_valid_year, normalise_track_number


class UpdateTracks:
    def __init__(self, window):
        self.window = window
        window.geometry("1280x820")
        window.minsize(1120, 720)
        window.title("Update Tracks")
        fonts.apply_theme(window)

        # Cập nhật: Đổi tỷ lệ chia cột từ 3:2 thành 2:1 để cột trái rộng hơn hẳn
        window.columnconfigure(0, weight=2, uniform="main_cols")
        window.columnconfigure(1, weight=1, uniform="main_cols")
        window.rowconfigure(2, weight=1)

        # Header riêng để tiêu đề không chồng lên mô tả
        header = ttk.Frame(window, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(18, 8))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Update Track Information",
            style="Hero.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            header,
            text="Edit metadata while keeping the original coursework logic.",
            style="Muted.TLabel"
        ).grid(row=1, column=0, sticky="w")

        self._build_main_panels()

        self.status_lbl = ttk.Label(window, text="Ready.", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 16))

        self.list_tracks_clicked()

    def _build_main_panels(self):
        left = ttk.Frame(self.window, style="Root.TFrame")
        left.grid(row=2, column=0, sticky="nsew", padx=(18, 10), pady=10)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        right = ttk.Frame(self.window, style="Root.TFrame")
        right.grid(row=2, column=1, sticky="nsew", padx=(10, 18), pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        # ===== Load Track =====
        search_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        search_card.grid(row=0, column=0, sticky="ew")
        search_card.columnconfigure(1, weight=1)

        ttk.Label(
            search_card,
            text="Load Track",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        ttk.Label(search_card, text="Track Number", style="Card.TLabel").grid(row=1, column=0, sticky="w")

        self.track_input = ttk.Entry(search_card)
        self.track_input.grid(row=1, column=1, sticky="ew", padx=10)
        self.track_input.bind("<Return>", lambda event: self.load_track_clicked())

        ttk.Button(
            search_card,
            text="Load",
            style="Neon.TButton",
            command=self.load_track_clicked
        ).grid(row=1, column=2, sticky="ew")

        # ===== Library Table =====
        table_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        table_card.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)

        ttk.Label(
            table_card,
            text="Current Library",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        table_wrap = ttk.Frame(table_card, style="Card.TFrame")
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        columns = ("key", "title", "artist", "album", "rating")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings")

        config = {
            "key": ("#", 60),
            "title": ("Song Title", 250),
            "artist": ("Artist", 180),
            "album": ("Album", 180),
            "rating": ("Rating", 130),
        }

        for column, (label, width) in config.items():
            self.tree.heading(column, text=label)
            self.tree.column(column, width=width, anchor="w", stretch=True)

        tree_y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        tree_x_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_y_scroll.set, xscrollcommand=tree_x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_y_scroll.grid(row=0, column=1, sticky="ns")
        tree_x_scroll.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self._select_from_tree)

        # ===== Edit Form =====
        form_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        form_card.grid(row=0, column=0, sticky="ew")
        form_card.columnconfigure(0, weight=1)
        form_card.columnconfigure(1, weight=1)

        ttk.Label(
            form_card,
            text="Edit Form",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        ttk.Label(form_card, text="Name", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 10))
        ttk.Label(form_card, text="Artist", style="Card.TLabel").grid(row=1, column=1, sticky="w")

        self.name_input = ttk.Entry(form_card)
        self.name_input.grid(row=2, column=0, sticky="ew", padx=(0, 10), pady=(6, 12))

        self.artist_input = ttk.Entry(form_card)
        self.artist_input.grid(row=2, column=1, sticky="ew", pady=(6, 12))

        ttk.Label(form_card, text="Album", style="Card.TLabel").grid(row=3, column=0, sticky="w", padx=(0, 10))
        ttk.Label(form_card, text="Year", style="Card.TLabel").grid(row=3, column=1, sticky="w")

        self.album_input = ttk.Entry(form_card)
        self.album_input.grid(row=4, column=0, sticky="ew", padx=(0, 10), pady=(6, 12))

        self.year_input = ttk.Entry(form_card)
        self.year_input.grid(row=4, column=1, sticky="ew", pady=(6, 12))

        ttk.Label(form_card, text="Rating", style="Card.TLabel").grid(row=5, column=0, sticky="w", padx=(0, 10))

        self.rating_input = ttk.Combobox(
            form_card,
            values=["0", "1", "2", "3", "4", "5"],
            state="readonly"
        )
        self.rating_input.grid(row=6, column=0, sticky="ew", padx=(0, 10), pady=(6, 12))
        self.rating_input.set("0")

        ttk.Button(
            form_card,
            text="Update Track",
            style="Neon.TButton",
            command=self.update_track_clicked
        ).grid(row=6, column=1, sticky="ew", pady=(6, 12))

        # ===== Preview =====
        preview_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        preview_card.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        preview_card.columnconfigure(0, weight=1)
        preview_card.rowconfigure(1, weight=1)

        ttk.Label(
            preview_card,
            text="Track Preview",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Đã giới hạn chiều rộng bằng width=1
        self.track_txt = tk.Text(preview_card, height=24, width=1, wrap="word")
        fonts.style_text_widget(self.track_txt)
        self.track_txt.grid(row=1, column=0, sticky="nsew")

        set_text(self.track_txt, "Select a track from the table or enter a track number to edit it.")

    def list_tracks_clicked(self):
        clear_tree(self.tree)
        for record in lib.get_track_records():
            self.tree.insert(
                "",
                "end",
                values=(
                    record["key"],
                    record["name"],
                    record["artist"],
                    record["album"] or "—",
                    stars_text(record["rating"])
                ),
            )
        self.status_lbl.configure(text="Library tracks are displayed.")

    def _select_from_tree(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.track_input.delete(0, tk.END)
        self.track_input.insert(0, values[0])
        self.load_track_clicked()

    def _clear_form_only(self):
        for widget in (self.name_input, self.artist_input, self.album_input, self.year_input):
            widget.delete(0, tk.END)
        self.rating_input.set("0")

    def load_track_clicked(self):
        track_key = normalise_track_number(self.track_input.get())
        if track_key is None:
            set_text(self.track_txt, "Track number must contain digits only.")
            self.status_lbl.configure(text="Please enter digits only for the track number.")
            return

        item = lib.get_item(track_key)
        if item is None:
            self._clear_form_only()
            set_text(self.track_txt, f"Track {track_key} was not found.")
            self.status_lbl.configure(text="That track number does not exist.")
            return

        self._clear_form_only()

        self.track_input.delete(0, tk.END)
        self.track_input.insert(0, track_key)

        self.name_input.insert(0, item.name)
        self.artist_input.insert(0, item.artist)
        self.rating_input.set(str(item.rating))

        if isinstance(item, AlbumTrack):
            self.album_input.insert(0, item.album)
            if item.year is not None:
                self.year_input.insert(0, str(item.year))

        set_text(self.track_txt, lib.get_details(track_key) or "")
        self.status_lbl.configure(text=f"Track {track_key} loaded successfully.")

    def update_track_clicked(self):
        track_key = normalise_track_number(self.track_input.get())
        if track_key is None:
            set_text(self.track_txt, "Track number must contain digits only.")
            self.status_lbl.configure(text="Please enter digits only for the track number.")
            return

        if lib.get_name(track_key) is None:
            set_text(self.track_txt, f"Track {track_key} was not found.")
            self.status_lbl.configure(text="That track number does not exist.")
            return

        name = self.name_input.get().strip()
        artist = self.artist_input.get().strip()

        if name == "" or artist == "":
            set_text(self.track_txt, "Name and artist cannot be empty.")
            self.status_lbl.configure(text="Please enter both name and artist.")
            return

        rating = get_valid_rating(self.rating_input.get(), allow_zero=True)
        if rating is None:
            set_text(self.track_txt, "Rating must be a whole number from 0 to 5.")
            self.status_lbl.configure(text="Please enter a rating between 0 and 5.")
            return

        year_text = self.year_input.get().strip()
        year = get_valid_year(year_text)
        if year_text != "" and year is None:
            set_text(self.track_txt, "Year must be between 1900 and 2100, or left blank.")
            self.status_lbl.configure(text="Year must be between 1900 and 2100, or left blank.")
            return

        album = self.album_input.get().strip()

        success = lib.update_track_info(track_key, name, artist, rating, album=album, year=year)
        if not success:
            set_text(self.track_txt, "The track could not be updated.")
            self.status_lbl.configure(text="Update failed. The file may not have been saved.")
            return

        set_text(self.track_txt, lib.get_details(track_key) or "")
        self.list_tracks_clicked()
        self.status_lbl.configure(text=f"Track {track_key} was updated successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    fonts.configure()
    UpdateTracks(root)
    root.mainloop()