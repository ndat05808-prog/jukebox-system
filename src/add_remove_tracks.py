import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from . import cover_manager as cover
from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import bind_two_column_stacking, clear_tree, setup_page_container, stars_text
from .validation import get_valid_rating, get_valid_year, normalise_track_number

COVER_FILETYPES = [
    ("Image files", "*.png *.gif *.ppm *.pgm"),
    ("PNG", "*.png"),
    ("GIF", "*.gif"),
    ("All files", "*.*"),
]


class AddRemoveTracks:
    def __init__(self, window, mode: str = "both"):
        if mode not in ("add", "remove", "both"):
            mode = "both"
        self.mode = mode
        self.window = window
        self.app_ref = None

        titles = {
            "add": ("Create Track", "Add a new track to your library with optional cover art."),
            "remove": ("Delete Track", "Remove a track (and its cover) from your library."),
            "both": ("Add / Remove Tracks", "Manage your library with a cleaner dark dashboard."),
        }
        hero_title, hero_subtitle = titles[mode]

        setup_page_container(
            window,
            title=hero_title,
            geometry="1280x820",
            minsize=(1120, 720),
        )

        window.columnconfigure(0, weight=2, uniform="main_cols")
        window.columnconfigure(1, weight=1, uniform="main_cols")
        window.rowconfigure(2, weight=1)

        # Header riêng để tiêu đề không đè lên mô tả
        header = ttk.Frame(window, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(18, 8))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text=hero_title,
            style="Hero.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            header,
            text=hero_subtitle,
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

        bind_two_column_stacking(self.window, left, right, breakpoint=900)

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

        self.selected_cover_path: Path | None = None
        self._preview_image = None

        next_row = 0
        if self.mode in ("add", "both"):
            self._build_add_card(forms_container, next_row)
            next_row += 1
        if self.mode in ("remove", "both"):
            self._build_delete_card(forms_container, next_row)
            next_row += 1
            self._build_delete_details_card(forms_container, next_row)
            next_row += 1

    def _build_add_card(self, parent, row: int):
        add_card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        add_card.grid(row=row, column=0, sticky="ew", pady=(0, 0) if row == 0 else (14, 0))
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

        ttk.Label(add_card, text="Cover Image", style="Card.TLabel").grid(row=7, column=0, columnspan=2, sticky="w", pady=(4, 6))

        cover_row = ttk.Frame(add_card, style="Card.TFrame")
        cover_row.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        cover_row.columnconfigure(1, weight=1)

        self.cover_preview = tk.Label(
            cover_row,
            bg=fonts.INPUT_BG,
            width=10,
            height=5,
        )
        self.cover_preview.grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 12))

        self.cover_name_lbl = ttk.Label(cover_row, text="No image selected.", style="Muted.TLabel")
        self.cover_name_lbl.grid(row=0, column=1, sticky="w")

        cover_btns = ttk.Frame(cover_row, style="Card.TFrame")
        cover_btns.grid(row=1, column=1, sticky="ew", pady=(6, 0))
        cover_btns.columnconfigure(0, weight=1)
        cover_btns.columnconfigure(1, weight=1)

        ttk.Button(cover_btns, text="Choose Image…", style="Ghost.TButton", command=self._choose_cover_clicked).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(cover_btns, text="Clear", style="Ghost.TButton", command=self._clear_cover_clicked).grid(row=0, column=1, sticky="ew")

        ttk.Button(
            add_card,
            text="Add Track",
            style="Neon.TButton",
            command=self.add_track_clicked
        ).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(6, 0))

    def _build_delete_card(self, parent, row: int):
        delete_card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        delete_card.grid(row=row, column=0, sticky="ew", pady=(0, 0) if row == 0 else (14, 0))
        delete_card.columnconfigure(1, weight=1)

        ttk.Label(delete_card, text="Delete Track", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))
        ttk.Label(delete_card, text="Track #", style="Card.TLabel").grid(row=1, column=0, sticky="w")

        self.remove_input = ttk.Entry(delete_card, width=10)
        self.remove_input.grid(row=1, column=1, sticky="ew", padx=10)
        self.remove_input.bind("<Return>", lambda event: self.remove_track_clicked())
        self.remove_input.bind("<KeyRelease>", self._refresh_delete_details)

        ttk.Button(
            delete_card,
            text="Delete",
            style="Danger.TButton",
            command=self.remove_track_clicked
        ).grid(row=1, column=2, sticky="ew")

    def _validation_error(self, message: str):
        self.status_lbl.configure(text=message)
        messagebox.showwarning("Cannot save track", message, parent=self.window)

    def _notify_success(self, title: str, message: str):
        self.status_lbl.configure(text=message)
        messagebox.showinfo(title, message, parent=self.window)

    def _notify_error(self, title: str, message: str):
        self.status_lbl.configure(text=message)
        messagebox.showerror(title, message, parent=self.window)

    def _build_delete_details_card(self, parent, row: int):
        details_card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        details_card.grid(row=row, column=0, sticky="ew", pady=(14, 0))
        details_card.columnconfigure(0, weight=1)

        ttk.Label(details_card, text="Track Details", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.delete_details_txt = tk.Text(details_card, height=10, width=1, wrap="word")
        fonts.style_text_widget(self.delete_details_txt)
        self.delete_details_txt.grid(row=1, column=0, sticky="ew")

        self._show_delete_details(None, "Enter or select a track number to preview its details.")

    def _show_delete_details(self, track_key: str | None, fallback: str = ""):
        if not hasattr(self, "delete_details_txt"):
            return
        if track_key is None:
            text = fallback
        else:
            details = lib.get_details(track_key)
            text = details if details else f"Track {track_key} was not found."
        self.delete_details_txt.configure(state="normal")
        self.delete_details_txt.delete("1.0", tk.END)
        self.delete_details_txt.insert("1.0", text)
        self.delete_details_txt.configure(state="disabled")

    def _render_cover_preview(self, path: Path | None):
        if path is None:
            self._preview_image = None
            self.cover_preview.configure(image="", width=10, height=5)
            self.cover_name_lbl.configure(text="No image selected.")
            return
        try:
            image = tk.PhotoImage(file=str(path))
        except tk.TclError:
            self._preview_image = None
            self.cover_preview.configure(image="", width=10, height=5)
            self.cover_name_lbl.configure(text=f"Unsupported image: {path.name}")
            return
        largest = max(image.width(), image.height())
        if largest > 80:
            factor = max(1, (largest + 79) // 80)
            image = image.subsample(factor, factor)
        self._preview_image = image
        self.cover_preview.configure(image=image, width=image.width(), height=image.height())
        self.cover_name_lbl.configure(text=path.name)

    def _choose_cover_clicked(self):
        initial = str(cover.COVERS_DIR) if cover.COVERS_DIR.exists() else str(Path.home())
        selected = filedialog.askopenfilename(
            parent=self.window,
            title="Choose cover image",
            initialdir=initial,
            filetypes=COVER_FILETYPES,
        )
        if not selected:
            return
        path = Path(selected)
        if path.suffix.lower() not in cover.SUPPORTED_EXTENSIONS:
            self.status_lbl.configure(text="Unsupported image format (use PNG, GIF, PPM, or PGM).")
            return
        self.selected_cover_path = path
        self._render_cover_preview(path)
        self.status_lbl.configure(text=f"Selected cover: {path.name}")

    def _clear_cover_clicked(self):
        self.selected_cover_path = None
        self._render_cover_preview(None)
        self.status_lbl.configure(text="Cover selection cleared.")

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
        if hasattr(self, "remove_input"):
            self.remove_input.delete(0, tk.END)
            self.remove_input.insert(0, values[0])
            self._refresh_delete_details()

    def _refresh_delete_details(self, event=None):
        if not hasattr(self, "remove_input"):
            return
        key = normalise_track_number(self.remove_input.get())
        if key is None:
            self._show_delete_details(None, "Enter or select a track number to preview its details.")
            return
        self._show_delete_details(key)

    def add_track_clicked(self):
        name = self.name_input.get().strip()
        artist = self.artist_input.get().strip()

        if name == "" or artist == "":
            self._validation_error("Please enter both a name and an artist.")
            return

        rating = get_valid_rating(self.rating_input.get(), allow_zero=True)
        if rating is None:
            self._validation_error("Rating must be a whole number between 0 and 5.")
            return

        year_text = self.year_input.get().strip()
        year = get_valid_year(year_text)
        if year_text != "" and year is None:
            self._validation_error("Year must be a four-digit number between 1900 and 2100, or left blank.")
            return

        album = self.album_input.get().strip()

        key = lib.add_track(name, artist, rating, album=album, year=year)
        if not key:
            self._notify_error("Create failed", "Track could not be saved — the library file may not be writable.")
            return

        lib.add_history_entry(key, source="manage", action="create")

        cover_note = ""
        if self.selected_cover_path is not None:
            saved = cover.assign_cover_image(key, self.selected_cover_path)
            cover_note = f" Cover saved ({saved.name})." if saved is not None else " (Cover could not be saved.)"

        self.refresh_list()
        self._notify_success(
            "Track created",
            f"Added track {key}: '{name}' by {artist}.{cover_note}",
        )

        for widget in (self.name_input, self.artist_input, self.album_input, self.year_input):
            widget.delete(0, tk.END)
        self.rating_input.set("0")
        self.selected_cover_path = None
        self._render_cover_preview(None)

        if self.app_ref is not None:
            self.app_ref.refresh_library()

    def remove_track_clicked(self):
        track_key = normalise_track_number(self.remove_input.get())
        if track_key is None:
            self._notify_error("Cannot delete track", "Please enter a valid track number.")
            return

        track_item = lib.get_item(track_key)
        if track_item is None:
            self._notify_error("Cannot delete track", f"Track {track_key} does not exist.")
            return

        track_name = track_item.name
        track_artist = track_item.artist

        confirmed = messagebox.askyesno(
            "Delete Track",
            f"Are you sure you want to delete track {track_key}: '{track_name}'?",
            parent=self.window
        )
        if not confirmed:
            self.status_lbl.configure(text="Delete track cancelled.")
            return

        if not lib.delete_track(track_key):
            self._notify_error("Delete failed", f"Track {track_key} could not be deleted.")
            return

        lib.add_history_entry(track_key, source="manage", action="delete", name=track_name, artist=track_artist)

        self.refresh_list()
        self.remove_input.delete(0, tk.END)
        self._show_delete_details(None, "")
        self._notify_success(
            "Track deleted",
            f"Track {track_key}: '{track_name}' by {track_artist} deleted successfully.",
        )

        if self.app_ref is not None:
            self.app_ref.refresh_library()


if __name__ == "__main__":
    root = tk.Tk()
    fonts.configure()
    AddRemoveTracks(root)
    root.mainloop()