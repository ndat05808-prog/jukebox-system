import tkinter as tk
from tkinter import messagebox, ttk

from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import bind_two_column_stacking, clear_tree, setup_page_container, stars_text
from .validation import normalise_track_number


class UpdateLyrics:
    def __init__(self, window):
        self.window = window
        self.app_ref = None
        self.selected_key: str | None = None

        setup_page_container(
            window,
            title="Update Lyrics",
            geometry="1280x820",
            minsize=(1120, 720),
        )

        window.columnconfigure(0, weight=2, uniform="main_cols")
        window.columnconfigure(1, weight=1, uniform="main_cols")
        window.rowconfigure(2, weight=1)

        header = ttk.Frame(window, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(18, 8))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Update Lyrics", style="Hero.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Label(
            header,
            text="Select a track and edit its lyrics. Changes are saved into the library file.",
            style="Muted.TLabel",
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

        bind_two_column_stacking(self.window, left, right, breakpoint=900)

        search_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        search_card.grid(row=0, column=0, sticky="ew")
        search_card.columnconfigure(0, weight=1)

        self.search_input = ttk.Entry(search_card)
        self.search_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_input.bind("<KeyRelease>", lambda event: self._apply_search())
        self.search_input.bind("<Return>", lambda event: self._apply_search())

        ttk.Button(
            search_card,
            text="Tìm kiếm",
            style="Neon.TButton",
            command=self._apply_search,
        ).grid(row=0, column=1, sticky="ew", padx=(0, 6))

        ttk.Button(
            search_card,
            text="Clear",
            style="Ghost.TButton",
            command=self._clear_search,
        ).grid(row=0, column=2, sticky="ew")

        table_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        table_card.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        table_card.columnconfigure(0, weight=1)
        table_card.rowconfigure(1, weight=1)

        ttk.Label(table_card, text="Current Library", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )

        table_wrap = ttk.Frame(table_card, style="Card.TFrame")
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        columns = ("key", "title", "artist", "lyrics", "rating")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings")

        config = {
            "key": ("#", 60),
            "title": ("Song Title", 240),
            "artist": ("Artist", 170),
            "lyrics": ("Lyrics", 90),
            "rating": ("Rating", 110),
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

        editor_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        editor_card.grid(row=0, column=0, sticky="nsew")
        editor_card.columnconfigure(0, weight=1)
        editor_card.rowconfigure(2, weight=1)

        ttk.Label(editor_card, text="Lyrics Editor", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )

        self.current_lbl = ttk.Label(
            editor_card,
            text="No track loaded.",
            style="CardMuted.TLabel",
            wraplength=280,
            justify="left",
        )
        self.current_lbl.grid(row=1, column=0, sticky="w", pady=(0, 10))

        self.lyrics_txt = tk.Text(editor_card, height=16, width=1, wrap="word")
        fonts.style_text_widget(self.lyrics_txt)
        self.lyrics_txt.grid(row=2, column=0, sticky="nsew")

        button_row = ttk.Frame(editor_card, style="Card.TFrame")
        button_row.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)

        ttk.Button(
            button_row,
            text="Save Lyrics",
            style="Neon.TButton",
            command=self.save_lyrics_clicked,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            button_row,
            text="Clear Lyrics",
            style="Ghost.TButton",
            command=self.clear_lyrics_clicked,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def list_tracks_clicked(self):
        self._apply_search()

    def _apply_search(self):
        keyword = self.search_input.get().strip().lower() if hasattr(self, "search_input") else ""
        clear_tree(self.tree)
        for record in reversed(lib.get_track_records()):
            if keyword and not (
                keyword in record["key"].lower()
                or keyword in record["name"].lower()
                or keyword in record["artist"].lower()
                or keyword in (record["album"] or "").lower()
            ):
                continue
            item = lib.get_item(record["key"])
            has_lyrics = "Yes" if item is not None and item.lyrics else "—"
            self.tree.insert(
                "",
                "end",
                values=(
                    record["key"],
                    record["name"],
                    record["artist"],
                    has_lyrics,
                    stars_text(record["rating"]),
                ),
            )

    def _clear_search(self):
        self.search_input.delete(0, tk.END)
        self._apply_search()

    def _select_from_tree(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self._load_track(values[0])

    def _set_lyrics_text(self, text: str):
        self.lyrics_txt.delete("1.0", tk.END)
        if text:
            self.lyrics_txt.insert("1.0", text)

    def _notify_success(self, title: str, message: str):
        self.status_lbl.configure(text=message)
        messagebox.showinfo(title, message, parent=self.window)

    def _notify_error(self, title: str, message: str):
        self.status_lbl.configure(text=message)
        messagebox.showerror(title, message, parent=self.window)

    def _load_track(self, raw_key: str):
        track_key = normalise_track_number(raw_key)
        if track_key is None:
            self._notify_error("Cannot load lyrics", "Track number must contain digits only.")
            return

        item = lib.get_item(track_key)
        if item is None:
            self._notify_error("Cannot load lyrics", f"Track {track_key} was not found.")
            return

        self.selected_key = track_key
        self.current_lbl.configure(text=f"Track {track_key}: {item.name} — {item.artist}")
        self._set_lyrics_text(item.lyrics or "")
        self.status_lbl.configure(text=f"Loaded lyrics for track {track_key}.")

    def save_lyrics_clicked(self):
        if self.selected_key is None:
            self._notify_error("Cannot save lyrics", "Load a track before saving lyrics.")
            return

        lyrics = self.lyrics_txt.get("1.0", tk.END).strip()
        if not lib.set_lyrics(self.selected_key, lyrics if lyrics else None):
            self._notify_error("Save failed", "Lyrics could not be saved. The library file may not be writable.")
            return

        lib.add_history_entry(self.selected_key, source="manage", action="update_lyrics")

        self.list_tracks_clicked()
        item = lib.get_item(self.selected_key)
        track_label = f"{item.name} — {item.artist}" if item else self.selected_key
        self._notify_success("Lyrics saved", f"Lyrics saved for track {self.selected_key}: {track_label}.")

        if self.app_ref is not None:
            self.app_ref.refresh_library()

    def clear_lyrics_clicked(self):
        if self.selected_key is None:
            self._notify_error("Cannot clear lyrics", "Load a track before clearing lyrics.")
            return

        confirmed = messagebox.askyesno(
            "Clear Lyrics",
            f"Remove saved lyrics for track {self.selected_key}?",
            parent=self.window,
        )
        if not confirmed:
            self.status_lbl.configure(text="Clear lyrics cancelled.")
            return

        if not lib.set_lyrics(self.selected_key, None):
            self._notify_error("Clear failed", "Lyrics could not be cleared.")
            return

        lib.add_history_entry(self.selected_key, source="manage", action="clear_lyrics")

        self._set_lyrics_text("")
        self.list_tracks_clicked()
        self._notify_success("Lyrics cleared", f"Lyrics removed for track {self.selected_key}.")

        if self.app_ref is not None:
            self.app_ref.refresh_library()


if __name__ == "__main__":
    root = tk.Tk()
    fonts.configure()
    UpdateLyrics(root)
    root.mainloop()
