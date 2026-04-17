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

        window.columnconfigure(0, weight=3)
        window.columnconfigure(1, weight=2)
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
        left.rowconfigure(1, weight=1)

        right = ttk.Frame(self.window, style="Root.TFrame")
        right.grid(row=2, column=1, sticky="nsew", padx=(10, 18), pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        # ===== Add form =====
        form_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        form_card.grid(row=0, column=0, sticky="ew")
        for col in range(4):
            form_card.columnconfigure(col, weight=1)

        ttk.Label(
            form_card,
            text="Add New Track",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        ttk.Label(form_card, text="Name", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
        self.name_input = ttk.Entry(form_card)
        self.name_input.grid(row=2, column=0, sticky="ew", padx=(0, 10), pady=(0, 10))

        ttk.Label(form_card, text="Artist", style="Card.TLabel").grid(row=1, column=1, sticky="w", padx=(0, 10), pady=6)
        self.artist_input = ttk.Entry(form_card)
        self.artist_input.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))

        ttk.Label(form_card, text="Rating", style="Card.TLabel").grid(row=1, column=2, sticky="w", padx=(0, 10), pady=6)
        self.rating_input = ttk.Combobox(form_card, values=["0", "1", "2", "3", "4", "5"], state="readonly")
        self.rating_input.grid(row=2, column=2, sticky="ew", padx=(0, 10), pady=(0, 10))
        self.rating_input.set("0")

        ttk.Label(form_card, text="Year", style="Card.TLabel").grid(row=1, column=3, sticky="w", pady=6)
        self.year_input = ttk.Entry(form_card)
        self.year_input.grid(row=2, column=3, sticky="ew", pady=(0, 10))

        ttk.Label(form_card, text="Album", style="Card.TLabel").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=6)
        self.album_input = ttk.Entry(form_card)
        self.album_input.grid(row=4, column=0, columnspan=3, sticky="ew", padx=(0, 10), pady=(0, 10))

        ttk.Button(
            form_card,
            text="Add Track",
            style="Neon.TButton",
            command=self.add_track_clicked
        ).grid(row=4, column=3, sticky="ew", pady=(0, 10))

        # ===== Current Library =====
        table_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        table_card.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)

        header = ttk.Frame(table_card, style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="Current Library",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            header,
            text="Refresh",
            style="Ghost.TButton",
            command=self.refresh_list
        ).grid(row=0, column=1, sticky="e")

        table_wrap = ttk.Frame(table_card, style="Card.TFrame")
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        columns = ("key", "name", "artist", "album", "year", "rating")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings")

        headings = {
            "key": ("#", 60),
            "name": ("Song Title", 250),
            "artist": ("Artist", 180),
            "album": ("Album", 180),
            "year": ("Year", 80),
            "rating": ("Rating", 130),
        }

        for column, (label, width) in headings.items():
            self.tree.heading(column, text=label)
            self.tree.column(column, width=width, anchor="w", stretch=True)

        tree_y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        tree_x_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_y_scroll.set, xscrollcommand=tree_x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_y_scroll.grid(row=0, column=1, sticky="ns")
        tree_x_scroll.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self._tree_selected)

        # ===== Delete + Preview =====
        right_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        right_card.grid(row=0, column=0, sticky="nsew")
        right_card.columnconfigure(0, weight=1)
        right_card.rowconfigure(5, weight=1)

        ttk.Label(
            right_card,
            text="Delete Track",
            style="CardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            right_card,
            text="Select a row or enter a track number manually.",
            style="CardMuted.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=(4, 12))

        ttk.Label(right_card, text="Track Number", style="Card.TLabel").grid(row=2, column=0, sticky="w")
        self.remove_input = ttk.Entry(right_card)
        self.remove_input.grid(row=3, column=0, sticky="ew", pady=(6, 12))

        ttk.Button(
            right_card,
            text="Delete Track",
            style="Danger.TButton",
            command=self.remove_track_clicked
        ).grid(row=4, column=0, sticky="ew")

        self.preview = tk.Text(right_card, height=18, wrap="word")
        fonts.style_text_widget(self.preview)
        self.preview.grid(row=5, column=0, sticky="nsew", pady=(16, 0))
        self.preview.configure(state="disabled")

    def _set_preview(self, content: str):
        self.preview.configure(state="normal")
        self.preview.delete("1.0", tk.END)
        self.preview.insert("1.0", content)
        self.preview.configure(state="disabled")

    def _tree_selected(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0], "values")
        track_key = item[0]

        self.remove_input.delete(0, tk.END)
        self.remove_input.insert(0, track_key)

        details = lib.get_details(track_key) or "Track not found."
        self._set_preview(details)

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
                    record["year"] or "—",
                    stars_text(record["rating"]),
                ),
            )

        self._set_preview("Select a track to see its full details here.")
        self.status_lbl.configure(text="Library list refreshed.")

    def add_track_clicked(self):
        name = self.name_input.get().strip()
        artist = self.artist_input.get().strip()
        rating_text = self.rating_input.get().strip()
        album = self.album_input.get().strip()
        year_text = self.year_input.get().strip()

        if name == "" or artist == "":
            self.status_lbl.configure(text="Name and artist cannot be empty.")
            return

        rating = get_valid_rating(rating_text, allow_zero=True)
        if rating is None:
            self.status_lbl.configure(text="Rating must be a whole number from 0 to 5.")
            return

        year = get_valid_year(year_text)
        if year_text != "" and year is None:
            self.status_lbl.configure(text="Year must be between 1900 and 2100, or left blank.")
            return

        key = lib.add_track(name, artist, rating, album=album, year=year)
        if key is None:
            self.status_lbl.configure(text="Track could not be saved.")
            return

        self.refresh_list()
        self._set_preview(lib.get_details(key) or "Track saved.")
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
        self._set_preview("Track deleted successfully.")
        self.status_lbl.configure(text=f"Deleted track {track_key}: '{track_name}'.")


if __name__ == "__main__":
    root = tk.Tk()
    fonts.configure()
    AddRemoveTracks(root)
    root.mainloop()