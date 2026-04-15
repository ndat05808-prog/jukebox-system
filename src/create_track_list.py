import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import clear_tree, stars_text
from .validation import get_valid_position, normalise_playlist_name, normalise_track_number

PROJECT_DIR = Path(__file__).resolve().parent
PLAYLIST_DIR = PROJECT_DIR / "playlists"
PLAYLIST_DIR.mkdir(exist_ok=True)


class CreateTrackList:
    def __init__(self, window):
        self.window = window
        self.playlist: list[str] = []
        self.current_index = None
        self.is_playing = False
        self.is_paused = False

        window.geometry("1360x820")
        window.minsize(1160, 740)
        window.title("Playlist Builder")
        fonts.apply_theme(window)

        window.columnconfigure(0, weight=3)
        window.columnconfigure(1, weight=2)
        window.rowconfigure(2, weight=1)

        ttk.Label(window, text="Playlist Builder", style="Hero.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 6))
        ttk.Label(window, text="Refined into a more visual workspace while keeping your save/load logic.", style="Muted.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(56, 12))

        toolbar = ttk.Frame(window, style="Root.TFrame")
        toolbar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=10)
        for i in range(12):
            toolbar.columnconfigure(i, weight=1)

        ttk.Button(toolbar, text="List Tracks", style="Ghost.TButton", command=self.list_tracks_clicked).grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.input_txt = ttk.Entry(toolbar)
        self.input_txt.grid(row=0, column=1, sticky="ew")
        self.input_txt.bind("<Return>", lambda event: self.add_track_clicked())
        ttk.Button(toolbar, text="Add Track", style="Neon.TButton", command=self.add_track_clicked).grid(row=0, column=2, padx=8, sticky="ew")

        self.remove_input = ttk.Entry(toolbar)
        self.remove_input.grid(row=0, column=3, sticky="ew")
        self.remove_input.bind("<Return>", lambda event: self.remove_track_clicked())
        ttk.Button(toolbar, text="Remove", style="Danger.TButton", command=self.remove_track_clicked).grid(row=0, column=4, padx=8, sticky="ew")

        self.move_input = ttk.Entry(toolbar)
        self.move_input.grid(row=0, column=5, sticky="ew")
        ttk.Button(toolbar, text="Move Up", style="Ghost.TButton", command=self.move_up_clicked).grid(row=0, column=6, padx=8, sticky="ew")
        ttk.Button(toolbar, text="Move Down", style="Ghost.TButton", command=self.move_down_clicked).grid(row=0, column=7, padx=(0, 8), sticky="ew")

        ttk.Button(toolbar, text="Play All", style="Neon.TButton", command=self.play_playlist_clicked).grid(row=0, column=8, sticky="ew")
        ttk.Button(toolbar, text="Load Current", style="Ghost.TButton", command=self.load_current_track_clicked).grid(row=0, column=9, padx=8, sticky="ew")
        ttk.Button(toolbar, text="Pause / Resume", style="Ghost.TButton", command=self.pause_resume_clicked).grid(row=0, column=10, sticky="ew")
        ttk.Button(toolbar, text="Skip", style="Ghost.TButton", command=self.skip_track_clicked).grid(row=0, column=11, padx=(8, 0), sticky="ew")

        left = ttk.Frame(window, style="Root.TFrame")
        left.grid(row=2, column=0, sticky="nsew", padx=(18, 10), pady=10)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        right = ttk.Frame(window, style="Root.TFrame")
        right.grid(row=2, column=1, sticky="nsew", padx=(10, 18), pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        library_card = ttk.Frame(left, style="Card.TFrame", padding=18)
        library_card.grid(row=0, column=0, sticky="nsew")
        library_card.columnconfigure(0, weight=1)
        library_card.rowconfigure(1, weight=1)
        ttk.Label(library_card, text="Library", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.library_tree = ttk.Treeview(library_card, columns=("key", "title", "artist", "album", "rating"), show="headings")
        config = {
            "key": ("#", 55),
            "title": ("Song Title", 240),
            "artist": ("Artist", 160),
            "album": ("Album", 180),
            "rating": ("Rating", 120),
        }
        for column, (label, width) in config.items():
            self.library_tree.heading(column, text=label)
            self.library_tree.column(column, width=width, anchor="w")
        self.library_tree.grid(row=1, column=0, sticky="nsew")
        self.library_tree.bind("<Double-1>", self._double_click_library)

        playlist_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        playlist_card.grid(row=0, column=0, sticky="nsew")
        playlist_card.columnconfigure(0, weight=1)
        playlist_card.rowconfigure(1, weight=1)
        ttk.Label(playlist_card, text="Current Playlist", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.playlist_tree = ttk.Treeview(playlist_card, columns=("position", "track", "title", "state"), show="headings")
        for column, label, width in (
            ("position", "Pos", 50),
            ("track", "Track", 60),
            ("title", "Song Title", 240),
            ("state", "State", 120),
        ):
            self.playlist_tree.heading(column, text=label)
            self.playlist_tree.column(column, width=width, anchor="w")
        self.playlist_tree.grid(row=1, column=0, sticky="nsew")
        self.playlist_tree.bind("<<TreeviewSelect>>", self._select_playlist_position)

        controls_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        controls_card.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        for i in range(5):
            controls_card.columnconfigure(i, weight=1)
        ttk.Label(controls_card, text="Playlist Files", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 10))
        self.playlist_name_input = ttk.Entry(controls_card)
        self.playlist_name_input.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 8))
        self.playlist_name_input.insert(0, "my_playlist")
        ttk.Button(controls_card, text="Save", style="Neon.TButton", command=self.save_playlist_clicked).grid(row=1, column=2, padx=8, sticky="ew")
        ttk.Button(controls_card, text="Load", style="Ghost.TButton", command=self.load_playlist_clicked).grid(row=1, column=3, padx=8, sticky="ew")
        ttk.Button(controls_card, text="List", style="Ghost.TButton", command=self.list_playlists_clicked).grid(row=1, column=4, sticky="ew")
        ttk.Button(controls_card, text="Rename", style="Ghost.TButton", command=self.rename_playlist_clicked).grid(row=2, column=0, pady=(10, 0), sticky="ew")
        ttk.Button(controls_card, text="Create New", style="Ghost.TButton", command=self.create_new_playlist_clicked).grid(row=2, column=1, pady=(10, 0), padx=(8, 8), sticky="ew")
        ttk.Button(controls_card, text="Reset", style="Danger.TButton", command=self.reset_playlist_clicked).grid(row=2, column=2, pady=(10, 0), sticky="ew")
        ttk.Button(controls_card, text="Delete File", style="Danger.TButton", command=self.delete_playlist_clicked).grid(row=2, column=3, columnspan=2, pady=(10, 0), padx=(8, 0), sticky="ew")

        self.status_lbl = ttk.Label(window, text="Ready.", style="Status.TLabel")
        self.status_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 16))

        self.list_tracks_clicked()
        self.refresh_playlist_tree()

    def _double_click_library(self, event=None):
        selected = self.library_tree.selection()
        if not selected:
            return
        values = self.library_tree.item(selected[0], "values")
        self.input_txt.delete(0, tk.END)
        self.input_txt.insert(0, values[0])
        self.add_track_clicked()

    def _select_playlist_position(self, event=None):
        selected = self.playlist_tree.selection()
        if not selected:
            return
        values = self.playlist_tree.item(selected[0], "values")
        self.remove_input.delete(0, tk.END)
        self.remove_input.insert(0, values[0])
        self.move_input.delete(0, tk.END)
        self.move_input.insert(0, values[0])

    def _reset_playback_state(self):
        self.current_index = None
        self.is_playing = False
        self.is_paused = False

    def _remove_missing_tracks(self, show_status=False):
        removed_keys = []
        valid_keys = []
        for track_key in self.playlist:
            if lib.get_name(track_key) is None:
                removed_keys.append(track_key)
            else:
                valid_keys.append(track_key)
        if removed_keys:
            self.playlist = valid_keys
            if len(self.playlist) == 0:
                self._reset_playback_state()
            elif self.current_index is not None and self.current_index >= len(self.playlist):
                self.current_index = len(self.playlist) - 1
            if show_status:
                self.status_lbl.configure(text=f"Removed {len(removed_keys)} missing track(s) from the playlist.")
        return removed_keys

    def _play_current_track(self, source="playlist_single"):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty. Add at least one track first.")
            return False
        if self.current_index is None or self.current_index < 0 or self.current_index >= len(self.playlist):
            self.current_index = 0
        track_key = self.playlist[self.current_index]
        track_name = lib.get_name(track_key) or "Unknown Track"
        if not lib.increment_play_count(track_key, auto_save=False):
            self.status_lbl.configure(text=f"Track {track_key} could not be played.")
            return False
        lib.add_history_entry(track_key, source=source)
        lib.save_library()
        self.is_playing = True
        self.is_paused = False
        self.refresh_playlist_tree()
        self.list_tracks_clicked()
        self.status_lbl.configure(text=f"Now playing: '{track_name}' (track {track_key}).")
        return True

    def list_tracks_clicked(self):
        clear_tree(self.library_tree)
        for record in lib.get_track_records():
            self.library_tree.insert("", "end", values=(record["key"], record["name"], record["artist"], record["album"] or "—", stars_text(record["rating"])))
        self.status_lbl.configure(text="Library tracks are displayed.")

    def refresh_playlist_tree(self):
        self._remove_missing_tracks(show_status=False)
        clear_tree(self.playlist_tree)
        if not self.playlist:
            self.status_lbl.configure(text="Playlist is empty.")
            return
        for number, track_key in enumerate(self.playlist, start=1):
            title = lib.get_name(track_key) or "[Missing Track]"
            state = "Ready"
            if self.current_index == number - 1:
                if self.is_playing:
                    state = "Playing"
                elif self.is_paused:
                    state = "Paused"
                else:
                    state = "Loaded"
            self.playlist_tree.insert("", "end", values=(number, track_key, title, state))

    def add_track_clicked(self):
        track_key = normalise_track_number(self.input_txt.get())
        if track_key is None:
            self.status_lbl.configure(text="Please enter digits only for the track number.")
            return
        track_name = lib.get_name(track_key)
        if track_name is None:
            self.status_lbl.configure(text=f"Track {track_key} does not exist.")
            return
        self.playlist.append(track_key)
        self.refresh_playlist_tree()
        self.input_txt.delete(0, tk.END)
        self.status_lbl.configure(text=f"Added '{track_name}' to the playlist.")

    def remove_track_clicked(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="There is nothing to remove because the playlist is empty.")
            return
        position = get_valid_position(self.remove_input.get(), len(self.playlist))
        if position is None:
            self.status_lbl.configure(text=f"Enter a valid position between 1 and {len(self.playlist)}.")
            return
        removed_index = position - 1
        removed_key = self.playlist.pop(removed_index)
        removed_name = lib.get_name(removed_key) or "Unknown Track"
        if len(self.playlist) == 0:
            self._reset_playback_state()
        elif self.current_index is not None:
            if removed_index < self.current_index:
                self.current_index -= 1
            elif removed_index == self.current_index:
                self.is_playing = False
                self.is_paused = False
                if self.current_index >= len(self.playlist):
                    self.current_index = len(self.playlist) - 1
        self.refresh_playlist_tree()
        self.remove_input.delete(0, tk.END)
        self.status_lbl.configure(text=f"Removed '{removed_name}' from position {position}.")

    def _get_move_position(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty, so there is nothing to move.")
            return None
        position = get_valid_position(self.move_input.get(), len(self.playlist))
        if position is None:
            self.status_lbl.configure(text=f"Enter a valid position between 1 and {len(self.playlist)}.")
            return None
        return position

    def move_up_clicked(self):
        position = self._get_move_position()
        if position is None:
            return
        if position == 1:
            self.status_lbl.configure(text="That track is already at the top of the playlist.")
            return
        index = position - 1
        self.playlist[index - 1], self.playlist[index] = self.playlist[index], self.playlist[index - 1]
        if self.current_index == index:
            self.current_index -= 1
        elif self.current_index == index - 1:
            self.current_index += 1
        self.refresh_playlist_tree()
        self.status_lbl.configure(text=f"Moved the track from position {position} to {position - 1}.")

    def move_down_clicked(self):
        position = self._get_move_position()
        if position is None:
            return
        if position == len(self.playlist):
            self.status_lbl.configure(text="That track is already at the bottom of the playlist.")
            return
        index = position - 1
        self.playlist[index], self.playlist[index + 1] = self.playlist[index + 1], self.playlist[index]
        if self.current_index == index:
            self.current_index += 1
        elif self.current_index == index + 1:
            self.current_index -= 1
        self.refresh_playlist_tree()
        self.status_lbl.configure(text=f"Moved the track from position {position} to {position + 1}.")

    def load_current_track_clicked(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty. Add at least one track first.")
            return
        if self.current_index is None or self.current_index < 0 or self.current_index >= len(self.playlist):
            self.current_index = 0
        track_key = self.playlist[self.current_index]
        track_name = lib.get_name(track_key) or "Unknown Track"
        self.is_playing = False
        self.is_paused = False
        self.refresh_playlist_tree()
        self.status_lbl.configure(text=f"Loaded track {track_key}: '{track_name}'.")

    def play_playlist_clicked(self):
        removed_keys = self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty. Add at least one track first.")
            return
        played_count = 0
        for track_key in self.playlist:
            if lib.increment_play_count(track_key, auto_save=False):
                lib.add_history_entry(track_key, source="playlist")
                played_count += 1
        lib.save_library()
        self.current_index = 0 if self.playlist else None
        self.is_playing = False
        self.is_paused = False
        self.list_tracks_clicked()
        self.refresh_playlist_tree()
        if removed_keys:
            self.status_lbl.configure(text=f"Played {played_count} valid track(s). Removed {len(removed_keys)} missing track(s).")
        else:
            self.status_lbl.configure(text=f"Playlist played successfully. Play count increased for {played_count} track(s).")

    def pause_resume_clicked(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty. Add at least one track first.")
            return
        if self.current_index is None or self.current_index < 0 or self.current_index >= len(self.playlist):
            self.status_lbl.configure(text="Load or play a track first.")
            return
        track_key = self.playlist[self.current_index]
        track_name = lib.get_name(track_key) or "Unknown Track"
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.refresh_playlist_tree()
            self.status_lbl.configure(text=f"Paused '{track_name}'.")
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.refresh_playlist_tree()
            self.status_lbl.configure(text=f"Resumed '{track_name}'.")
        else:
            self.status_lbl.configure(text="Track is loaded but not playing.")

    def skip_track_clicked(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty. Add at least one track first.")
            return
        if self.current_index is None or self.current_index < 0 or self.current_index >= len(self.playlist):
            self.current_index = 0
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self._play_current_track(source="playlist_skip")

    def reset_playlist_clicked(self):
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is already empty.")
            return
        confirmed = messagebox.askyesno("Reset Playlist", "Are you sure you want to clear the current playlist?", parent=self.window)
        if not confirmed:
            self.status_lbl.configure(text="Reset playlist cancelled.")
            return
        self.playlist.clear()
        self._reset_playback_state()
        clear_tree(self.playlist_tree)
        self.status_lbl.configure(text="Playlist reset complete.")

    def _get_playlist_path(self):
        playlist_name = normalise_playlist_name(self.playlist_name_input.get())
        if playlist_name is None:
            return None
        return PLAYLIST_DIR / f"{playlist_name}.txt"

    def create_new_playlist_clicked(self):
        new_name_text = simpledialog.askstring("Create New Playlist", "Enter the new playlist name:", parent=self.window)
        if new_name_text is None:
            self.status_lbl.configure(text="Create new playlist cancelled.")
            return
        new_name = normalise_playlist_name(new_name_text)
        if new_name is None:
            self.status_lbl.configure(text="Please enter a valid playlist name.")
            return
        new_path = PLAYLIST_DIR / f"{new_name}.txt"
        if new_path.exists():
            self.status_lbl.configure(text="A playlist with that name already exists.")
            return
        self.playlist.clear()
        self._reset_playback_state()
        clear_tree(self.playlist_tree)
        self.playlist_name_input.delete(0, tk.END)
        self.playlist_name_input.insert(0, new_name)
        try:
            new_path.write_text("", encoding="utf-8")
        except OSError:
            self.status_lbl.configure(text="Could not create the new playlist file.")
            return
        self.status_lbl.configure(text=f"Created new playlist '{new_name}'.")

    def save_playlist_clicked(self):
        self._remove_missing_tracks(show_status=False)
        if len(self.playlist) == 0:
            self.status_lbl.configure(text="Nothing to save because the playlist is empty.")
            return
        path = self._get_playlist_path()
        if path is None:
            self.status_lbl.configure(text="Please enter a valid playlist name.")
            return
        try:
            path.write_text("\n".join(self.playlist), encoding="utf-8")
        except OSError:
            self.status_lbl.configure(text="Could not save the playlist file.")
            return
        self.status_lbl.configure(text=f"Playlist saved to {path.stem}.")

    def load_playlist_clicked(self):
        path = self._get_playlist_path()
        if path is None:
            self.status_lbl.configure(text="Please enter a valid playlist name.")
            return
        if not path.exists():
            self.status_lbl.configure(text="That playlist does not exist yet.")
            return
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            self.status_lbl.configure(text="Could not load the playlist file.")
            return
        loaded_playlist = []
        skipped_count = 0
        for track_key in lines:
            if lib.get_name(track_key) is not None:
                loaded_playlist.append(track_key)
            else:
                skipped_count += 1
        self.playlist = loaded_playlist
        self._reset_playback_state()
        self.refresh_playlist_tree()
        if skipped_count > 0:
            self.status_lbl.configure(text=f"Loaded {len(self.playlist)} track(s) from {path.stem}. Skipped {skipped_count} missing track(s).")
        else:
            self.status_lbl.configure(text=f"Loaded {len(self.playlist)} track(s) from {path.stem}.")

    def rename_playlist_clicked(self):
        old_path = self._get_playlist_path()
        if old_path is None:
            self.status_lbl.configure(text="Please enter the current playlist name first.")
            return
        if not old_path.exists():
            self.status_lbl.configure(text="That playlist does not exist yet.")
            return
        new_name_text = simpledialog.askstring("Rename Playlist", "Enter the new playlist name:", parent=self.window)
        if new_name_text is None:
            self.status_lbl.configure(text="Rename cancelled.")
            return
        new_name = normalise_playlist_name(new_name_text)
        if new_name is None:
            self.status_lbl.configure(text="Please enter a valid new playlist name.")
            return
        new_path = PLAYLIST_DIR / f"{new_name}.txt"
        if old_path == new_path:
            self.status_lbl.configure(text="The new playlist name is the same as the current name.")
            return
        if new_path.exists():
            self.status_lbl.configure(text="A playlist with that name already exists.")
            return
        try:
            old_path.rename(new_path)
        except OSError:
            self.status_lbl.configure(text="Could not rename the playlist file.")
            return
        self.playlist_name_input.delete(0, tk.END)
        self.playlist_name_input.insert(0, new_name)
        self.status_lbl.configure(text=f"Renamed playlist to {new_name}.")

    def list_playlists_clicked(self):
        playlist_files = sorted(path.stem for path in PLAYLIST_DIR.glob("*.txt"))
        if len(playlist_files) == 0:
            self.status_lbl.configure(text="No saved playlists were found.")
            return
        messagebox.showinfo("Saved Playlists", "\n".join(playlist_files), parent=self.window)
        self.status_lbl.configure(text=f"Found {len(playlist_files)} saved playlist(s).")

    def delete_playlist_clicked(self):
        path = self._get_playlist_path()
        if path is None:
            self.status_lbl.configure(text="Please enter a valid playlist name.")
            return
        if not path.exists():
            self.status_lbl.configure(text="That playlist does not exist yet.")
            return
        confirmed = messagebox.askyesno("Delete Playlist", f"Are you sure you want to delete '{path.stem}'?", parent=self.window)
        if not confirmed:
            self.status_lbl.configure(text="Delete playlist cancelled.")
            return
        try:
            path.unlink()
        except OSError:
            self.status_lbl.configure(text="Could not delete the playlist file.")
            return
        self.status_lbl.configure(text=f"Deleted playlist file {path.stem}.")


if __name__ == "__main__":
    root = tk.Tk()
    fonts.configure()
    CreateTrackList(root)
    root.mainloop()