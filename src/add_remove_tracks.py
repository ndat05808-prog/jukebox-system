import tkinter as tk
from tkinter import messagebox, ttk

from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import clear_tree, stars_text
from .validation import get_valid_rating, get_valid_year, normalise_track_number


class AddRemoveTracks:
    def __init__(self, window):
        self.window = window
        window.geometry("1280x820")
        window.minsize(1120, 720)
        window.title("Add / Remove Tracks")
        fonts.apply_theme(window)

        # Cập nhật: Đổi tỷ lệ chia cột thành 2:1 và thêm uniform="main_cols"
        window.columnconfigure(0, weight=2, uniform="main_cols")
        window.columnconfigure(1, weight=1, uniform="main_cols")
        window.rowconfigure(2, weight=1)

        # Header riêng để tiêu đề không đè lên mô tả
        header = ttk.Frame(window, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(18, 8))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Add / Remove Tracks",
            style="Hero.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            header,
            text="Manage your library with a cleaner dark dashboard.",
            style="Muted.TLabel"
        ).grid(row=1, column=0, sticky="w")

        self._build_main_panels()

        self.status_lbl = ttk.Label(window, text="Ready.", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 16))

        self.refresh_list()

    def _build_main_panels(self):
        left = ttk.Frame(self.window, style="Root.TFrame")
        left.grid(row=2, column=0, sticky="nsew", padx=(18, 10), pady=10)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        right = ttk.Frame(self.window, style="Root.TFrame")
        right.grid(row=2, column=1, sticky="nsew", padx=(10, 18), pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        # ===== Library Table =====
        table_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        table_card.grid(row=0, column=0, sticky="nsew")
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

        # ===== Forms Column =====
        forms_container = ttk.Frame(right, style="Root.TFrame")
        forms_container.grid(row=0, column=0, sticky="nsew")
        forms_container.columnconfigure(0, weight=1)

        # 1. Add Track
        add_card = ttk.Frame(forms_container, style="Card.TFrame", padding=18)
        add_card.grid(row=0, column=0, sticky="ew")
        add_card.columnconfigure(0, weight=1)
        add_card.columnconfigure(1, weight=1)

        ttk.Label(add_card, text="Add New Track", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        ttk.Label(add_card, text="Name", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 10))
        ttk.Label(add_card, text="Artist", style="Card.TLabel").grid(row=1, column=1, sticky="w")

        self.name_input = ttk.Entry(add_card)
        self.name_input.grid(row=2, column=0, sticky="ew", padx=(0, 10), pady=(6, 12))

        self.artist_input = ttk.Entry(add_card)
        self.artist_input.grid(row=2, column=1, sticky="ew", pady=(6, 12))

        ttk.Label(add_card, text="Album", style="Card.TLabel").grid(row=3, column=0, sticky="w", padx=(0, 10))
        ttk.Label(add_card, text="Year", style="Card.TLabel").grid(row=3, column=1, sticky="w")

        self.album_input = ttk.Entry(add_card)
        self.album_input.grid(row=4, column=0, sticky="ew", padx=(0, 10), pady=(6, 12))

        self.year_input = ttk.Entry(add_card)
        self.year_input.grid(row=4, column=1, sticky="ew", pady=(6, 12))

        ttk.Label(add_card, text="Rating", style="Card.TLabel").grid(row=5, column=0, sticky="w", padx=(0, 10))

        self.rating_input = ttk.Combobox(
            add_card,
            values=["0", "1", "2", "3", "4", "5"],
            state="readonly"
        )
        self.rating_input.grid(row=6, column=0, sticky="ew", padx=(0, 10), pady=(6, 12))
        self.rating_input.set("0")

        ttk.Button(
            add_card,
            text="Add Track",
            style="Neon.TButton",
            command=self.add_track_clicked
        ).grid(row=6, column=1, sticky="ew", pady=(6, 12))

        # 2. Delete Track
        delete_card = ttk.Frame(forms_container, style="Card.TFrame", padding=18)
        delete_card.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        delete_card.columnconfigure(1, weight=1)

        ttk.Label(delete_card, text="Delete Track", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))
        ttk.Label(delete_card, text="Track #", style="Card.TLabel").grid(row=1, column=0, sticky="w")

        self.remove_input = ttk.Entry(delete_card, width=10)
        self.remove_input.grid(row=1, column=1, sticky="ew", padx=10)
        self.remove_input.bind("<Return>", lambda event: self.remove_track_clicked())

        ttk.Button(
            delete_card,
            text="Delete",
            style="Danger.TButton",
            command=self.remove_track_clicked
        ).grid(row=1, column=2, sticky="ew")

        # 3. Latest Action
        action_card = ttk.Frame(forms_container, style="Card.TFrame", padding=18)
        action_card.grid(row=2, column=0, sticky="nsew", pady=(14, 0))
        action_card.columnconfigure(0, weight=1)
        action_card.rowconfigure(1, weight=1)
        forms_container.rowconfigure(2, weight=1)

        ttk.Label(action_card, text="Latest Action", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Cập nhật: Thêm width=1 vào text widget
        self.preview_txt = tk.Text(action_card, height=12, width=1, wrap="word")
        fonts.style_text_widget(self.preview_txt)
        self.preview_txt.grid(row=1, column=0, sticky="nsew")

        self._set_preview("Fill out the form to add a track, or select one to delete.")

    def _set_preview(self, text: str):
        self.preview_txt.configure(state="normal")
        self.preview_txt.delete("1.0", tk.END)
        self.preview_txt.insert("1.0", text)
        self.preview_txt.configure(state="disabled")

    def refresh_list(self):
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

    def _select_from_tree(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.remove_input.delete(0, tk.END)
        self.remove_input.insert(0, values[0])

    def add_track_clicked(self):
        name = self.name_input.get().strip()
        artist = self.artist_input.get().strip()

        if name == "" or artist == "":
            self._set_preview("Please provide both a name and an artist.")
            self.status_lbl.configure(text="Missing required fields.")
            return

        rating = get_valid_rating(self.rating_input.get(), allow_zero=True)
        if rating is None:
            self._set_preview("Rating must be a whole number between 0 and 5.")
            self.status_lbl.configure(text="Invalid rating value.")
            return

        year_text = self.year_input.get().strip()
        year = get_valid_year(year_text)
        if year_text != "" and year is None:
            self._set_preview("Year must be a four-digit number between 1900 and 2100.")
            self.status_lbl.configure(text="Invalid year value.")
            return

        album = self.album_input.get().strip()

        key = lib.add_track(name, artist, rating, album=album, year=year)
        if not key:
            self._set_preview("Failed to add track. The library file may not be writable.")
            self.status_lbl.configure(text="Track could not be saved.")
            return

        self.refresh_list()
        self._set_preview(f"Success!\n\nAdded track {key}:\n{name} by {artist}\nRating: {rating}/5")
        self.status_lbl.configure(text=f"Added track {key}: '{name}' by {artist}.")

        for widget in (self.name_input, self.artist_input, self.album_input, self.year_input):
            widget.delete(0, tk.END)
        self.rating_input.set("0")

    def remove_track_clicked(self):
        track_key = normalise_track_number(self.remove_input.get())
        if track_key is None:
            self.status_lbl.configure(text="Please enter a valid track number.")
            return

        track_name = lib.get_name(track_key)
        if track_name is None:
            self.status_lbl.configure(text=f"Track {track_key} does not exist.")
            return

        confirmed = messagebox.askyesno(
            "Delete Track",
            f"Are you sure you want to delete track {track_key}: '{track_name}'?",
            parent=self.window
        )
        if not confirmed:
            self.status_lbl.configure(text="Delete track cancelled.")
            return

        if not lib.delete_track(track_key):
            self.status_lbl.configure(text="Track could not be deleted.")
            return

        self.refresh_list()
        self.remove_input.delete(0, tk.END)
        self._set_preview(f"Track {track_key} ('{track_name}') has been removed from the library.")
        self.status_lbl.configure(text=f"Track {track_key} deleted successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    fonts.configure()
    AddRemoveTracks(root)
    root.mainloop()