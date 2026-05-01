import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ..models import audio_manager as audio
from ..models import cover_manager as cover
from . import font_manager as fonts
from ..models import track_library as lib
from .gui_helpers import bind_two_column_stacking, clear_tree, create_scrollable_column, setup_page_container, stars_text
from ..models.library_item import AlbumTrack
from ..models.validation import get_valid_rating, get_valid_year, normalise_track_number

COVER_FILETYPES = [
    ("Image files", "*.png *.gif *.ppm *.pgm"),
    ("PNG", "*.png"),
    ("GIF", "*.gif"),
    ("All files", "*.*"),
]

AUDIO_FILETYPES = [
    ("Audio files", "*.mp3 *.wav *.ogg *.flac *.m4a *.aac"),
    ("MP3", "*.mp3"),
    ("WAV", "*.wav"),
    ("All files", "*.*"),
]


class UpdateTracks:
    def __init__(self, window):
        self.window = window
        self.app_ref = None
        setup_page_container(
            window,
            title="Update Tracks",
            geometry="1280x820",
            minsize=(1120, 720),
        )

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
        right.rowconfigure(0, weight=1)

        bind_two_column_stacking(self.window, left, right, breakpoint=940)

        form_host = ttk.Frame(right, style="Root.TFrame")
        form_host.grid(row=0, column=0, sticky="nsew")
        form_scroll = create_scrollable_column(form_host)
        form_scroll.columnconfigure(0, weight=1)

        # ===== Load Track =====
        search_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        search_card.grid(row=0, column=0, sticky="ew")
        search_card.columnconfigure(1, weight=1)

        ttk.Label(
            search_card,
            text="Search Track",
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
        form_card = ttk.Frame(form_scroll, style="Card.TFrame", padding=18)
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

        ttk.Label(form_card, text="Cover Image", style="Card.TLabel").grid(row=7, column=0, columnspan=2, sticky="w", pady=(4, 6))

        cover_row = ttk.Frame(form_card, style="Card.TFrame")
        cover_row.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        cover_row.columnconfigure(1, weight=1)

        self.cover_preview = tk.Label(
            cover_row,
            bg=fonts.INPUT_BG,
            width=10,
            height=5,
        )
        self.cover_preview.grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 12))

        self.cover_name_lbl = ttk.Label(cover_row, text="No cover assigned.", style="Muted.TLabel")
        self.cover_name_lbl.grid(row=0, column=1, sticky="w")

        cover_btns = ttk.Frame(cover_row, style="Card.TFrame")
        cover_btns.grid(row=1, column=1, sticky="ew", pady=(6, 0))
        cover_btns.columnconfigure(0, weight=1)
        cover_btns.columnconfigure(1, weight=1)

        ttk.Button(cover_btns, text="Choose Image…", style="Ghost.TButton", command=self._choose_cover_clicked).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(cover_btns, text="Remove Cover", style="Ghost.TButton", command=self._clear_cover_clicked).grid(row=0, column=1, sticky="ew")

        ttk.Label(form_card, text="Audio File", style="Card.TLabel").grid(row=9, column=0, columnspan=2, sticky="w", pady=(4, 6))

        audio_row = ttk.Frame(form_card, style="Card.TFrame")
        audio_row.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        audio_row.columnconfigure(0, weight=1)

        self.audio_name_lbl = ttk.Label(audio_row, text="No audio assigned.", style="Muted.TLabel")
        self.audio_name_lbl.grid(row=0, column=0, sticky="w")

        audio_btns = ttk.Frame(audio_row, style="Card.TFrame")
        audio_btns.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        audio_btns.columnconfigure(0, weight=1)
        audio_btns.columnconfigure(1, weight=1)

        ttk.Button(audio_btns, text="Choose Audio…", style="Ghost.TButton", command=self._choose_audio_clicked).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(audio_btns, text="Remove Audio", style="Ghost.TButton", command=self._clear_audio_clicked).grid(row=0, column=1, sticky="ew")

        self.selected_cover_path: Path | None = None
        self.clear_cover_on_save = False
        self.selected_audio_path: Path | None = None
        self.clear_audio_on_save = False
        self._preview_image = None

        ttk.Button(
            form_card,
            text="Update Track",
            style="Neon.TButton",
            command=self.update_track_clicked
        ).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(6, 0))


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
        self.selected_cover_path = None
        self.clear_cover_on_save = False
        self._render_cover_preview(None, "No cover assigned.")
        self.selected_audio_path = None
        self.clear_audio_on_save = False
        self._render_audio_name(None, "No audio assigned.")

    def _render_cover_preview(self, path: Path | None, empty_text: str = "No image selected."):
        if path is None:
            self._preview_image = None
            self.cover_preview.configure(image="", width=10, height=5)
            self.cover_name_lbl.configure(text=empty_text)
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
        self.clear_cover_on_save = False
        self._render_cover_preview(path)
        self.status_lbl.configure(text=f"Selected cover: {path.name} (will save on update).")

    def _validation_error(self, message: str):
        self.status_lbl.configure(text=message)
        messagebox.showwarning("Cannot update track", message, parent=self.window)

    def _notify_success(self, title: str, message: str):
        self.status_lbl.configure(text=message)
        messagebox.showinfo(title, message, parent=self.window)

    def _notify_error(self, title: str, message: str):
        self.status_lbl.configure(text=message)
        messagebox.showerror(title, message, parent=self.window)

    def _clear_cover_clicked(self):
        self.selected_cover_path = None
        self.clear_cover_on_save = True
        self._render_cover_preview(None, "Cover will be removed on update.")
        self.status_lbl.configure(text="Cover will be removed when you update the track.")

    def _render_audio_name(self, path: Path | None, empty_text: str = "No audio assigned."):
        if path is None:
            self.audio_name_lbl.configure(text=empty_text)
        else:
            self.audio_name_lbl.configure(text=path.name)

    def _choose_audio_clicked(self):
        initial = str(audio.AUDIO_DIR) if audio.AUDIO_DIR.exists() else str(Path.home())
        selected = filedialog.askopenfilename(
            parent=self.window,
            title="Choose audio file",
            initialdir=initial,
            filetypes=AUDIO_FILETYPES,
        )
        if not selected:
            return
        path = Path(selected)
        if path.suffix.lower() not in audio.SUPPORTED_EXTENSIONS:
            self.status_lbl.configure(text="Unsupported audio format (use MP3, WAV, OGG, FLAC, M4A, or AAC).")
            return
        self.selected_audio_path = path
        self.clear_audio_on_save = False
        self._render_audio_name(path)
        self.status_lbl.configure(text=f"Selected audio: {path.name} (will save on update).")

    def _clear_audio_clicked(self):
        self.selected_audio_path = None
        self.clear_audio_on_save = True
        self._render_audio_name(None, "Audio will be removed on update.")
        self.status_lbl.configure(text="Audio will be removed when you update the track.")

    def load_track_clicked(self):
        track_key = normalise_track_number(self.track_input.get())
        if track_key is None:
            self.status_lbl.configure(text="Track number must contain digits only.")
            return

        item = lib.get_item(track_key)
        if item is None:
            self._clear_form_only()
            self.status_lbl.configure(text=f"Track {track_key} was not found.")
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

        existing_cover = cover.find_cover_path(track_key) if cover.has_custom_cover(track_key) else None
        if existing_cover is not None:
            self._render_cover_preview(existing_cover)
            self.cover_name_lbl.configure(text=f"Current: {existing_cover.name}")
        else:
            self._render_cover_preview(None, "No cover assigned.")

        existing_audio = audio.find_audio_path(track_key) if audio.has_audio(track_key) else None
        if existing_audio is not None:
            self.audio_name_lbl.configure(text=f"Current: {existing_audio.name}")
        else:
            self._render_audio_name(None, "No audio assigned.")

        self.status_lbl.configure(text=f"Track {track_key} loaded successfully.")

    def update_track_clicked(self):
        track_key = normalise_track_number(self.track_input.get())
        if track_key is None:
            self._validation_error("Track number must contain digits only.")
            return

        if lib.get_name(track_key) is None:
            self._validation_error(f"Track {track_key} was not found.")
            return

        name = self.name_input.get().strip()
        artist = self.artist_input.get().strip()

        if name == "" or artist == "":
            self._validation_error("Please enter both name and artist.")
            return

        rating = get_valid_rating(self.rating_input.get(), allow_zero=True)
        if rating is None:
            self._validation_error("Rating must be a whole number from 0 to 5.")
            return

        year_text = self.year_input.get().strip()
        year = get_valid_year(year_text)
        if year_text != "" and year is None:
            self._validation_error("Year must be a four-digit number between 1900 and 2100, or left blank.")
            return

        album = self.album_input.get().strip()

        success = lib.update_track_info(track_key, name, artist, rating, album=album, year=year)
        if not success:
            self._notify_error("Update failed", "Track could not be updated. The library file may not have been saved.")
            return

        lib.add_history_entry(track_key, source="manage", action="update")

        cover_status = ""
        if self.selected_cover_path is not None:
            saved = cover.assign_cover_image(track_key, self.selected_cover_path)
            cover_status = " Cover saved." if saved is not None else " (Cover could not be saved.)"
            self.selected_cover_path = None
        elif self.clear_cover_on_save:
            cover.remove_cover_image(track_key)
            self.clear_cover_on_save = False
            cover_status = " Cover removed."

        audio_status = ""
        if self.selected_audio_path is not None:
            saved_audio = audio.assign_audio(track_key, self.selected_audio_path)
            audio_status = " Audio saved." if saved_audio is not None else " (Audio could not be saved.)"
            self.selected_audio_path = None
        elif self.clear_audio_on_save:
            audio.remove_audio(track_key)
            self.clear_audio_on_save = False
            audio_status = " Audio removed."

        existing_cover = cover.find_cover_path(track_key) if cover.has_custom_cover(track_key) else None
        if existing_cover is not None:
            self._render_cover_preview(existing_cover)
            self.cover_name_lbl.configure(text=f"Current: {existing_cover.name}")
        else:
            self._render_cover_preview(None, "No cover assigned.")

        existing_audio = audio.find_audio_path(track_key) if audio.has_audio(track_key) else None
        if existing_audio is not None:
            self.audio_name_lbl.configure(text=f"Current: {existing_audio.name}")
        else:
            self._render_audio_name(None, "No audio assigned.")

        self.list_tracks_clicked()

        play_count = lib.get_play_count(track_key)

        self._notify_success(
            "Track updated",
            f"Track {track_key}: '{name}' by {artist} was updated successfully. "
            f"New rating: {rating}/5. Play count: {play_count}."
            f"{cover_status}{audio_status}",
        )

        if self.app_ref is not None:
            self.app_ref.refresh_library()


if __name__ == "__main__":
    root = tk.Tk()
    fonts.configure()
    UpdateTracks(root)
    root.mainloop()