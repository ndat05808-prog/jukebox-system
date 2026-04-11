import tkinter as tk
import tkinter.scrolledtext as tkst
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from . import font_manager as fonts
from . import track_library as lib
from .gui_helpers import set_text
from .validation import (
    get_valid_position,
    normalise_playlist_name,
    normalise_track_number,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
PLAYLIST_DIR = PROJECT_DIR / "playlists"
PLAYLIST_DIR.mkdir(exist_ok=True)


class CreateTrackList:
    def __init__(self, window):
        self.window = window
        self.playlist = []
        self.current_index = None
        self.is_playing = False
        self.is_paused = False

        window.geometry("1160x700")
        window.title("Playlist Builder")
        fonts.apply_theme(window)
        window.columnconfigure(0, weight=1)
        window.columnconfigure(1, weight=1)
        window.rowconfigure(4, weight=1)

        title_lbl = ttk.Label(window, text="Playlist Builder", style="Title.TLabel")
        title_lbl.grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 6))

        add_frame = ttk.LabelFrame(window, text="Add Tracks", style="Section.TLabelframe")
        add_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        list_tracks_btn = ttk.Button(add_frame, text="List All Tracks", command=self.list_tracks_clicked)
        list_tracks_btn.grid(row=0, column=0, padx=8, pady=8)

        enter_lbl = ttk.Label(add_frame, text="Track Number")
        enter_lbl.grid(row=0, column=1, padx=8, pady=8)

        self.input_txt = ttk.Entry(add_frame, width=8)
        self.input_txt.grid(row=0, column=2, padx=8, pady=8)
        self.input_txt.bind("<Return>", lambda event: self.add_track_clicked())

        add_track_btn = ttk.Button(add_frame, text="Add Track", command=self.add_track_clicked)
        add_track_btn.grid(row=0, column=3, padx=8, pady=8)

        remove_lbl = ttk.Label(add_frame, text="Remove Position")
        remove_lbl.grid(row=0, column=4, padx=8, pady=8)

        self.remove_input = ttk.Entry(add_frame, width=8)
        self.remove_input.grid(row=0, column=5, padx=8, pady=8)
        self.remove_input.bind("<Return>", lambda event: self.remove_track_clicked())

        remove_btn = ttk.Button(add_frame, text="Remove Track", command=self.remove_track_clicked,
                                style="Danger.TButton")
        remove_btn.grid(row=0, column=6, padx=8, pady=8)

        move_frame = ttk.LabelFrame(window, text="Reorder Playlist / Playback", style="Section.TLabelframe")
        move_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        move_lbl = ttk.Label(move_frame, text="Position")
        move_lbl.grid(row=0, column=0, padx=8, pady=8)

        self.move_input = ttk.Entry(move_frame, width=8)
        self.move_input.grid(row=0, column=1, padx=8, pady=8)

        move_up_btn = ttk.Button(move_frame, text="Move Up", command=self.move_up_clicked)
        move_up_btn.grid(row=0, column=2, padx=8, pady=8)

        move_down_btn = ttk.Button(move_frame, text="Move Down", command=self.move_down_clicked)
        move_down_btn.grid(row=0, column=3, padx=8, pady=8)

        play_btn = ttk.Button(move_frame, text="Play Playlist", command=self.play_playlist_clicked)
        play_btn.grid(row=0, column=4, padx=8, pady=8)

        reset_btn = ttk.Button(move_frame, text="Reset Playlist", command=self.reset_playlist_clicked, style="Danger.TButton")
        reset_btn.grid(row=0, column=5, padx=8, pady=8)

        load_current_btn = ttk.Button(move_frame, text="Load Current Track", command=self.load_current_track_clicked)
        load_current_btn.grid(row=1, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="ew")

        pause_resume_btn = ttk.Button(move_frame, text="Pause / Resume", command=self.pause_resume_clicked)
        pause_resume_btn.grid(row=1, column=2, columnspan=2, padx=8, pady=(0, 8), sticky="ew")

        skip_btn = ttk.Button(move_frame, text="Skip Track", command=self.skip_track_clicked)
        skip_btn.grid(row=1, column=4, columnspan=2, padx=8, pady=(0, 8), sticky="ew")

        save_frame = ttk.LabelFrame(window, text="Save / Load Playlists", style="Section.TLabelframe")
        save_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        playlist_name_lbl = ttk.Label(save_frame, text="Playlist Name")
        playlist_name_lbl.grid(row=0, column=0, padx=8, pady=8)

        self.playlist_name_input = ttk.Entry(save_frame, width=24)
        self.playlist_name_input.grid(row=0, column=1, padx=8, pady=8)
        self.playlist_name_input.insert(0, "my_playlist")

        save_btn = ttk.Button(save_frame, text="Save Playlist", command=self.save_playlist_clicked)
        save_btn.grid(row=0, column=2, padx=8, pady=8)

        load_btn = ttk.Button(save_frame, text="Load Playlist", command=self.load_playlist_clicked)
        load_btn.grid(row=0, column=3, padx=8, pady=8)

        list_playlists_btn = ttk.Button(save_frame, text="List Playlists", command=self.list_playlists_clicked)
        list_playlists_btn.grid(row=0, column=4, padx=8, pady=8)

        delete_playlist_btn = ttk.Button(save_frame, text="Delete Playlist", command=self.delete_playlist_clicked, style="Danger.TButton")
        delete_playlist_btn.grid(row=0, column=5, padx=8, pady=8)

        rename_playlist_btn = ttk.Button(
            save_frame,
            text="Rename Playlist",
            command=self.rename_playlist_clicked,
        )
        rename_playlist_btn.grid(row=1, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="w")

        create_playlist_btn = ttk.Button(
            save_frame,
            text="Create New Playlist",
            command=self.create_new_playlist_clicked,
        )
        create_playlist_btn.grid(row=1, column=2, columnspan=2, padx=8, pady=(0, 8), sticky="w")

        library_frame = ttk.LabelFrame(window, text="Library", style="Section.TLabelframe")
        library_frame.grid(row=4, column=0, sticky="nsew", padx=(12, 6), pady=8)
        library_frame.columnconfigure(0, weight=1)
        library_frame.rowconfigure(0, weight=1)

        playlist_frame = ttk.LabelFrame(window, text="Current Playlist", style="Section.TLabelframe")
        playlist_frame.grid(row=4, column=1, sticky="nsew", padx=(6, 12), pady=8)
        playlist_frame.columnconfigure(0, weight=1)
        playlist_frame.rowconfigure(0, weight=1)

        self.library_txt = tkst.ScrolledText(library_frame, width=50, height=20, wrap="none")
        self.library_txt.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.playlist_txt = tkst.ScrolledText(playlist_frame, width=50, height=20, wrap="none")
        self.playlist_txt.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.status_lbl = ttk.Label(window, text="", style="Status.TLabel")
        self.status_lbl.grid(row=5, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 10))

        self.list_tracks_clicked()
        self.refresh_playlist_text()

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
                self.status_lbl.configure(
                    text=f"Removed {len(removed_keys)} missing track(s) from the playlist."
                )

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

        try:
            lib.add_history_entry(track_key, source=source)
            lib.save_library()
        except OSError:
            self.status_lbl.configure(text="Track played in memory, but saving to file failed.")
            return False

        self.is_playing = True
        self.is_paused = False
        self.refresh_playlist_text()
        self.status_lbl.configure(text=f"Now playing: '{track_name}' (track {track_key}).")
        return True

    def list_tracks_clicked(self):
        set_text(self.library_txt, lib.list_all())
        self.status_lbl.configure(text="Library tracks are displayed.")

    def refresh_playlist_text(self):
        self._remove_missing_tracks(show_status=False)

        if len(self.playlist) == 0:
            set_text(self.playlist_txt, "No tracks in current playlist.")
            return

        output_lines = []
        for number, track_key in enumerate(self.playlist, start=1):
            track_name = lib.get_name(track_key) or "[Missing Track]"

            marker = "  "
            if self.current_index == number - 1:
                if self.is_playing:
                    marker = ">>"
                elif self.is_paused:
                    marker = "||"
                else:
                    marker = "[]"

            output_lines.append(f"{marker} {number}. {track_key} {track_name}")

        set_text(self.playlist_txt, "\n".join(output_lines))

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
        self.refresh_playlist_text()
        self.status_lbl.configure(text=f"Added '{track_name}' to the playlist.")
        self.input_txt.delete(0, tk.END)

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

        self.refresh_playlist_text()
        self.status_lbl.configure(text=f"Removed '{removed_name}' from position {position}.")
        self.remove_input.delete(0, tk.END)

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

        self.refresh_playlist_text()
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

        self.refresh_playlist_text()
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
        self.refresh_playlist_text()
        self.status_lbl.configure(text=f"Loaded track {track_key}: '{track_name}'. Click Play Playlist to simulate full playlist play.")

    def play_playlist_clicked(self):
        removed_keys = self._remove_missing_tracks(show_status=False)

        if len(self.playlist) == 0:
            self.status_lbl.configure(text="The playlist is empty. Add at least one track first.")
            return

        played_count = 0

        try:
            for track_key in self.playlist:
                if lib.increment_play_count(track_key, auto_save=False):
                    lib.add_history_entry(track_key, source="playlist")
                    played_count += 1

            lib.save_library()
        except OSError:
            self.status_lbl.configure(text="Playlist play count updated in memory, but saving failed.")
            return

        self.current_index = 0 if self.playlist else None
        self.is_playing = False
        self.is_paused = False
        self.refresh_playlist_text()

        if removed_keys:
            self.status_lbl.configure(
                text=f"Played {played_count} valid track(s). Removed {len(removed_keys)} missing track(s)."
            )
        else:
            self.status_lbl.configure(
                text=f"Playlist played successfully. Play count increased for {played_count} track(s)."
            )

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
            self.refresh_playlist_text()
            self.status_lbl.configure(text=f"Paused '{track_name}'.")
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.refresh_playlist_text()
            self.status_lbl.configure(text=f"Resumed '{track_name}'.")
        else:
            self.status_lbl.configure(text="Track is loaded but not playing. Use Skip or Load Current Track.")

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

        confirmed = messagebox.askyesno(
            "Reset Playlist",
            "Are you sure you want to clear the current playlist?",
            parent=self.window,
        )
        if not confirmed:
            self.status_lbl.configure(text="Reset playlist cancelled.")
            return

        self.playlist.clear()
        self._reset_playback_state()
        self.refresh_playlist_text()
        self.status_lbl.configure(text="Playlist reset complete.")

    def _get_playlist_path(self):
        playlist_name = normalise_playlist_name(self.playlist_name_input.get())
        if playlist_name is None:
            return None
        return PLAYLIST_DIR / f"{playlist_name}.txt"

    def create_new_playlist_clicked(self):
        new_name_text = simpledialog.askstring(
            "Create New Playlist",
            "Enter the new playlist name:",
            parent=self.window,
        )
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
        self.refresh_playlist_text()
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
        self.refresh_playlist_text()

        if skipped_count > 0:
            self.status_lbl.configure(
                text=f"Loaded {len(self.playlist)} track(s) from {path.stem}. Skipped {skipped_count} missing track(s)."
            )
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

        new_name_text = simpledialog.askstring(
            "Rename Playlist",
            "Enter the new playlist name:",
            parent=self.window,
        )
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

        confirmed = messagebox.askyesno(
            "Delete Playlist",
            f"Are you sure you want to delete '{path.stem}'?",
            parent=self.window,
        )
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
    window = tk.Tk()
    fonts.configure()
    CreateTrackList(window)
    window.mainloop()